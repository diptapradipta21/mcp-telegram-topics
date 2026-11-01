# 📡 Telegram Topics MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![MCP Standard](https://img.shields.io/badge/MCP-2.0-orange.svg)](https://modelcontextprotocol.io/)
[![Anthropic Claude](https://img.shields.io/badge/Claude-Desktop%20%26%20Code-purple.svg)](https://claude.ai/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

> **Official Model Context Protocol (MCP) server that empowers Claude Desktop, Claude Code, and autonomous AI agents to seamlessly route alerts, create topics, and manage Telegram supergroup forum threads.**

---

## 💡 Why This Exists
Modern AI workflows run continuous tasks: coding iterations, automated research, data scraping, and daily summaries. 
Routing all agent output into a single Telegram channel creates unreadable noise. 

Telegram **Forum Topics** solve this by creating dedicated sub-threads (e.g., `#engineering`, `#marketing`, `#financial-audits`).
This MCP server gives Claude **native tools** to:
1. **Send targeted updates** directly into the right topic thread (`send_topic_message`).
2. **Create new discussion threads** on the fly for new projects or incident tickets (`create_forum_topic`).
3. **Archive/Close topics** when tasks or sprints are completed (`close_forum_topic`).
4. **Resolve division tags** into specific `thread_id`s automatically (`list_registered_topics`).

---

## 🛠️ Available MCP Tools

| Tool | Parameters | Description |
| :--- | :--- | :--- |
| `send_topic_message` | `thread_id`, `message`, `parse_mode` | Posts formatted Markdown or text into a specific topic thread. |
| `create_forum_topic`| `name`, `icon_color`, `icon_custom_emoji_id` | Spawns a new forum topic in your Telegram supergroup. |
| `edit_forum_topic`  | `thread_id`, `name`, `icon_custom_emoji_id` | Renames a topic or updates its icon. |
| `close_forum_topic` | `thread_id` | Marks a topic as closed/archived. |
| `reopen_forum_topic`| `thread_id` | Reopens a closed forum topic. |
| `delete_forum_topic`| `thread_id` | Permanently deletes a topic and all its messages. |
| `pin_topic_message` | `thread_id`, `message_id`, `disable_notification` | Pins a key message inside a topic thread. |
| `unpin_all_topic_messages` | `thread_id` | Clears all pinned messages inside a topic thread. |
| `list_registered_topics` | *none* | Returns human-readable mapping from `TELEGRAM_TOPIC_MAP`. |

---

## 🚀 Setup & Integration

### 1. Prerequisites
- A Telegram Supergroup with **Topics enabled** (Group Settings → Topics: On).
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather) added as an Administrator in the group with *Manage Topics* permission.
- Your Supergroup Chat ID (e.g., `-100xxxxxxxxxx`).

---

### 2. Integration with Claude Code CLI
Add this MCP server to your Claude Code workspace in one command:

```bash
claude mcp add telegram-topics -- python3 /path/to/server.py
```

Set environment variables in your terminal:
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="-100xxxxxxxxxx"
# Optional topic routing shortcut:
export TELEGRAM_TOPIC_MAP='{"ENGINEERING": 1760, "MARKETING": 137, "GENERAL": 1}'
```

---

### 3. Integration with Claude Desktop
Open your Claude Desktop configuration file:
* **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
* **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add the server under `mcpServers`:

```json
{
  "mcpServers": {
    "telegram-topics": {
      "command": "python3",
      "args": ["/absolute/path/to/mcp-telegram-topics/server.py"],
      "env": {
        "TELEGRAM_BOT_TOKEN": "your_bot_token_here",
        "TELEGRAM_CHAT_ID": "-100xxxxxxxxxx",
        "TELEGRAM_TOPIC_MAP": "{\"DEV\": 1760, \"MARKETING\": 137}"
      }
    }
  }
}
```

Restart Claude Desktop. You will see the hammer icon 🔨 with Telegram tools active!

---

## 💬 Example Prompt in Claude

> *"Claude, analyze the bug in `auth.py`, fix it, and send a completion summary to our Engineering topic thread on Telegram."*

Claude will automatically:
1. Inspect the code and patch the issue.
2. Call `send_topic_message(thread_id=1760, message="✅ Fixed JWT expiration bug in auth.py")`.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
