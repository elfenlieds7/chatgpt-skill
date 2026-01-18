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
import time
from pathlib import Path

from nodriver_kit.core import (
    launch_chrome,
    connect_browser,
    get_active_tab,
    get_available_port,
)
from nodriver_kit.tools import goto, snapshot

PROFILE_DIR = Path.home() / ".nodriver-kit" / "profiles" / "chatgpt"


async def list_chats(limit: int = 20) -> list[dict]:
    """List recent chats from sidebar.

    Args:
        limit: Maximum number of chats to return

    Returns:
        List of {"title": str, "ref": str} dicts
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

        # Get accessibility tree snapshot
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

        return chats

    finally:
        process.terminate()


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
