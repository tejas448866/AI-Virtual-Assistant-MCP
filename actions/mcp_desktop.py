"""
JARVIS action — Desktop Utility MCP Suite.
Powered by Model Context Protocol (MCP) for verified OS interactions.
Enables clipboard assistance, safe recent file search, volume control, and app coordination.
"""
import json
from mcp.bridge import MCPActionBridge

_bridge = MCPActionBridge.get_instance()
_bridge.initialize_sync()


def mcp_desktop_utility(parameters: dict, **kwargs) -> str:
    """
    Unified dispatcher for desktop OS utilities via MCP.
    """
    feature = parameters.get("feature", "clipboard").lower()
    action = parameters.get("action", "read").lower()

    if feature == "clipboard":
        tool_name = "mcp_desktop_clipboard_assistant"
        args = {"action": action, "text": parameters.get("text", "")}
    elif feature == "volume":
        tool_name = "mcp_desktop_system_audio"
        args = {"action": action, "level": int(parameters.get("level", 50))}
    elif feature == "files":
        tool_name = "mcp_desktop_quick_file_finder"
        args = {
            "keyword": parameters.get("keyword") or parameters.get("text", ""),
            "folder": parameters.get("folder", "downloads"),
        }
    else:  # apps
        tool_name = "mcp_desktop_desktop_apps"
        args = {"action": action, "app_name": parameters.get("text", "")}

    res = _bridge.execute_tool_sync(tool_name, args)
    if res.get("status") == "done":
        result_data = res.get("result", {})
        if isinstance(result_data, dict):
            msg = result_data.get("message") or result_data.get("summary")
            if msg:
                return f"[Desktop MCP] {msg}"
            return f"[Desktop MCP] {json.dumps(result_data)}"
        return f"[Desktop MCP] {result_data}"
    elif res.get("status") == "cancelled":
        return f"[Desktop MCP Safety Gate] {res.get('message')}"
    else:
        return f"[Desktop MCP Error] {res.get('error', 'Execution error')}"


TOOL = {
    "name": "mcp_desktop_utility",
    "description": (
        "Desktop OS control and utilities powered by Model Context Protocol (MCP). "
        "Provides safe and verified interactions with the system clipboard, volume control, "
        "and quick file searching in Downloads/Documents. "
        "Features: 'clipboard', 'volume', 'files', 'apps'."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "feature": {
                "type": "STRING",
                "description": "Desktop feature: 'clipboard', 'volume', 'files', or 'apps'",
            },
            "action": {
                "type": "STRING",
                "description": "Action: 'read', 'set', 'clear', 'get', 'mute', 'launch', or 'list_running'",
            },
            "text": {
                "type": "STRING",
                "description": "Text to set on clipboard, app name, or search keyword",
            },
            "level": {
                "type": "INTEGER",
                "description": "Volume percentage from 0 to 100",
            },
            "folder": {
                "type": "STRING",
                "description": "Folder to search in: 'downloads', 'documents', 'desktop'",
            },
        },
        "required": ["feature", "action"],
    },
    "handler": mcp_desktop_utility,
}
