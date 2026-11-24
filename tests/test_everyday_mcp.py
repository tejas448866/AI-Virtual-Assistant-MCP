"""
Integration tests for built-in Everyday Life MCP Server.
"""
import asyncio
import tempfile
import unittest
from pathlib import Path

from mcp.servers.daily_life_mcp import DailyLifeMCPServer
from mcp.servers.communication_mcp import CommunicationMCPServer


class TestEverydayMCPServers(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.server = DailyLifeMCPServer(storage_dir=Path(self.temp_dir.name))
        self.comm_server = CommunicationMCPServer()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_grocery_list_flow(self):
        async def run_flow():
            # Add items
            res = await self.server.execute_tool("grocery_list", {"action": "add", "items": "Oat Milk, Apples, Bread"})
            self.assertEqual(res["status"], "done")

            # List items
            list_res = await self.server.execute_tool("grocery_list", {"action": "list"})
            self.assertEqual(len(list_res["pending_items"]), 3)
            self.assertIn("Oat Milk", list_res["pending_items"])

            # Check off item
            check_res = await self.server.execute_tool("grocery_list", {"action": "check_off", "items": "Bread"})
            self.assertEqual(check_res["status"], "done")

            # Check remaining
            after_res = await self.server.execute_tool("grocery_list", {"action": "list"})
            self.assertEqual(len(after_res["pending_items"]), 2)
            self.assertEqual(len(after_res["completed_items"]), 1)

        asyncio.run(run_flow())

    def test_quick_notes_flow(self):
        async def run_flow():
            await self.server.execute_tool("quick_notes", {"action": "save", "text": "WiFi password is SuperSecret123"})
            search_res = await self.server.execute_tool("quick_notes", {"action": "search", "query": "WiFi"})
            self.assertEqual(search_res["status"], "done")
            self.assertEqual(search_res["count"], 1)

        asyncio.run(run_flow())

    def test_communication_email_draft(self):
        async def run_flow():
            res = await self.comm_server.execute_tool("draft_email", {
                "recipient_name": "Sarah",
                "subject": "Project Review Sync",
                "key_points": "Let's review the MCP prototype on Thursday morning.",
                "tone": "formal"
            })
            self.assertEqual(res["status"], "done")
            self.assertIn("Dear Sarah", res["body"])
            self.assertIn("MCP prototype", res["body"])

        asyncio.run(run_flow())


if __name__ == "__main__":
    unittest.main()
