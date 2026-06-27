"""
MCP client manager — async.

Manages stdio connections to one or more MCP servers.
Provides tool catalogue in OpenAI format and async tool dispatch.
"""

import re
import uuid
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Read-only tool name patterns — tools matching these are safe for reviewer use.
# All other tools (write/edit/delete/move) are excluded from the read-only subset.
_READONLY_TOOL_PATTERNS = (
    r"^read",           # read, read_file, read_text_file
    r"^list",           # list, list_files, list_directory
    r"^grep",           # grep, grep_file
    r"^search",         # search
    r"^stat",           # stat
    r"^get_file_info",  # get_file_info
    r"^find",           # find (read-only search)
    r"^head",           # head
    r"^tail",           # tail
    r"^cat",            # cat
)


class MCPClient:
    """Manages connections to multiple MCP servers."""

    def __init__(self, servers: dict[str, dict]) -> None:
        self._servers = servers
        self._sessions: dict[str, ClientSession] = {}
        self._contexts: list = []
        self._tools: dict[str, dict] = {}  # tool_name -> {server, description, input_schema}

    async def connect(self) -> None:
        """Connect to all configured MCP servers and build tool catalogue."""
        for name, cfg in self._servers.items():
            params = StdioServerParameters(
                command=cfg["command"],
                args=cfg.get("args", []),
                env=cfg.get("env"),
            )
            try:
                ctx = stdio_client(params)
                read, write = await ctx.__aenter__()
                self._contexts.append(ctx)
                session = ClientSession(read, write)
                await session.__aenter__()
                await session.initialize()
                self._sessions[name] = session
                response = await session.list_tools()
                for tool in response.tools:
                    self._tools[tool.name] = {
                        "server": name,
                        "description": tool.description or "",
                        "input_schema": tool.inputSchema or {},
                    }
                print(f"[ael] Connected: {name} ({len(response.tools)} tools)")
            except Exception as e:
                print(f"[ael] Warning: failed to connect to '{name}': {e}")

    def _is_readonly_tool(self, name: str) -> bool:
        """Return True if the tool name matches a read-only pattern."""
        return any(re.match(pattern, name) for pattern in _READONLY_TOOL_PATTERNS)

    def get_openai_tools(self, readonly: bool = False) -> list[dict]:
        """
        Return tool catalogue in OpenAI tools array format.

        Args:
            readonly: If True, return only read-only tools (read/list/grep/search).
                      If False, return all tools.
        """
        tools = []
        for name, meta in self._tools.items():
            if readonly and not self._is_readonly_tool(name):
                continue
            tools.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": meta["description"],
                    "parameters": meta["input_schema"],
                },
            })
        return tools

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        """Dispatch a tool call and return result as string."""
        if name not in self._tools:
            return f"Error: unknown tool '{name}'"
        server_name = self._tools[name]["server"]
        session = self._sessions.get(server_name)
        if not session:
            return f"Error: server '{server_name}' not connected"
        try:
            result = await session.call_tool(name, arguments)
            parts = []
            for content in result.content:
                if hasattr(content, "text"):
                    parts.append(content.text)
                else:
                    parts.append(str(content))
            return "\n".join(parts)
        except Exception as e:
            return f"Error calling '{name}': {e}"

    async def close(self) -> None:
        """Close all server connections."""
        for session in self._sessions.values():
            try:
                await session.__aexit__(None, None, None)
            except Exception:
                pass
        # Note: ctx.__aexit__() is intentionally skipped. Calling it during orchestrator
        # shutdown raises anyio RuntimeError (cancel scope task mismatch) on Python 3.11.
        # The stdio subprocess is a short-lived child process; it will be reaped by the OS
        # when the parent process exits. This is safe for single-run orchestrator sessions.
        self._contexts.clear()
