"""
MCP Action Bridge — Seamlessly exposes MCP tools into the assistant's core runtime.

Allows Gemini Live, OpenAI, and local LLM backends to invoke any discovered
MCP tool natively through standard function calling.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional

from .server_manager import MCPServerManager

logger = logging.getLogger("OmniMCP.Bridge")


class MCPActionBridge:
    """Singleton bridge linking MCPServerManager with the assistant engine."""

    _instance: Optional["MCPActionBridge"] = None

    def __init__(self):
        self.manager = MCPServerManager()
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    @classmethod
    def get_instance(cls) -> "MCPActionBridge":
        if cls._instance is None:
            cls._instance = MCPActionBridge()
        return cls._instance

    def initialize_sync(self) -> None:
        """Synchronously bootstraps the MCP manager inside an event loop."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Already running loop (e.g. within an async app)
                asyncio.create_task(self.manager.initialize_all())
            else:
                loop.run_until_complete(self.manager.initialize_all())
        except RuntimeError:
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            new_loop.run_until_complete(self.manager.initialize_all())

    def get_tool_declarations(self) -> List[Dict[str, Any]]:
        """Returns Gemini/OpenAI tool declarations for all connected MCP servers."""
        return self.manager.get_all_tool_declarations()

    def execute_tool_sync(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        confirm_callback: Optional[Callable[[str], bool]] = None,
    ) -> Dict[str, Any]:
        """Synchronous wrapper to execute an MCP tool from standard synchronous action dispatchers."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Run with future in background loop or separate thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(
                        asyncio.run,
                        self.manager.execute_tool(tool_name, arguments, confirm_callback)
                    )
                    return future.result(timeout=20.0)
            else:
                return loop.run_until_complete(
                    self.manager.execute_tool(tool_name, arguments, confirm_callback)
                )
        except Exception as e:
            logger.error("Failed to execute MCP tool '%s' synchronously: %s", tool_name, e)
            return {"status": "failed", "error": str(e)}
