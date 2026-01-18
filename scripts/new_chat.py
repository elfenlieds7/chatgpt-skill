#!/usr/bin/env python3
"""Start a new ChatGPT conversation.

Usage:
    python scripts/new_chat.py
"""

import asyncio
import time
from pathlib import Path

from nodriver_kit.core import (
    launch_chrome,
    connect_browser,
    get_active_tab,
    get_available_port,
)
from nodriver_kit.tools import goto, click

PROFILE_DIR = Path.home() / ".nodriver-kit" / "profiles" / "chatgpt"


async def new_chat() -> dict:
    """Start a new chat.

    Returns:
        {"success": bool, "url": str or None, "chat_id": str or None}
    """
    # Start Chrome with saved profile (includes session-restore suppression)
    port = get_available_port()
    process = launch_chrome(port=port, user_data_dir=str(PROFILE_DIR))

    # Wait for Chrome to be ready
    time.sleep(2)

    try:
        browser = await connect_browser(port=port)
        tab = await get_active_tab(browser)

        # Navigate to ChatGPT
        await goto(tab, "https://chatgpt.com")
        await asyncio.sleep(2)

        # Click "New chat" button using stable data-testid selector
        result = await click(tab, selector='a[data-testid="create-new-chat-button"]')
        if result.get("error"):
            return {"success": False, "url": None, "chat_id": None}

        # Wait for URL to change to /c/{chat_id}
        for _ in range(10):
            await asyncio.sleep(0.5)
            url = tab.target.url
            if "/c/" in url:
                chat_id = url.split("/c/")[-1].split("?")[0]
                return {"success": True, "url": url, "chat_id": chat_id}

        # URL didn't change to chat format, but new chat may still work
        return {"success": True, "url": tab.target.url, "chat_id": None}

    finally:
        process.terminate()


async def main():
    result = await new_chat()
    if result["success"]:
        print(f"URL: {result['url']}")
        if result["chat_id"]:
            print(f"Chat ID: {result['chat_id']}")
    else:
        print("Failed to start new chat")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
