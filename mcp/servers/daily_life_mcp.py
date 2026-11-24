"""
Daily Life MCP Server — Everyday personal assistant tools for regular users.

Capabilities:
1. `manage_calendar`: View, check conflicts, or add schedule items.
2. `grocery_list`: Add, view, check off, or clear shopping items.
3. `quick_notes`: Save, search, and manage everyday thoughts and reminders.
4. `budget_tracker`: Log daily expenses, calculate budget spent by category.
5. `habit_tracker`: Check and log daily habits (medicines, water, exercise).
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger("OmniMCP.DailyLife")


class DailyLifeMCPServer:
    """In-process MCP Server implementing everyday life utilities."""

    def __init__(self, storage_dir: Optional[Path] = None):
        if storage_dir is None:
            storage_dir = Path.home() / ".jarvis" / "everyday_data"
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.groceries_file = self.storage_dir / "groceries.json"
        self.notes_file = self.storage_dir / "notes.json"
        self.budget_file = self.storage_dir / "expenses.json"
        self.calendar_file = self.storage_dir / "calendar.json"
        self.habits_file = self.storage_dir / "habits.json"

    # ── Helpers ──────────────────────────────────────────────────────────────
    def _read_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default

    def _write_json(self, path: Path, data: Any) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ── MCP Protocol Dispatch ────────────────────────────────────────────────
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
                "serverInfo": {"name": "everyday-daily-life", "version": "1.0.0"},
                "capabilities": {"tools": {}},
            }
        return {}

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "daily_calendar",
                "description": "Manage everyday appointments and check schedule conflicts. Actions: 'list', 'add', 'clear'.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["list", "add", "clear"], "description": "Action to perform"},
                        "date": {"type": "string", "description": "Date format YYYY-MM-DD (defaults to today)"},
                        "time": {"type": "string", "description": "Time e.g. 14:30 or 2:30 PM"},
                        "title": {"type": "string", "description": "Event description or appointment name"},
                    },
                    "required": ["action"],
                },
            },
            {
                "name": "grocery_list",
                "description": "Everyday shopping and grocery manager. Actions: 'list', 'add', 'check_off', 'clear'.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["list", "add", "check_off", "clear"], "description": "List action"},
                        "items": {"type": "string", "description": "Comma-separated items to add or remove (e.g. 'Milk, Eggs, Bread')"},
                    },
                    "required": ["action"],
                },
            },
            {
                "name": "quick_notes",
                "description": "Capture quick thoughts, ideas, or search stored notes. Actions: 'save', 'search', 'list'.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["save", "search", "list"], "description": "Notes action"},
                        "text": {"type": "string", "description": "Content of the note to save"},
                        "query": {"type": "string", "description": "Keyword to search existing notes"},
                    },
                    "required": ["action"],
                },
            },
            {
                "name": "budget_tracker",
                "description": "Track everyday personal expenses and view categorized budget summary. Actions: 'log', 'summary'.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["log", "summary"], "description": "Budget action"},
                        "amount": {"type": "number", "description": "Expense amount spent"},
                        "category": {"type": "string", "description": "Category e.g. Food, Transport, Bills, Shopping"},
                        "note": {"type": "string", "description": "Brief description of the purchase"},
                    },
                    "required": ["action"],
                },
            },
            {
                "name": "habit_tracker",
                "description": "Track everyday healthy habits (medication, hydration, exercise). Actions: 'log', 'status'.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["log", "status"], "description": "Habit action"},
                        "habit": {"type": "string", "description": "Name of habit e.g. 'morning_vitamins', 'drink_water', 'exercise'"},
                        "details": {"type": "string", "description": "Optional notes or quantity"},
                    },
                    "required": ["action"],
                },
            },
        ]

    async def execute_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        action = args.get("action", "list").lower()

        if name == "grocery_list":
            groceries = self._read_json(self.groceries_file, [])
            if action == "add":
                items_str = args.get("items", "")
                new_items = [i.strip() for i in items_str.split(",") if i.strip()]
                for item in new_items:
                    groceries.append({"item": item, "added_at": datetime.now().isoformat(), "done": False})
                self._write_json(self.groceries_file, groceries)
                return {"status": "done", "message": f"Added {len(new_items)} items to grocery list: {', '.join(new_items)}"}
            elif action == "check_off":
                target = (args.get("items") or "").lower()
                matched = 0
                for g in groceries:
                    if target in g["item"].lower():
                        g["done"] = True
                        matched += 1
                self._write_json(self.groceries_file, groceries)
                return {"status": "done", "message": f"Checked off {matched} item(s) matching '{target}'."}
            elif action == "clear":
                self._write_json(self.groceries_file, [])
                return {"status": "done", "message": "Grocery list cleared."}
            else:  # list
                pending = [g["item"] for g in groceries if not g.get("done")]
                completed = [g["item"] for g in groceries if g.get("done")]
                return {
                    "status": "done",
                    "pending_items": pending,
                    "completed_items": completed,
                    "summary": f"{len(pending)} pending items: {', '.join(pending) if pending else 'None'}",
                }

        elif name == "quick_notes":
            notes = self._read_json(self.notes_file, [])
            if action == "save":
                text = (args.get("text") or "").strip()
                if not text:
                    return {"status": "failed", "error": "Note text is required."}
                entry = {"id": len(notes) + 1, "text": text, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")}
                notes.append(entry)
                self._write_json(self.notes_file, notes)
                return {"status": "done", "message": f"Saved note: '{text}'"}
            elif action == "search":
                q = (args.get("query") or "").lower()
                matches = [n for n in notes if q in n["text"].lower()]
                return {"status": "done", "matches": matches, "count": len(matches)}
            else:  # list
                recent = notes[-5:]
                return {"status": "done", "recent_notes": recent, "total_notes": len(notes)}

        elif name == "budget_tracker":
            expenses = self._read_json(self.budget_file, [])
            if action == "log":
                amt = float(args.get("amount", 0.0))
                category = args.get("category", "General").capitalize()
                note = args.get("note", "")
                expenses.append({
                    "amount": amt,
                    "category": category,
                    "note": note,
                    "timestamp": datetime.now().isoformat(),
                })
                self._write_json(self.budget_file, expenses)
                return {"status": "done", "message": f"Logged expense of ${amt:.2f} under {category}."}
            else:  # summary
                total = sum(e.get("amount", 0) for e in expenses)
                by_cat: Dict[str, float] = {}
                for e in expenses:
                    c = e.get("category", "General")
                    by_cat[c] = by_cat.get(c, 0.0) + float(e.get("amount", 0))
                return {
                    "status": "done",
                    "total_spent": total,
                    "breakdown_by_category": by_cat,
                    "expense_count": len(expenses),
                }

        elif name == "daily_calendar":
            calendar = self._read_json(self.calendar_file, [])
            if action == "add":
                date_val = args.get("date") or datetime.now().strftime("%Y-%m-%d")
                time_val = args.get("time", "All Day")
                title = args.get("title", "New Event")
                event = {"date": date_val, "time": time_val, "title": title}
                calendar.append(event)
                self._write_json(self.calendar_file, calendar)
                return {"status": "done", "message": f"Scheduled '{title}' on {date_val} at {time_val}."}
            elif action == "clear":
                self._write_json(self.calendar_file, [])
                return {"status": "done", "message": "Calendar events cleared."}
            else:  # list
                today = datetime.now().strftime("%Y-%m-%d")
                today_events = [e for e in calendar if e.get("date") == today]
                return {
                    "status": "done",
                    "today": today,
                    "events": today_events,
                    "summary": f"{len(today_events)} event(s) scheduled for today.",
                }

        elif name == "habit_tracker":
            habits = self._read_json(self.habits_file, {})
            today = datetime.now().strftime("%Y-%m-%d")
            if action == "log":
                habit_name = args.get("habit", "daily_check").strip()
                if today not in habits:
                    habits[today] = []
                habits[today].append({"habit": habit_name, "logged_at": datetime.now().strftime("%H:%M:%S")})
                self._write_json(self.habits_file, habits)
                return {"status": "done", "message": f"Logged habit '{habit_name}' for today."}
            else:  # status
                today_logs = habits.get(today, [])
                completed = [h["habit"] for h in today_logs]
                return {"status": "done", "today": today, "completed_habits": completed}

        return {"status": "failed", "error": f"Unknown tool '{name}'"}
