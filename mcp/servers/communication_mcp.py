"""
Communication MCP Server — Controlled messaging & drafting for everyday productivity.
Emphasizes Safety First: drafts are reviewed before external sending.
"""
from __future__ import annotations

import logging
import urllib.parse
from typing import Any, Dict, List

logger = logging.getLogger("OmniMCP.Communication")


class CommunicationMCPServer:
    """In-process MCP Server implementing everyday communication assistance."""

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
                "serverInfo": {"name": "everyday-communication", "version": "1.0.0"},
                "capabilities": {"tools": {}},
            }
        return {}

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "draft_email",
                "description": "Compose an email draft for everyday tasks (e.g. sick leave, inquiry, follow-up, RSVP).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "recipient_name": {"type": "string", "description": "Recipient name or email address"},
                        "subject": {"type": "string", "description": "Subject line"},
                        "key_points": {"type": "string", "description": "Core points to include in the email body"},
                        "tone": {"type": "string", "enum": ["formal", "casual", "urgent"], "description": "Desired tone"},
                    },
                    "required": ["recipient_name", "subject", "key_points"],
                },
            },
            {
                "name": "prepare_whatsapp_draft",
                "description": "Prepares a safe WhatsApp Web message draft with one-click preview (never sends without confirmation).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "phone_number": {"type": "string", "description": "Optional phone number with country code (e.g. +919876543210)"},
                        "message_text": {"type": "string", "description": "Draft message content"},
                    },
                    "required": ["message_text"],
                },
            },
        ]

    async def execute_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name == "draft_email":
            recipient = args.get("recipient_name", "Colleague")
            subject = args.get("subject", "Update")
            points = args.get("key_points", "")
            tone = args.get("tone", "formal")

            greeting = f"Dear {recipient}," if tone == "formal" else f"Hi {recipient},"
            sign_off = "Best regards,\n[Your Name]" if tone == "formal" else "Thanks,\n[Your Name]"

            body = f"{greeting}\n\nI am writing regarding {subject.lower()}.\n{points}\n\nPlease let me know if you have any questions.\n\n{sign_off}"

            return {
                "status": "done",
                "subject": subject,
                "body": body,
                "action_prompt": "Draft prepared. Would you like me to copy this to your clipboard or open your default mail client?",
            }

        elif name == "prepare_whatsapp_draft":
            phone = (args.get("phone_number") or "").replace("+", "").replace("-", "").replace(" ", "")
            msg = args.get("message_text", "")
            encoded_msg = urllib.parse.quote(msg)

            if phone:
                wa_url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}"
            else:
                wa_url = f"https://web.whatsapp.com/send?text={encoded_msg}"

            return {
                "status": "done",
                "preview_text": msg,
                "web_url": wa_url,
                "safety_note": "Prepared in safe mode. You can preview and send with a single click.",
            }

        return {"status": "failed", "error": f"Unknown tool '{name}'"}
