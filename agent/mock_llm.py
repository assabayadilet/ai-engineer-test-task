from __future__ import annotations

import json
from typing import Any, List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from .parser import parse_query


class MockLLM(BaseChatModel):
    """Mock LLM that returns a deterministic action plan for the agent."""

    @property
    def _llm_type(self) -> str:  # noqa: D401
        return "mock-llm"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> ChatResult:
        user_text = messages[-1].content if messages else ""
        decision = parse_query(str(user_text))
        content = json.dumps(decision, ensure_ascii=False)
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])
