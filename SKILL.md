---
name: chatgpt-skill
description: Browser automation for ChatGPT. Use when automating ChatGPT interactions: listing chats, sending messages, creating new conversations, etc.
---

# ChatGPT Skill

Browser automation for ChatGPT using nodriver-kit.

## Prerequisites

Login first to save session:
```bash
python -m nodriver_kit.tools.login_interactive --url "https://chatgpt.com" --profile chatgpt
```

## Scripts

### list_chats

List conversations from sidebar.

```bash
python scripts/list_chats.py [--limit N] [--json]
```

## Exploration Notes

### Sidebar Structure

- **Your chats** section contains chat links
- Each chat link has name pattern: `{title} Open conversation options`
- Use `nodriver_kit.tools.snapshot` to get all elements, filter by role='link'
