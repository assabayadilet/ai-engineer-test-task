from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph
from langchain_core.messages import AIMessage, HumanMessage

from .mock_llm import MockLLM
from .mcp_client import MCPClient
from .tools import calculator, format_products, formatter


class AgentState(TypedDict, total=False):
    query: str
    decision: Dict[str, Any]
    tool_result: Any
    tools_used: List[str]
    response: str
    error: str


logger = logging.getLogger(__name__)


class AgentRunner:
    def __init__(self, app) -> None:
        self._app = app

    async def run(self, query: str) -> dict:
        state = await self._app.ainvoke({"query": query})
        return {
            "response": state.get("response", ""),
            "tools_used": state.get("tools_used", []),
        }


def build_agent(mcp_client: Optional[MCPClient] = None, llm: Optional[MockLLM] = None) -> AgentRunner:
    llm = llm or MockLLM()
    mcp_client = mcp_client or MCPClient()

    async def analyze(state: AgentState) -> AgentState:
        message = HumanMessage(content=state["query"])
        llm_response = llm.invoke([message])
        decision: Dict[str, Any] = {"action": "unknown"}
        if isinstance(llm_response, AIMessage):
            try:
                decision = json.loads(llm_response.content)
            except json.JSONDecodeError:
                decision = {"action": "unknown"}
        elif isinstance(llm_response, dict):
            decision = llm_response
        logger.info("Agent decision: %s", decision)
        return {"decision": decision}

    async def execute(state: AgentState) -> AgentState:
        decision = state.get("decision", {})
        action = decision.get("action", "unknown")
        tools_used: list[str] = []

        try:
            logger.info("Executing action: %s", action)
            if action == "list_products":
                tools_used.append("list_products")
                products = await mcp_client.call_tool("list_products", {})
                category = decision.get("category")
                if category:
                    products = [p for p in products if p.get("category") == category]
                return {"tool_result": products, "tools_used": tools_used}

            if action == "get_statistics":
                tools_used.append("get_statistics")
                stats = await mcp_client.call_tool("get_statistics", {})
                return {"tool_result": stats, "tools_used": tools_used}

            if action == "add_product":
                tools_used.append("add_product")
                payload = {
                    "name": decision.get("name"),
                    "price": decision.get("price"),
                    "category": decision.get("category"),
                    "in_stock": decision.get("in_stock", True),
                }
                created = await mcp_client.call_tool("add_product", payload)
                return {"tool_result": created, "tools_used": tools_used}

            if action == "get_product":
                tools_used.append("get_product")
                product = await mcp_client.call_tool("get_product", {"product_id": decision.get("product_id")})
                return {"tool_result": product, "tools_used": tools_used}

            if action == "discount":
                tools_used.append("get_product")
                product = await mcp_client.call_tool("get_product", {"product_id": decision.get("product_id")})
                price = float(product.get("price", 0))
                percent = float(decision.get("percent", 0))
                tools_used.append("calculator")
                discounted = calculator(f"{price} * (1 - {percent} / 100)")
                return {
                    "tool_result": {
                        "product": product,
                        "discount_percent": percent,
                        "discounted_price": discounted,
                    },
                    "tools_used": tools_used,
                }

            logger.warning("Unknown action: %s", action)
            return {"error": "Не удалось определить действие для запроса.", "tools_used": tools_used}

        except Exception as exc:  # noqa: BLE001
            logger.exception("Agent execution error")
            return {"error": str(exc), "tools_used": tools_used}

    async def respond(state: AgentState) -> AgentState:
        if state.get("error"):
            logger.error("Agent response error: %s", state["error"])
            return {"response": state["error"], "tools_used": state.get("tools_used", [])}

        decision = state.get("decision", {})
        action = decision.get("action")
        result = state.get("tool_result")

        if action == "list_products":
            response = format_products(result)
            return {"response": response, "tools_used": state.get("tools_used", [])}

        if action == "get_statistics":
            count = result.get("count")
            avg = formatter(result.get("average_price"), "currency")
            response = f"Всего продуктов: {count}. Средняя цена: {avg}."
            return {"response": response, "tools_used": state.get("tools_used", [])}

        if action == "add_product":
            response = (
                "Добавлен продукт: "
                f"{result.get('name')} (ID {result.get('id')}) за {result.get('price')}"
            )
            return {"response": response, "tools_used": state.get("tools_used", [])}

        if action == "get_product":
            response = format_products([result])
            return {"response": response, "tools_used": state.get("tools_used", [])}

        if action == "discount":
            product = result.get("product", {})
            discounted = formatter(result.get("discounted_price"), "currency")
            response = (
                f"Цена товара {product.get('name')} после скидки "
                f"{result.get('discount_percent')}%: {discounted}"
            )
            return {"response": response, "tools_used": state.get("tools_used", [])}

        return {"response": "Запрос обработан.", "tools_used": state.get("tools_used", [])}

    graph = StateGraph(AgentState)
    graph.add_node("analyze", analyze)
    graph.add_node("execute", execute)
    graph.add_node("respond", respond)
    graph.set_entry_point("analyze")
    graph.add_edge("analyze", "execute")
    graph.add_edge("execute", "respond")
    graph.add_edge("respond", END)

    app = graph.compile()
    return AgentRunner(app)
