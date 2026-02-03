from __future__ import annotations

import json
import sys
from typing import Any, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    def __init__(self, command: Optional[list[str]] = None) -> None:
        self._command = command or [sys.executable, "-m", "mcp_server.server"]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        params = StdioServerParameters(command=self._command[0], args=self._command[1:])
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments)
        return self._normalize_result(result)

    @staticmethod
    def _normalize_result(result: Any) -> Any:
        if isinstance(result, (dict, list)):
            return result
        if hasattr(result, "content"):
            content = result.content
            if isinstance(content, list) and content:
                first = content[0]
                text = getattr(first, "text", None)
                if isinstance(text, str):
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        return text
            return content
        return result
