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

## Features

- [ ] list_chats - List conversations from sidebar
- [ ] send_message - Send a message in current chat
- [ ] new_chat - Start a new conversation
- [ ] get_response - Get the latest assistant response

## Exploration Notes

### Sidebar Structure (2026-01-18)

Sidebar sections:
- Apps, Codex, GPTs (links)
- **Projects** (button, expandable) - contains project links
- **Group chats** (button, expandable) - contains group chat links
- **Your chats** (button, expandable) - contains personal chat links

Each chat in "Your chats" is a link with:
- `role: 'link'`
- `name: '{chat_title} Open conversation options'`

Example chats found:
```
{'role': 'link', 'name': '猫与Tom的相似性 Open conversation options'}
{'role': 'link', 'name': '猫咪舔毛行为分析 Open conversation options'}
```

### Selectors

```python
# Your chats section button
your_chats_btn = await tab.find("Your chats")

# Individual chat links (under Your chats)
# Pattern: link name ends with "Open conversation options"
chats = [el for el in elements if el['role'] == 'link' and 'Open conversation options' in el.get('name', '')]
```

## Implementation

```python
import asyncio
import nodriver as uc
from pathlib import Path

PROFILE_DIR = Path.home() / ".nodriver-kit" / "profiles" / "chatgpt"

async def list_chats(limit: int = 20) -> list[dict]:
    """List recent chats from sidebar.

    Returns:
        List of {"title": str, "ref": str} dicts
    """
    browser = await uc.start(
        headless=False,
        user_data_dir=str(PROFILE_DIR)
    )
    tab = await browser.get("https://chatgpt.com")
    await tab.sleep(3)

    from nodriver_kit.tools import snapshot
    elements = await snapshot(tab)

    chats = []
    for el in elements:
        if el.get('role') == 'link':
            name = el.get('name', '')
            if 'Open conversation options' in name:
                title = name.replace(' Open conversation options', '')
                chats.append({
                    'title': title,
                    'ref': el.get('ref')
                })
                if len(chats) >= limit:
                    break

    browser.stop()
    return chats
```
