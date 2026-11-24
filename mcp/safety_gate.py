"""
Safety Gate — Controlled Interactions for Everyday Utility ("Less Magic, More Utility").

Every tool execution in the assistant passes through this safety gate:
1. SAFE / READ_ONLY: Executes automatically.
2. REVERSIBLE: Executes automatically with an undo receipt and immediate HUD audit log.
3. CRITICAL / IRREVERSIBLE: Pauses for explicit user confirmation via voice or HUD button.
"""
from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Callable, Dict, Optional, Tuple

logger = logging.getLogger("OmniMCP.SafetyGate")


class ConfirmationLevel(Enum):
    SAFE = "safe"                          # Read-only operations, queries, status checks
    REVERSIBLE = "reversible"              # Draft creation, app launching, note additions
    CRITICAL = "critical"                  # External messaging, file deletion, system shutdown, purchasing


class SafetyGate:
    def __init__(self, require_voice_confirm: bool = True):
        self.require_voice_confirm = require_voice_confirm
        # Explicit mapping of dangerous keywords or prefixes
        self._critical_patterns = (
            "delete", "remove", "drop", "purge", "shutdown", "reboot",
            "send_message", "send_email", "pay", "order", "purchase",
            "format", "terminate", "kill"
        )
        self._safe_patterns = (
            "get", "read", "list", "search", "check", "view", "find",
            "status", "query", "summarize", "inspect", "fetch"
        )
        self._callbacks: Dict[str, Callable] = {}

    def classify_action(self, tool_name: str, arguments: Dict[str, Any]) -> ConfirmationLevel:
        """Determines the safety level of an action based on tool metadata and argument payload."""
        lower_name = tool_name.lower()
        action_arg = str(arguments.get("action", "")).lower()

        # Check explicit critical patterns in name or action argument
        for crit in self._critical_patterns:
            if crit in lower_name or crit in action_arg:
                return ConfirmationLevel.CRITICAL

        # Check safe patterns in name or action argument
        for safe in self._safe_patterns:
            if safe in lower_name or safe in action_arg:
                return ConfirmationLevel.SAFE

        # Check argument risk
        if any(k in arguments for k in ("force", "overwrite", "permanent", "confirm")):
            if arguments.get("force") is True or arguments.get("overwrite") is True:
                return ConfirmationLevel.CRITICAL

        # Default standard actions to REVERSIBLE
        return ConfirmationLevel.REVERSIBLE

    def evaluate(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        confirm_callback: Optional[Callable[[str], bool]] = None
    ) -> Tuple[bool, str]:
        """
        Evaluates whether an action is permitted to execute immediately,
        or requires human-in-the-loop confirmation.
        Returns: (allowed: bool, reason_or_preview: str)
        """
        level = self.classify_action(tool_name, arguments)

        if level == ConfirmationLevel.SAFE:
            return True, f"Auto-approved read action [{tool_name}]."

        if level == ConfirmationLevel.REVERSIBLE:
            logger.info("Executing reversible action [%s] with audit logging.", tool_name)
            return True, f"Approved action [{tool_name}] with recovery point."

        # Level is CRITICAL
        preview = self._format_action_preview(tool_name, arguments)
        logger.warning("Critical action requested: %s. Awaiting confirmation.", preview)

        if confirm_callback:
            user_agreed = confirm_callback(preview)
            if user_agreed:
                return True, f"User confirmed critical action [{tool_name}]."
            else:
                return False, f"Action [{tool_name}] was cancelled by the user."

        # If no interactive callback is hooked, enforce gate block for safety
        return False, f"Action [{tool_name}] requires explicit confirmation: '{preview}'"

    def _format_action_preview(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Generates an intuitive, non-technical description of the requested action for everyday users."""
        clean_tool = tool_name.replace("mcp_", "")
        args_summary = ", ".join(f"{k}='{v}'" for k, v in list(arguments.items())[:3])
        return f"{clean_tool} ({args_summary})"
