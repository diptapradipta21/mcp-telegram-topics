#!/usr/bin/env python3
"""
mcp-telegram-topics — Model Context Protocol (MCP) Server for Telegram Forum Topics.
Enables Claude Desktop, Claude Code, and Anthropic AI agents to create, route, and manage Telegram supergroup forum threads.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from typing import Optional
try:
    from mcp.server.mcpserver import MCPServer
    app = MCPServer("telegram-topics-mcp")
except ImportError:
    class DummyMCPServer:
        """Fallback lightweight mock when mcp package is not installed."""
        def __init__(self, name: str = ""):
            self.name = name

        def tool(self):
            def decorator(fn):
                return fn
            return decorator

        def run(self, **kwargs):
            raise RuntimeError("mcp package is not installed. Install with 'pip install mcp'.")

    app = DummyMCPServer("telegram-topics-mcp")

def get_config():
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID environment variables.")
    return bot_token, chat_id

def make_telegram_request(endpoint: str, payload: dict) -> dict:
    bot_token, _ = get_config()
    url = f"https://api.telegram.org/bot{bot_token}/{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        try:
            parsed = json.loads(err_msg)
            return {"ok": False, "error": parsed.get("description", err_msg)}
        except Exception:
            return {"ok": False, "error": err_msg}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.tool()
def send_topic_message(thread_id: int, message: str, parse_mode: str = "Markdown") -> str:
    """
    Send a message or notification to a specific Telegram forum topic thread.
    
    Args:
        thread_id: The target forum topic message_thread_id.
        message: The text content to post (supports Markdown formatting).
        parse_mode: Formatting parser (default 'Markdown', or 'HTML', or 'None').
    """
    _, chat_id = get_config()
    payload = {
        "chat_id": chat_id,
        "message_thread_id": thread_id,
        "text": message
    }
    if parse_mode and parse_mode.lower() != "none":
        payload["parse_mode"] = parse_mode

    res = make_telegram_request("sendMessage", payload)
    if res.get("ok"):
        msg_id = res["result"]["message_id"]
        return f"Successfully sent message (ID: {msg_id}) to topic thread {thread_id}."
    return f"Failed to send message: {res.get('error', 'Unknown error')}"

@app.tool()
def create_forum_topic(name: str, icon_color: int = 7322096, icon_custom_emoji_id: Optional[str] = None) -> str:
    """
    Create a new forum topic in the configured Telegram Supergroup.
    
    Args:
        name: Name/Title of the topic (1 to 128 characters).
        icon_color: Decimal RGB color code for topic icon (default 7322096 / light blue).
                    Colors: Blue (7322096), Amber (16775294), Emerald (9367192), Red (16766590), Purple (13338331).
        icon_custom_emoji_id: Optional Telegram custom emoji identifier.
    """
    _, chat_id = get_config()
    payload = {
        "chat_id": chat_id,
        "name": name,
        "icon_color": icon_color
    }
    if icon_custom_emoji_id:
        payload["icon_custom_emoji_id"] = icon_custom_emoji_id

    res = make_telegram_request("createForumTopic", payload)
    if res.get("ok"):
        thread_id = res["result"]["message_thread_id"]
        return f"Created topic '{name}' with thread ID {thread_id}."
    return f"Failed to create topic: {res.get('error', 'Unknown error')}"

@app.tool()
def edit_forum_topic(thread_id: int, name: Optional[str] = None, icon_custom_emoji_id: Optional[str] = None) -> str:
    """
    Rename an existing forum topic or change its icon.
    
    Args:
        thread_id: The target forum topic message_thread_id.
        name: New title for the topic.
        icon_custom_emoji_id: New custom emoji ID for the icon.
    """
    _, chat_id = get_config()
    payload = {"chat_id": chat_id, "message_thread_id": thread_id}
    if name:
        payload["name"] = name
    if icon_custom_emoji_id:
        payload["icon_custom_emoji_id"] = icon_custom_emoji_id

    res = make_telegram_request("editForumTopic", payload)
    if res.get("ok"):
        return f"Topic thread {thread_id} updated successfully."
    return f"Failed to edit topic: {res.get('error', 'Unknown error')}"

@app.tool()
def close_forum_topic(thread_id: int) -> str:
    """
    Close an active forum topic (marks it as completed/archived).
    
    Args:
        thread_id: The target forum topic message_thread_id.
    """
    _, chat_id = get_config()
    res = make_telegram_request("closeForumTopic", {"chat_id": chat_id, "message_thread_id": thread_id})
    if res.get("ok"):
        return f"Topic thread {thread_id} closed."
    return f"Failed to close topic: {res.get('error', 'Unknown error')}"

@app.tool()
def reopen_forum_topic(thread_id: int) -> str:
    """
    Reopen a previously closed forum topic.
    
    Args:
        thread_id: The target forum topic message_thread_id.
    """
    _, chat_id = get_config()
    res = make_telegram_request("reopenForumTopic", {"chat_id": chat_id, "message_thread_id": thread_id})
    if res.get("ok"):
        return f"Topic thread {thread_id} reopened."
    return f"Failed to reopen topic: {res.get('error', 'Unknown error')}"

@app.tool()
def delete_forum_topic(thread_id: int) -> str:
    """
    Permanently delete a forum topic and all its messages.
    
    Args:
        thread_id: The target forum topic message_thread_id to delete.
    """
    _, chat_id = get_config()
    res = make_telegram_request("deleteForumTopic", {"chat_id": chat_id, "message_thread_id": thread_id})
    if res.get("ok"):
        return f"Topic thread {thread_id} permanently deleted."
    return f"Failed to delete topic: {res.get('error', 'Unknown error')}"

@app.tool()
def pin_topic_message(thread_id: int, message_id: int, disable_notification: bool = False) -> str:
    """
    Pin a key message within a forum topic thread.
    
    Args:
        thread_id: The forum topic message_thread_id.
        message_id: The message ID to pin.
        disable_notification: If True, pin silently without notifying members.
    """
    _, chat_id = get_config()
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "disable_notification": disable_notification
    }
    res = make_telegram_request("pinChatMessage", payload)
    if res.get("ok"):
        return f"Message {message_id} successfully pinned in topic thread {thread_id}."
    return f"Failed to pin message: {res.get('error', 'Unknown error')}"

@app.tool()
def unpin_all_topic_messages(thread_id: int) -> str:
    """
    Clear and unpin all pinned messages inside a forum topic.
    
    Args:
        thread_id: The forum topic message_thread_id.
    """
    _, chat_id = get_config()
    res = make_telegram_request("unpinAllForumTopicMessages", {"chat_id": chat_id, "message_thread_id": thread_id})
    if res.get("ok"):
        return f"All messages unpinned in topic thread {thread_id}."
    return f"Failed to unpin messages: {res.get('error', 'Unknown error')}"

@app.tool()
def list_registered_topics() -> str:
    """
    List known topic mappings from TELEGRAM_TOPIC_MAP environment variable (if configured).
    Helpful for Claude to route messages by division name rather than raw ID.
    """
    topic_map_raw = os.environ.get("TELEGRAM_TOPIC_MAP", "").strip()
    if not topic_map_raw or topic_map_raw == "{}":
        return "No predefined topic mappings configured in TELEGRAM_TOPIC_MAP. Use integer thread_ids directly."
    try:
        mapping = json.loads(topic_map_raw)
        if not mapping:
            return "No predefined topic mappings configured in TELEGRAM_TOPIC_MAP. Use integer thread_ids directly."
        formatted = [f"- {name}: Thread ID {tid}" for name, tid in mapping.items()]
        return "Registered Topic Routing:\n" + "\n".join(formatted)
    except Exception as e:
        return f"Error parsing TELEGRAM_TOPIC_MAP: {e}"

if __name__ == "__main__":
    app.run(transport="stdio")
