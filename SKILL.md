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

### new_chat

Start a new conversation.

```bash
python scripts/new_chat.py
```

### open_chat

Open a chat by fuzzy matching title.

```bash
python scripts/open_chat.py "猫"           # fuzzy match
python scripts/open_chat.py "猫与Tom" --exact  # exact match
```

## Exploration Notes

### Selectors

| Element | Selector | Note |
|---------|----------|------|
| New chat button | `a[data-testid="create-new-chat-button"]` | Stable |
| Sidebar chats | Accessibility name: `{title} Open conversation options` | Use snapshot |

### Sidebar Structure

- **New chat button**: Use CSS selector `data-testid`, not text search
- **Your chats**: links with accessibility name pattern `{title} Open conversation options`
- Use `snapshot()` to list chats, filter by accessibility name
