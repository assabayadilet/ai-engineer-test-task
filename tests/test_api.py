from __future__ import annotations

from fastapi.testclient import TestClient

from api import main


class FakeAgent:
    async def run(self, query: str) -> dict:
        return {"response": "ok", "tools_used": []}


def test_api_query(monkeypatch):
    monkeypatch.setattr(main, "get_agent", lambda: FakeAgent())
    client = TestClient(main.app)
    response = client.post("/api/v1/agent/query", json={"query": "test"})
    assert response.status_code == 200
    assert response.json()["response"] == "ok"
