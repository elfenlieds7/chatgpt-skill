#!/usr/bin/env python3
"""Open a ChatGPT conversation by fuzzy matching title.

Usage:
    python scripts/open_chat.py "猫"
    python scripts/open_chat.py "Tom" --exact
"""

import argparse
import asyncio
import time
from pathlib import Path

from nodriver_kit.core import (
    launch_chrome,
    connect_browser,
    get_active_tab,
    get_available_port,
)
from nodriver_kit.tools import goto, snapshot, click

PROFILE_DIR = Path.home() / ".nodriver-kit" / "profiles" / "chatgpt"


async def open_chat(query: str, exact: bool = False) -> dict:
    """Open a chat by matching title.

    Args:
        query: Search string to match against chat titles
        exact: If True, require exact match; otherwise fuzzy match

    Returns:
        {"success": bool, "title": str or None, "error": str or None}
    """
    # Start Chrome with saved profile
    port = get_available_port()
    process = launch_chrome(port=port, user_data_dir=str(PROFILE_DIR))

    # Wait for Chrome to be ready
    time.sleep(2)

    try:
        browser = await connect_browser(port=port)
        tab = await get_active_tab(browser)

        # Navigate to ChatGPT
        await goto(tab, "https://chatgpt.com")
        await asyncio.sleep(3)

        # Get accessibility tree to find chats
        elements = await snapshot(tab)

        # Find matching chat
        matched_title = None

        for el in elements:
            if el.get("role") == "link":
                name = el.get("name", "")
                if "Open conversation options" in name:
                    title = name.replace(" Open conversation options", "")

                    if exact:
                        if query == title:
                            matched_title = title
                            break
                    else:
                        # Fuzzy match: query is substring of title (case-insensitive)
                        if query.lower() in title.lower():
                            matched_title = title
                            break

        if not matched_title:
            return {"success": False, "title": None, "error": f"No chat matching '{query}'"}

        # Click the chat using CSS selector with href pattern
        # First get all chat links to find the href for matching title
        chat_links = await tab.select_all('nav a[href^="/c/"]')
        for link in chat_links:
            text = link.text_all or ""
            if matched_title in text:
                await link.click()
                await asyncio.sleep(2)
                return {"success": True, "title": matched_title, "error": None}

        return {"success": False, "title": matched_title, "error": "Could not click chat"}

    finally:
        process.terminate()


async def main():
    parser = argparse.ArgumentParser(description="Open ChatGPT chat by title")
    parser.add_argument("query", help="Search string to match chat title")
    parser.add_argument("--exact", action="store_true", help="Require exact match")
    args = parser.parse_args()

    result = await open_chat(args.query, args.exact)

    if result["success"]:
        print(f"Opened: {result['title']}")
    else:
        print(f"Error: {result['error']}")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
