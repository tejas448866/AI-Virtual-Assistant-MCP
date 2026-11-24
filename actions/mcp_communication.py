"""
JARVIS action — Communication MCP Suite.
Powered by Model Context Protocol (MCP) for safe email and messaging assistance.
Always follows Human-in-the-Loop safety: prepares drafts without sending without confirmation.
"""
import json
from mcp.bridge import MCPActionBridge

_bridge = MCPActionBridge.get_instance()
_bridge.initialize_sync()


def mcp_communication_helper(parameters: dict, **kwargs) -> str:
    """
    Unified dispatcher for messaging and email assistance via MCP.
    """
    mode = parameters.get("mode", "email").lower()

    if mode == "whatsapp":
        tool_name = "mcp_comm_prepare_whatsapp_draft"
        args = {
            "phone_number": parameters.get("contact", ""),
            "message_text": parameters.get("content", ""),
        }
    else:  # email default
        tool_name = "mcp_comm_draft_email"
        args = {
            "recipient_name": parameters.get("contact", "Colleague"),
            "subject": parameters.get("subject", "Update"),
            "key_points": parameters.get("content", ""),
            "tone": parameters.get("tone", "formal"),
        }

    res = _bridge.execute_tool_sync(tool_name, args)
    if res.get("status") == "done":
        result_data = res.get("result", {})
        if isinstance(result_data, dict):
            if mode == "email":
                body = result_data.get("body", "")
                prompt = result_data.get("action_prompt", "")
                return f"[Communication MCP - Email Draft]\n{body}\n\n{prompt}"
            else:
                msg = result_data.get("preview_text", "")
                url = result_data.get("web_url", "")
                note = result_data.get("safety_note", "")
                return f"[Communication MCP - WhatsApp Draft]\nMessage: {msg}\nLink: {url}\n{note}"
        return f"[Communication MCP] {result_data}"
    elif res.get("status") == "cancelled":
        return f"[Communication MCP Safety Gate] {res.get('message')}"
    else:
        return f"[Communication MCP Error] {res.get('error', 'Execution error')}"


TOOL = {
    "name": "mcp_communication_helper",
    "description": (
        "Assists with drafting everyday emails and preparing WhatsApp messages safely via Model Context Protocol (MCP). "
        "Enforces Human-in-the-Loop safety: never sends messages externally without user review and confirmation. "
        "Modes: 'email' or 'whatsapp'."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "mode": {
                "type": "STRING",
                "description": "Communication channel: 'email' or 'whatsapp'",
            },
            "contact": {
                "type": "STRING",
                "description": "Recipient name, email address, or phone number",
            },
            "subject": {
                "type": "STRING",
                "description": "Email subject line (required for email)",
            },
            "content": {
                "type": "STRING",
                "description": "Key points or body content of the message",
            },
            "tone": {
                "type": "STRING",
                "description": "Tone: 'formal', 'casual', or 'urgent' (for email)",
            },
        },
        "required": ["mode", "content"],
    },
    "handler": mcp_communication_helper,
}
