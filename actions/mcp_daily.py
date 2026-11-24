"""
JARVIS action — Everyday Life MCP Suite.
Directly powered by the Model Context Protocol (MCP) Daily Life Server.
Provides natural tools for managing calendars, shopping lists, quick notes, personal budgets, and daily habits.
"""
import json
from mcp.bridge import MCPActionBridge

_bridge = MCPActionBridge.get_instance()
_bridge.initialize_sync()


def mcp_everyday_assistant(parameters: dict, **kwargs) -> str:
    """
    Unified dispatcher for everyday life MCP capabilities.
    """
    category = parameters.get("category", "notes").lower()
    action = parameters.get("action", "list").lower()

    if category == "calendar":
        tool_name = "mcp_daily_daily_calendar"
        args = {
            "action": action,
            "date": parameters.get("date"),
            "time": parameters.get("time"),
            "title": parameters.get("details") or parameters.get("title", "Event"),
        }
    elif category == "groceries":
        tool_name = "mcp_daily_grocery_list"
        args = {
            "action": action,
            "items": parameters.get("details") or parameters.get("items", ""),
        }
    elif category == "budget":
        tool_name = "mcp_daily_budget_tracker"
        args = {
            "action": action,
            "amount": float(parameters.get("amount", 0.0) or 0.0),
            "category": parameters.get("sub_category", "General"),
            "note": parameters.get("details", ""),
        }
    elif category == "habits":
        tool_name = "mcp_daily_habit_tracker"
        args = {
            "action": action,
            "habit": parameters.get("details", "daily_check"),
        }
    else:  # notes default
        tool_name = "mcp_daily_quick_notes"
        args = {
            "action": action,
            "text": parameters.get("details", ""),
            "query": parameters.get("query", ""),
        }

    res = _bridge.execute_tool_sync(tool_name, args)
    if res.get("status") == "done":
        result_data = res.get("result", {})
        if isinstance(result_data, dict):
            msg = result_data.get("message") or result_data.get("summary")
            if msg:
                return f"[Everyday MCP] {msg}"
            return f"[Everyday MCP] {json.dumps(result_data)}"
        return f"[Everyday MCP] {result_data}"
    elif res.get("status") == "cancelled":
        return f"[Everyday MCP Safety Gate] {res.get('message')}"
    else:
        return f"[Everyday MCP Error] {res.get('error', 'Execution error')}"


TOOL = {
    "name": "mcp_everyday_assistant",
    "description": (
        "Everyday personal assistant powered by Model Context Protocol (MCP). "
        "Use this for daily organization tasks: calendar schedules, grocery/shopping lists, "
        "quick thoughts/notes, daily expense tracking, and healthy habit logging. "
        "Categories: 'calendar', 'groceries', 'notes', 'budget', 'habits'. "
        "Actions: 'list', 'add', 'save', 'check_off', 'summary', 'clear'."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "category": {
                "type": "STRING",
                "description": "Category of everyday task: 'calendar', 'groceries', 'notes', 'budget', or 'habits'",
            },
            "action": {
                "type": "STRING",
                "description": "Action to perform: 'list', 'add', 'save', 'check_off', 'summary', 'clear'",
            },
            "details": {
                "type": "STRING",
                "description": "Item details, note text, appointment title, habit name, or expense note",
            },
            "date": {
                "type": "STRING",
                "description": "Optional date in YYYY-MM-DD format (for calendar)",
            },
            "time": {
                "type": "STRING",
                "description": "Optional time (e.g. 14:00 or 2:00 PM for calendar)",
            },
            "amount": {
                "type": "NUMBER",
                "description": "Optional numeric amount for expense logging (for budget)",
            },
            "sub_category": {
                "type": "STRING",
                "description": "Optional expense category (e.g. Food, Groceries, Travel, Bills)",
            },
            "query": {
                "type": "STRING",
                "description": "Optional search term to find existing notes",
            },
        },
        "required": ["category", "action"],
    },
    "handler": mcp_everyday_assistant,
}
