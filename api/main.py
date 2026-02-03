from __future__ import annotations

import logging
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent.graph import build_agent, AgentRunner


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(title="AI Engineer Test Task")

_agent: AgentRunner | None = None


class QueryRequest(BaseModel):
    query: str


def get_agent() -> AgentRunner:
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


@app.post("/api/v1/agent/query")
async def query_agent(request: QueryRequest) -> dict:
    try:
        agent = get_agent()
        logger.info("Query received: %s", request.query)
        return await agent.run(request.query)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unhandled error in API")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
