#!/usr/bin/env python3
"""Open a ChatGPT conversation by fuzzy matching title.

Usage:
    python scripts/open_chat.py "猫"
    python scripts/open_chat.py "Tom" --exact
"""

import argparse
import asyncio
from pathlib import Path

import nodriver as uc

PROFILE_DIR = Path.home() / ".nodriver-kit" / "profiles" / "chatgpt"


async def open_chat(query: str, exact: bool = False) -> dict:
    """Open a chat by matching title.

    Args:
        query: Search string to match against chat titles
        exact: If True, require exact match; otherwise fuzzy match

    Returns:
        {"success": bool, "title": str or None, "error": str or None}
    """
    browser = await uc.start(
        headless=False,
        user_data_dir=str(PROFILE_DIR)
    )
    tab = await browser.get("https://chatgpt.com")
    await tab.sleep(3)

    from nodriver_kit.tools import snapshot
    elements = await snapshot(tab)

    # Find matching chat
    matched_chat = None
    matched_title = None

    for el in elements:
        if el.get("role") == "link":
            name = el.get("name", "")
            if "Open conversation options" in name:
                title = name.replace(" Open conversation options", "")

                if exact:
                    if query == title:
                        matched_chat = el
                        matched_title = title
                        break
                else:
                    # Fuzzy match: query is substring of title (case-insensitive)
                    if query.lower() in title.lower():
                        matched_chat = el
                        matched_title = title
                        break

    if not matched_chat:
        browser.stop()
        return {"success": False, "title": None, "error": f"No chat matching '{query}'"}

    # Click the chat link using ref
    ref = matched_chat.get("ref")
    if ref:
        # Find element by text (the title part)
        chat_link = await tab.find(matched_title, best_match=True)
        if chat_link:
            await chat_link.click()
            await tab.sleep(2)
            browser.stop()
            return {"success": True, "title": matched_title, "error": None}

    browser.stop()
    return {"success": False, "title": matched_title, "error": "Could not click chat"}


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
