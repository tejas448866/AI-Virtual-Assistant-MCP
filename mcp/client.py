"""
Model Context Protocol (MCP) Client Implementation.

Supports:
- JSON-RPC 2.0 protocol over stdio subprocess transport
- Capability negotiation (`initialize`, `tools/list`, `tools/call`, `resources/list`)
- Direct Python in-process handler transport for zero-latency local servers
- Asynchronous execution with timeout guards and health monitoring
"""
from __future__ import annotations

import asyncio
import json
import logging
import subprocess
import sys
from typing import Any, Callable, Dict, List, Optional

from .schemas import JSONRPCRequest, JSONRPCResponse, MCPTool

logger = logging.getLogger("OmniMCP.Client")


class StdIOTransport:
    """Manages an external MCP server running in a child process via standard I/O."""

    def __init__(self, command: str, args: Optional[List[str]] = None, env: Optional[Dict[str, str]] = None):
        self.command = command
        self.args = args or []
        self.env = env
        self.process: Optional[asyncio.subprocess.Process] = None
        self._request_counter = 0

    async def start(self) -> None:
        """Launches the MCP server subprocess."""
        import shutil
        resolved_cmd = shutil.which(self.command) or self.command
        cmd_list = [resolved_cmd] + self.args
        creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        try:
            self.process = await asyncio.create_subprocess_exec(
                *cmd_list,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                creationflags=creationflags,
                env=self.env,
            )
            logger.info("Started MCP subprocess: %s (PID: %d)", resolved_cmd, self.process.pid)
        except Exception as e:
            logger.error("Failed to start MCP server subprocess '%s': %s", self.command, e)
            raise

    async def send_request(self, method: str, params: Optional[Dict[str, Any]] = None, timeout: float = 15.0) -> Any:
        """Sends a JSON-RPC request and awaits the parsed JSON result."""
        if not self.process or self.process.returncode is not None:
            raise RuntimeError(f"MCP server subprocess '{self.command}' is not running.")

        self._request_counter += 1
        req_id = self._request_counter
        req = JSONRPCRequest(method=method, params=params, id=req_id)
        raw_msg = req.to_json() + "\n"

        assert self.process.stdin is not None
        assert self.process.stdout is not None

        self.process.stdin.write(raw_msg.encode("utf-8"))
        await self.process.stdin.drain()

        # Read line response with timeout
        try:
            line_bytes = await asyncio.wait_for(self.process.stdout.readline(), timeout=timeout)
            if not line_bytes:
                raise ConnectionResetError("MCP server process closed output stream.")
            data = json.loads(line_bytes.decode("utf-8").strip())
            resp = JSONRPCResponse.from_dict(data)
            if resp.error:
                raise RuntimeError(f"MCP Error [{resp.error.get('code')}]: {resp.error.get('message')}")
            return resp.result
        except asyncio.TimeoutError:
            logger.error("Timeout (%0.1fs) waiting for MCP server '%s' on method '%s'", timeout, self.command, method)
            raise TimeoutError(f"MCP server timed out on {method}")

    async def close(self) -> None:
        if self.process and self.process.returncode is None:
            try:
                self.process.terminate()
                await asyncio.wait_for(self.process.wait(), timeout=3.0)
            except Exception:
                self.process.kill()


class MCPClient:
    """High-level client interacting with one MCP server instance."""

    def __init__(self, name: str, transport: Optional[StdIOTransport] = None, in_process_handler: Optional[Callable] = None):
        self.name = name
        self.transport = transport
        self.in_process_handler = in_process_handler
        self.tools: Dict[str, MCPTool] = {}
        self.server_info: Dict[str, Any] = {}
        self.is_initialized = False

    async def initialize(self) -> bool:
        """Handshakes with the MCP server and negotiates protocol capabilities."""
        if self.in_process_handler:
            self.server_info = {"name": self.name, "version": "1.0.0", "mode": "in-process"}
            self.is_initialized = True
            await self.refresh_tools()
            return True

        if not self.transport:
            raise ValueError(f"MCPClient '{self.name}' has no active transport.")

        await self.transport.start()
        init_params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {"listChanged": True},
                "sampling": {},
            },
            "clientInfo": {
                "name": "OmniMCP-Assistant",
                "version": "1.0.0",
            },
        }

        result = await self.transport.send_request("initialize", init_params)
        self.server_info = result if isinstance(result, dict) else {}
        self.is_initialized = True
        logger.info("Initialized MCP server '%s': %s", self.name, self.server_info)

        # Notify initialized
        try:
            await self.transport.send_request("notifications/initialized", {})
        except Exception:
            pass  # Notifications might not return a response

        await self.refresh_tools()
        return True

    async def refresh_tools(self) -> List[MCPTool]:
        """Queries the MCP server for available tools via `tools/list`."""
        if self.in_process_handler:
            # Local in-process handler
            tool_defs = await self.in_process_handler("tools/list", {})
        elif self.transport:
            tool_defs = await self.transport.send_request("tools/list", {})
        else:
            return []

        tools_list = []
        raw_tools = tool_defs.get("tools", []) if isinstance(tool_defs, dict) else []
        for t in raw_tools:
            tool_obj = MCPTool(
                name=t.get("name", "unnamed"),
                description=t.get("description", ""),
                input_schema=t.get("inputSchema", {}),
                server_name=self.name,
            )
            self.tools[tool_obj.name] = tool_obj
            tools_list.append(tool_obj)

        logger.info("Discovered %d tools from MCP server '%s'", len(tools_list), self.name)
        return tools_list

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Executes a tool on the MCP server via `tools/call`."""
        if self.in_process_handler:
            return await self.in_process_handler("tools/call", {"name": tool_name, "arguments": arguments})

        if not self.transport:
            raise RuntimeError(f"No transport available for MCP server '{self.name}'")

        params = {"name": tool_name, "arguments": arguments}
        return await self.transport.send_request("tools/call", params)

    async def close(self) -> None:
        if self.transport:
            await self.transport.close()
