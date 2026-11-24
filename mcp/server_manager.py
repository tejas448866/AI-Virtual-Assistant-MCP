"""
MCP Server Manager — Aggregates and orchestrates all configured MCP servers.

Reads `mcp_servers.json`, auto-initializes built-in everyday servers,
spawns external stdio MCP processes, discovers tools, and provides a unified
tool execution router governed by the Safety Gate.
"""
from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .client import MCPClient, StdIOTransport
from .safety_gate import SafetyGate
from .schemas import MCPTool
from .servers.daily_life_mcp import DailyLifeMCPServer
from .servers.desktop_utility_mcp import DesktopUtilityMCPServer
from .servers.communication_mcp import CommunicationMCPServer

logger = logging.getLogger("OmniMCP.ServerManager")


class MCPServerManager:
    """Central registry and coordinator for all Model Context Protocol servers."""

    def __init__(self, config_path: Optional[Path] = None, safety_gate: Optional[SafetyGate] = None):
        self.config_path = config_path or (Path(__file__).resolve().parent.parent / "mcp_servers.json")
        self.safety_gate = safety_gate or SafetyGate()
        self.clients: Dict[str, MCPClient] = {}
        self.all_tools: Dict[str, MCPTool] = {}  # Global lookup: full_name -> MCPTool
        self._initialized = False

    async def initialize_all(self) -> None:
        """Initializes all built-in and external MCP servers."""
        if self._initialized:
            return

        logger.info("Initializing MCP Server Manager...")

        # 1. Register Built-in Everyday MCP Servers (Zero configuration, fast)
        await self._register_builtin_servers()

        # 2. Register External Configured MCP Servers (from mcp_servers.json)
        await self._load_external_servers()

        # 3. Aggregate all discovered tools
        self.all_tools.clear()
        for s_name, client in self.clients.items():
            for t_name, tool in client.tools.items():
                namespaced_name = f"mcp_{s_name}_{t_name}"
                self.all_tools[namespaced_name] = tool

        self._initialized = True
        logger.info("MCP Manager online: %d servers active, %d total tools registered.", len(self.clients), len(self.all_tools))

    async def _register_builtin_servers(self) -> None:
        """Mounts default everyday servers directly into the assistant runtime."""
        # Daily Life MCP
        daily_server = DailyLifeMCPServer()
        daily_client = MCPClient(
            name="daily",
            in_process_handler=daily_server.handle_request,
        )
        await daily_client.initialize()
        self.clients["daily"] = daily_client

        # Desktop Utility MCP
        desktop_server = DesktopUtilityMCPServer()
        desktop_client = MCPClient(
            name="desktop",
            in_process_handler=desktop_server.handle_request,
        )
        await desktop_client.initialize()
        self.clients["desktop"] = desktop_client

        # Communication MCP
        comm_server = CommunicationMCPServer()
        comm_client = MCPClient(
            name="comm",
            in_process_handler=comm_server.handle_request,
        )
        await comm_client.initialize()
        self.clients["comm"] = comm_client

    async def _load_external_servers(self) -> None:
        """Reads mcp_servers.json and starts external stdio subprocess servers."""
        if not self.config_path.exists():
            logger.info("No external mcp_servers.json found at %s. Using built-in servers.", self.config_path)
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.error("Failed to parse mcp_servers.json: %s", e)
            return

        servers_dict = data.get("mcpServers", {})
        for s_name, s_conf in servers_dict.items():
            cmd = s_conf.get("command")
            if not cmd:
                continue
            args = s_conf.get("args", [])
            env = s_conf.get("env")
            transport = StdIOTransport(command=cmd, args=args, env=env)
            client = MCPClient(name=s_name, transport=transport)
            try:
                # Add with timeout so a hung server does not block assistant boot
                await asyncio.wait_for(client.initialize(), timeout=8.0)
                self.clients[s_name] = client
            except Exception as e:
                logger.warning("Could not start external MCP server '%s': %s", s_name, e)

    def get_all_tool_declarations(self) -> List[Dict[str, Any]]:
        """Returns Gemini/OpenAI-compatible tool declarations for all registered MCP tools."""
        declarations = []
        for namespaced_name, tool in self.all_tools.items():
            decl = tool.to_gemini_declaration()
            decl["name"] = namespaced_name
            declarations.append(decl)
        return declarations

    async def execute_tool(
        self,
        namespaced_tool_name: str,
        arguments: Dict[str, Any],
        confirm_callback: Optional[Callable[[str], bool]] = None,
    ) -> Dict[str, Any]:
        """
        Executes an MCP tool with full Safety Gate evaluation.
        """
        # Safety gate check
        allowed, reason = self.safety_gate.evaluate(
            tool_name=namespaced_tool_name,
            arguments=arguments,
            confirm_callback=confirm_callback,
        )

        if not allowed:
            return {
                "status": "cancelled",
                "gate_reason": reason,
                "message": f"Action paused for safety: {reason}",
            }

        # Resolve server and tool name
        # Format is mcp_{server_name}_{tool_name}
        if not namespaced_tool_name.startswith("mcp_"):
            return {"status": "failed", "error": f"Invalid MCP tool identifier: {namespaced_tool_name}"}

        parts = namespaced_tool_name[4:].split("_", 1)
        if len(parts) != 2:
            return {"status": "failed", "error": f"Malformed tool name: {namespaced_tool_name}"}

        server_name, actual_tool_name = parts
        client = self.clients.get(server_name)
        if not client:
            return {"status": "failed", "error": f"MCP server '{server_name}' is not connected."}

        try:
            raw_result = await client.call_tool(actual_tool_name, arguments)
            return {
                "status": "done",
                "server": server_name,
                "tool": actual_tool_name,
                "result": raw_result,
            }
        except Exception as e:
            logger.error("Error executing MCP tool '%s': %s", namespaced_tool_name, e)
            return {"status": "failed", "error": str(e)}

    async def shutdown(self) -> None:
        """Gracefully shuts down all child transports."""
        for client in self.clients.values():
            await client.close()
        self.clients.clear()
        self.all_tools.clear()
