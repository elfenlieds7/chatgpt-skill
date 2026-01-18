#!/usr/bin/env python3
"""List ChatGPT chats from sidebar.

Usage:
    python scripts/list_chats.py [--limit N]

Example:
    python scripts/list_chats.py --limit 10
"""

import argparse
import asyncio
import json
from pathlib import Path

import nodriver as uc

PROFILE_DIR = Path.home() / ".nodriver-kit" / "profiles" / "chatgpt"


async def list_chats(limit: int = 20) -> list[dict]:
    """List recent chats from sidebar.

    Args:
        limit: Maximum number of chats to return

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
        if el.get("role") == "link":
            name = el.get("name", "")
            if "Open conversation options" in name:
                title = name.replace(" Open conversation options", "")
                chats.append({
                    "title": title,
                    "ref": el.get("ref")
                })
                if len(chats) >= limit:
                    break

    browser.stop()
    return chats


async def main():
    parser = argparse.ArgumentParser(description="List ChatGPT chats")
    parser.add_argument("--limit", "-n", type=int, default=20, help="Max chats to list")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    chats = await list_chats(args.limit)

    if args.json:
        print(json.dumps(chats, ensure_ascii=False, indent=2))
    else:
        for i, chat in enumerate(chats, 1):
            print(f"{i}. {chat['title']}")
        print(f"\nTotal: {len(chats)} chats")


if __name__ == "__main__":
    asyncio.run(main())
