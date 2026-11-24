"""
OmniMCP — Model Context Protocol Subsystem for AI Virtual Assistant.

Implements the official Model Context Protocol (MCP) JSON-RPC standard,
enabling the AI Virtual Assistant to connect seamlessly to local and remote
MCP servers, discover tools dynamically, and execute real-world everyday actions
under a strictly controlled Human-in-the-Loop safety gate.
"""

from .client import MCPClient, StdIOTransport
from .server_manager import MCPServerManager
from .safety_gate import SafetyGate, ConfirmationLevel
from .bridge import MCPActionBridge

__all__ = [
    "MCPClient",
    "StdIOTransport",
    "MCPServerManager",
    "SafetyGate",
    "ConfirmationLevel",
    "MCPActionBridge",
]
