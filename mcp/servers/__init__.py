"""
Built-in MCP Servers for everyday life and desktop utility.
"""
from .daily_life_mcp import DailyLifeMCPServer
from .desktop_utility_mcp import DesktopUtilityMCPServer
from .communication_mcp import CommunicationMCPServer

__all__ = [
    "DailyLifeMCPServer",
    "DesktopUtilityMCPServer",
    "CommunicationMCPServer",
]
