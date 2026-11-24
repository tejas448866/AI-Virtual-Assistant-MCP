"""
Unit tests for SafetyGate ("Less Magic, More Utility").
"""
import unittest
from mcp.safety_gate import SafetyGate, ConfirmationLevel


class TestSafetyGate(unittest.TestCase):
    def setUp(self):
        self.gate = SafetyGate()

    def test_safe_operations(self):
        level = self.gate.classify_action("daily_calendar", {"action": "list"})
        self.assertEqual(level, ConfirmationLevel.SAFE)

        allowed, _ = self.gate.evaluate("mcp_daily_notes", {"action": "search", "query": "meeting"})
        self.assertTrue(allowed)

    def test_critical_operations(self):
        level = self.gate.classify_action("system_control_shutdown", {})
        self.assertEqual(level, ConfirmationLevel.CRITICAL)

        # Without user confirmation callback, it should block
        allowed, reason = self.gate.evaluate("send_message", {"recipient": "boss", "text": "I resign"})
        self.assertFalse(allowed)
        self.assertIn("explicit confirmation", reason)

    def test_critical_with_user_agreement(self):
        def user_approves(prompt):
            return True

        allowed, reason = self.gate.evaluate("send_email", {"subject": "Hello"}, confirm_callback=user_approves)
        self.assertTrue(allowed)
        self.assertIn("confirmed", reason)


if __name__ == "__main__":
    unittest.main()
