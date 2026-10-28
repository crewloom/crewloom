#!/usr/bin/env python3
"""Comprehensive test suite for Crewloom Claude Computer Use Engine."""
import base64
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
try:
    import computer_use as cu
except ModuleNotFoundError:
    import scripts.computer_use as cu


class ClaudeComputerUseSchemaTest(unittest.TestCase):
    """Test compliance with Anthropic Claude Computer Use tool schema."""

    def test_tool_definition_anthropic_format(self):
        tool_def = cu.get_tool_definition(width=1920, height=1080, display=1)
        self.assertEqual(tool_def["type"], "computer_20241022")
        self.assertEqual(tool_def["name"], "computer")
        self.assertEqual(tool_def["display_width_px"], 1920)
        self.assertEqual(tool_def["display_height_px"], 1080)
        self.assertEqual(tool_def["display_number"], 1)

    def test_tool_input_schema(self):
        schema = cu.get_tool_input_schema()
        self.assertEqual(schema["type"], "object")
        self.assertIn("action", schema["required"])
        self.assertIn("mouse_move", schema["properties"]["action"]["enum"])
        self.assertIn("left_click", schema["properties"]["action"]["enum"])
        self.assertIn("create_tab", schema["properties"]["action"]["enum"])
        self.assertIn("list_tabs", schema["properties"]["action"]["enum"])
        self.assertIn("coordinate", schema["properties"])
        self.assertIn("active", schema["properties"])


class ComputerUseEngineTest(unittest.TestCase):
    """Test engine actions and validation."""

    def setUp(self):
        self.engine = cu.ComputerUseEngine(width=1280, height=800)

    def test_coordinate_validation(self):
        self.assertEqual(self.engine.validate_coordinate([100, 200]), (100, 200))
        self.assertEqual(self.engine.validate_coordinate((0, 0)), (0, 0))
        self.assertEqual(self.engine.validate_coordinate([1280, 800]), (1280, 800))

        with self.assertRaises(ValueError):
            self.engine.validate_coordinate([1281, 400])
        with self.assertRaises(ValueError):
            self.engine.validate_coordinate([-1, 400])
        with self.assertRaises(ValueError):
            self.engine.validate_coordinate([100])

    def test_mouse_move_and_cursor_position(self):
        res = self.engine.execute({"action": "mouse_move", "coordinate": [350, 450]})
        self.assertTrue(res["ok"])
        self.assertEqual(res["coordinate"], [350, 450])

        pos_res = self.engine.execute({"action": "cursor_position"})
        self.assertTrue(pos_res["ok"])
        self.assertEqual(pos_res["coordinate"], [350, 450])

    def test_click_actions(self):
        for click_type in ["left_click", "right_click", "double_click", "triple_click", "middle_click"]:
            res = self.engine.execute({"action": click_type, "coordinate": [500, 300]})
            self.assertTrue(res["ok"])
            self.assertEqual(res["action"], click_type)
            self.assertEqual(res["coordinate"], [500, 300])

    def test_left_click_drag(self):
        self.engine.execute({"action": "mouse_move", "coordinate": [100, 100]})
        drag_res = self.engine.execute({"action": "left_click_drag", "coordinate": [400, 500]})
        self.assertTrue(drag_res["ok"])
        self.assertEqual(drag_res["start"], [100, 100])
        self.assertEqual(drag_res["end"], [400, 500])

    def test_type_and_key_actions(self):
        type_res = self.engine.execute({"action": "type", "text": "Crewloom Computer Use Engine"})
        self.assertTrue(type_res["ok"])
        self.assertEqual(type_res["text"], "Crewloom Computer Use Engine")
        self.assertEqual(type_res["length"], 28)

        key_res = self.engine.execute({"action": "key", "text": "Return"})
        self.assertTrue(key_res["ok"])
        self.assertEqual(key_res["key"], "Return")

        with self.assertRaises(ValueError):
            self.engine.execute({"action": "type", "text": 123})
        with self.assertRaises(ValueError):
            self.engine.execute({"action": "key", "text": ""})

    def test_scroll_action(self):
        scroll_res = self.engine.execute({"action": "scroll", "direction": "down", "amount": 600})
        self.assertTrue(scroll_res["ok"])
        self.assertEqual(scroll_res["direction"], "down")
        self.assertEqual(scroll_res["amount"], 600)

        with self.assertRaises(ValueError):
            self.engine.execute({"action": "scroll", "direction": "diagonal"})

    def test_screenshot_action(self):
        shot_res = self.engine.execute({"action": "screenshot"})
        self.assertTrue(shot_res["ok"])
        self.assertTrue(shot_res["dataUrl"].startswith("data:image/svg+xml;base64,"))
        self.assertEqual(shot_res["dimensions"], [1280, 800])

    def test_chrome_tab_group_and_background_browsing(self):
        # 1. Create background tab for chat-session-1 (active defaults to False!)
        t1 = self.engine.execute({
            "action": "create_tab",
            "url": "https://crewloom.dev/docs",
            "chatId": "chat-session-1",
            "chatTitle": "Research Documentation",
        })
        self.assertTrue(t1["ok"])
        self.assertFalse(t1["active"])
        self.assertFalse(t1["tab"]["active"])
        group_id_1 = t1["groupId"]

        # 2. Create another tab in the same chat session -> should join same group
        t2 = self.engine.execute({
            "action": "create_tab",
            "url": "https://crewloom.dev/api",
            "chatId": "chat-session-1",
        })
        self.assertTrue(t2["ok"])
        self.assertEqual(t2["groupId"], group_id_1)

        # 3. Create tab for different chat session -> should have separate group
        t3 = self.engine.execute({
            "action": "create_tab",
            "url": "https://github.com/crewloom",
            "chatId": "chat-session-2",
        })
        self.assertTrue(t3["ok"])
        self.assertNotEqual(t3["groupId"], group_id_1)

        # 4. List tabs filtered by chat session
        tabs_chat_1 = self.engine.execute({"action": "list_tabs", "chatId": "chat-session-1"})
        self.assertTrue(tabs_chat_1["ok"])
        self.assertEqual(len(tabs_chat_1["tabs"]), 2)

        # 5. Navigate tab without focus stealing
        nav = self.engine.execute({
            "action": "navigate",
            "tabId": t1["tab"]["id"],
            "url": "https://crewloom.dev/guides",
            "active": False,
        })
        self.assertTrue(nav["ok"])
        self.assertEqual(nav["tab"]["url"], "https://crewloom.dev/guides")
        self.assertFalse(nav["tab"]["active"])

        # 6. Close tab
        close_res = self.engine.execute({"action": "close_tab", "tabId": t1["tab"]["id"]})
        self.assertTrue(close_res["ok"])
        tabs_after_close = self.engine.execute({"action": "list_tabs", "chatId": "chat-session-1"})
        self.assertEqual(len(tabs_after_close["tabs"]), 1)

    def test_indexed_actions(self):
        idx_res = self.engine.execute({"action": "index"})
        self.assertTrue(idx_res["ok"])
        self.assertGreaterEqual(idx_res["count"], 1)

        click_res = self.engine.execute({"action": "click_index", "index": 1})
        self.assertTrue(click_res["ok"])
        self.assertEqual(click_res["index"], 1)

        type_res = self.engine.execute({"action": "type_index", "index": 2, "text": "agent input", "submit": True})
        self.assertTrue(type_res["ok"])
        self.assertTrue(type_res["submit"])

        content_res = self.engine.execute({"action": "extract_page_content"})
        self.assertTrue(content_res["ok"])
        self.assertIn("Crewloom", content_res["content"])


if __name__ == "__main__":
    unittest.main()
