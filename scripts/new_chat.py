#!/usr/bin/env python3
"""Start a new ChatGPT conversation.

Usage:
    python scripts/new_chat.py
"""

import asyncio
from pathlib import Path

import nodriver as uc

PROFILE_DIR = Path.home() / ".nodriver-kit" / "profiles" / "chatgpt"


async def new_chat() -> bool:
    """Start a new chat.

    Returns:
        True if successful
    """
    browser = await uc.start(
        headless=False,
        user_data_dir=str(PROFILE_DIR)
    )
    tab = await browser.get("https://chatgpt.com")
    await tab.sleep(2)

    # Find and click "New chat" link
    new_chat_btn = await tab.find("New chat", best_match=True)
    if new_chat_btn:
        await new_chat_btn.click()
        await tab.sleep(1)
        print("New chat started")
        browser.stop()
        return True

    print("Could not find New chat button")
    browser.stop()
    return False


async def main():
    success = await new_chat()
    exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
