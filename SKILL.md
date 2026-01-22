---
name: chatgpt
description: "Browser automation for ChatGPT. Use when user wants to: (1) list/search ChatGPT conversations, (2) send messages to ChatGPT, (3) create/open/delete chats, (4) download chat history."
---

# ChatGPT Skill

Browser automation for ChatGPT using ai-dev-browser.

## Setup (One-Time)

```bash
python -m ai_dev_browser.tools.login_interactive --url "https://chatgpt.com" --profile chatgpt
```

## Send Message

```bash
python scripts/send_message.py "your message"
python scripts/send_message.py "your message" --no-wait  # don't wait for response
```

## List Chats

```bash
python scripts/list_chats.py
python scripts/list_chats.py --limit 20 --json
```

## Open Chat

```bash
python scripts/open_chat.py "猫"              # fuzzy match
python scripts/open_chat.py "猫与Tom" --exact  # exact match
```

## New Chat

```bash
python scripts/new_chat.py
```

## Delete Chat

```bash
python scripts/delete_chat.py  # delete current chat
```

## Download Chat

```bash
python scripts/download_chat.py              # download current chat
python scripts/download_chat.py --json       # JSON format
```
