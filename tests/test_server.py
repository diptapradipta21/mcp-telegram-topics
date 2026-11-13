#!/usr/bin/env python3
import json
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import server

class TestTelegramTopicsMCP(unittest.TestCase):
    def setUp(self):
        self.env_patcher = patch.dict("os.environ", {
            "TELEGRAM_BOT_TOKEN": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
            "TELEGRAM_CHAT_ID": "-1001234567890"
        })
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    def test_get_config_success(self):
        token, chat_id = server.get_config()
        self.assertEqual(token, "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
        self.assertEqual(chat_id, "-1001234567890")

    def test_get_config_missing_raises_value_error(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ValueError):
                server.get_config()

    @patch("urllib.request.urlopen")
    def test_send_topic_message_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"ok": True, "result": {"message_id": 999}}).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = server.send_topic_message(141, "Hello from test")
        self.assertIn("Successfully sent message (ID: 999)", res)
        self.assertIn("141", res)

    @patch("urllib.request.urlopen")
    def test_create_forum_topic_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"ok": True, "result": {"message_thread_id": 42}}).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = server.create_forum_topic("Ops Room")
        self.assertIn("Created topic 'Ops Room' with thread ID 42", res)

    @patch("urllib.request.urlopen")
    def test_close_and_reopen_forum_topic(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"ok": True, "result": True}).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        close_res = server.close_forum_topic(42)
        self.assertIn("Topic thread 42 closed", close_res)

        reopen_res = server.reopen_forum_topic(42)
        self.assertIn("Topic thread 42 reopened", reopen_res)

    @patch("urllib.request.urlopen")
    def test_delete_forum_topic(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"ok": True, "result": True}).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = server.delete_forum_topic(42)
        self.assertIn("Topic thread 42 permanently deleted", res)

    @patch("urllib.request.urlopen")
    def test_pin_and_unpin_topic_message(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"ok": True, "result": True}).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        pin_res = server.pin_topic_message(42, 1001)
        self.assertIn("Message 1001 successfully pinned", pin_res)

        unpin_res = server.unpin_all_topic_messages(42)
        self.assertIn("All messages unpinned in topic thread 42", unpin_res)

    @patch("urllib.request.urlopen")
    def test_edit_forum_topic(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"ok": True, "result": True}).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = server.edit_forum_topic(42, name="Renamed Topic")
        self.assertIn("Topic thread 42 updated successfully", res)

    def test_list_registered_topics(self):
        with patch.dict("os.environ", {"TELEGRAM_TOPIC_MAP": json.dumps({"WarRoom": 141, "CBSI": 827})}):
            res = server.list_registered_topics()
            self.assertIn("WarRoom: Thread ID 141", res)
            self.assertIn("CBSI: Thread ID 827", res)

        with patch.dict("os.environ", {"TELEGRAM_TOPIC_MAP": ""}):
            res = server.list_registered_topics()
            self.assertIn("No predefined topic mappings", res)

    def test_tool_annotations_declared(self):
        if hasattr(server.app, "list_tools"):
            import asyncio
            tools = asyncio.run(server.app.list_tools())
            self.assertEqual(len(tools), 10)
            for t in tools:
                ann = t.annotations
                assert ann is not None, f"{t.name} missing annotations"
                dumped = ann.model_dump(by_alias=True)
                for hint in ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"):
                    self.assertIsInstance(dumped.get(hint), bool, f"{t.name}.{hint} must be bool")

    @patch("urllib.request.urlopen")
    def test_check_bot_health_success(self, mock_urlopen):
        mock_me = MagicMock()
        mock_me.read.return_value = json.dumps({"ok": True, "result": {"username": "HermesBot"}}).encode("utf-8")
        mock_me.__enter__.return_value = mock_me

        mock_chat = MagicMock()
        mock_chat.read.return_value = json.dumps({"ok": True, "result": {"title": "HQ Group", "is_forum": True}}).encode("utf-8")
        mock_chat.__enter__.return_value = mock_chat

        mock_urlopen.side_effect = [mock_me, mock_chat]

        res = server.check_bot_health()
        self.assertIn("Bot Healthy: @HermesBot", res)
        self.assertIn("HQ Group", res)
        self.assertIn("Forum Enabled: True", res)

    @patch("urllib.request.urlopen")
    def test_check_bot_health_auth_failure(self, mock_urlopen):
        mock_me = MagicMock()
        mock_me.read.return_value = json.dumps({"ok": False, "error": "Unauthorized"}).encode("utf-8")
        mock_me.__enter__.return_value = mock_me
        mock_urlopen.return_value = mock_me

        res = server.check_bot_health()
        self.assertIn("Bot auth failure: Unauthorized", res)

if __name__ == "__main__":

    unittest.main()
