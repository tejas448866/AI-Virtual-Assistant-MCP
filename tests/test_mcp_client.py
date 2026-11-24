"""
Tests for MCPClient and MCPServerManager orchestration.
"""
import asyncio
import unittest

from mcp.server_manager import MCPServerManager


class TestMCPClientAndManager(unittest.TestCase):
    def test_manager_initialization_and_tool_discovery(self):
        async def run_test():
            manager = MCPServerManager()
            await manager.initialize_all()

            # Verify built-in servers registered
            self.assertIn("daily", manager.clients)
            self.assertIn("desktop", manager.clients)
            self.assertIn("comm", manager.clients)

            # Verify tools exist
            declarations = manager.get_all_tool_declarations()
            self.assertTrue(len(declarations) >= 8)

            names = [d["name"] for d in declarations]
            self.assertIn("mcp_daily_grocery_list", names)
            self.assertIn("mcp_daily_quick_notes", names)
            self.assertIn("mcp_comm_draft_email", names)

            # Test tool execution through manager with safety gate
            exec_res = await manager.execute_tool(
                "mcp_daily_quick_notes",
                {"action": "save", "text": "Testing MCP Manager pipeline"}
            )
            self.assertEqual(exec_res["status"], "done")
            self.assertEqual(exec_res["server"], "daily")

            await manager.shutdown()

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
