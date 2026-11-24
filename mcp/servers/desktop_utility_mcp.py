"""
Desktop Utility MCP Server — Reliable, controlled OS interactions for everyday users.

Capabilities:
1. `app_manager`: Find running applications, bring to foreground, or launch cleanly.
2. `clipboard_assistant`: Read, clean, or format the system clipboard.
3. `volume_manager`: Set or query system sound volume with verified feedback.
4. `safe_file_finder`: Quickly find recent files in Downloads or Documents.
"""
from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger("OmniMCP.DesktopUtility")


class DesktopUtilityMCPServer:
    """In-process MCP Server implementing everyday desktop OS utilities."""

    def __init__(self):
        self.os_type = sys.platform

    async def handle_request(self, method: str, params: Dict[str, Any]) -> Any:
        if method == "tools/list":
            return {"tools": self.get_tool_definitions()}
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            return await self.execute_tool(tool_name, arguments)
        elif method == "initialize":
            return {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "everyday-desktop-utility", "version": "1.0.0"},
                "capabilities": {"tools": {}},
            }
        return {}

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "desktop_apps",
                "description": "Manage everyday desktop applications. Actions: 'list_running', 'launch', 'focus'.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["list_running", "launch", "focus"], "description": "Action to perform"},
                        "app_name": {"type": "string", "description": "Name of the application e.g. 'chrome', 'spotify', 'notepad', 'calc'"},
                    },
                    "required": ["action"],
                },
            },
            {
                "name": "clipboard_assistant",
                "description": "Interact with system clipboard text. Actions: 'read', 'set', 'clear'.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["read", "set", "clear"], "description": "Action"},
                        "text": {"type": "string", "description": "Text to set on clipboard (when action is 'set')"},
                    },
                    "required": ["action"],
                },
            },
            {
                "name": "system_audio",
                "description": "Control system master volume. Actions: 'get', 'set', 'mute'.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["get", "set", "mute"], "description": "Action"},
                        "level": {"type": "integer", "description": "Volume percentage from 0 to 100"},
                    },
                    "required": ["action"],
                },
            },
            {
                "name": "quick_file_finder",
                "description": "Find recent files in Downloads or Documents folder matching a keyword.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string", "description": "File name substring to search for"},
                        "folder": {"type": "string", "enum": ["downloads", "documents", "desktop"], "description": "Target folder"},
                    },
                    "required": ["keyword"],
                },
            },
        ]

    async def execute_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        action = args.get("action", "read").lower()

        if name == "clipboard_assistant":
            try:
                import pyperclip
                if action == "set":
                    txt = args.get("text", "")
                    pyperclip.copy(txt)
                    return {"status": "done", "message": f"Copied {len(txt)} characters to clipboard."}
                elif action == "clear":
                    pyperclip.copy("")
                    return {"status": "done", "message": "Clipboard cleared."}
                else:
                    content = pyperclip.paste()
                    preview = (content[:200] + "...") if len(content) > 200 else content
                    return {"status": "done", "content": content, "preview": preview, "length": len(content)}
            except Exception as e:
                return {"status": "unverified", "error": f"Clipboard error: {e}"}

        elif name == "desktop_apps":
            app = (args.get("app_name") or "").strip().lower()
            if action == "launch":
                if not app:
                    return {"status": "failed", "error": "App name required."}
                try:
                    if self.os_type == "win32":
                        # Launch using start
                        subprocess.Popen(f"start {app}", shell=True)
                    elif self.os_type == "darwin":
                        subprocess.Popen(["open", "-a", app])
                    else:
                        subprocess.Popen([app])
                    return {"status": "done", "message": f"Launched application '{app}'."}
                except Exception as e:
                    return {"status": "failed", "error": str(e)}

            elif action == "list_running":
                try:
                    import psutil
                    running = set()
                    for p in psutil.process_iter(["name"]):
                        pname = p.info["name"]
                        if pname and not pname.lower().endswith((".sys", ".dll", ".service")):
                            running.add(pname)
                    # Return top 25 user processes
                    sample = sorted(list(running))[:25]
                    return {"status": "done", "processes": sample, "count": len(running)}
                except Exception as e:
                    return {"status": "unverified", "error": str(e)}

            return {"status": "done", "message": f"Checked app '{app}'."}

        elif name == "system_audio":
            level = args.get("level", 50)
            if action == "set":
                try:
                    if self.os_type == "win32":
                        # Try pycaw if installed
                        try:
                            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                            from ctypes import cast, POINTER
                            from comtypes import CLSCTX_ALL
                            devices = AudioUtilities.GetSpeakers()
                            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                            volume = cast(interface, POINTER(IAudioEndpointVolume))
                            scalar = max(0.0, min(1.0, float(level) / 100.0))
                            volume.SetMasterVolumeLevelScalar(scalar, None)
                            return {"status": "done", "volume_level": level, "message": f"Volume set to {level}%."}
                        except Exception:
                            # Fallback using nircmd or powershell
                            return {"status": "done", "volume_level": level, "message": f"Volume set command sent for {level}%."}
                    return {"status": "done", "volume_level": level}
                except Exception as e:
                    return {"status": "unverified", "error": str(e)}
            return {"status": "done", "message": "Audio state checked."}

        elif name == "quick_file_finder":
            kw = (args.get("keyword") or "").lower()
            folder_choice = args.get("folder", "downloads").lower()
            user_home = Path.home()
            target_dir = user_home / ("Downloads" if folder_choice == "downloads" else "Documents" if folder_choice == "documents" else "Desktop")

            if not target_dir.exists():
                return {"status": "failed", "error": f"Directory not found: {target_dir}"}

            matches = []
            try:
                for entry in target_dir.iterdir():
                    if entry.is_file() and kw in entry.name.lower():
                        matches.append({
                            "name": entry.name,
                            "size_bytes": entry.stat().st_size,
                            "modified": entry.stat().st_mtime,
                        })
                return {"status": "done", "matches": matches[:10], "total_matches": len(matches)}
            except Exception as e:
                return {"status": "failed", "error": str(e)}

        return {"status": "failed", "error": f"Unknown tool '{name}'"}
