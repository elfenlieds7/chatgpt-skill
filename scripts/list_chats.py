#!/usr/bin/env python3
"""List ChatGPT chats from sidebar.

Usage:
    python scripts/list_chats.py [--limit N]
    python scripts/list_chats.py --port 9222  # use existing browser
"""

import argparse
import asyncio
import json

from nodriver_kit.core import connect_browser, get_active_tab
from nodriver_kit.tools import browser_start, ax_tree


async def list_chats(port: int = None, limit: int = 20) -> list[dict]:
    """List recent chats from sidebar.

    Args:
        port: If provided, connect to existing browser
        limit: Maximum number of chats to return

    Returns:
        List of {"title": str, "node_id": int} dicts
    """
    if port is None:
        result = browser_start(url="https://chatgpt.com")
        if "error" in result:
            return []
        port = result["port"]

    browser = await connect_browser(port=port)
    tab = await get_active_tab(browser)
    await tab.sleep(2)

    # Get accessibility tree
    tree = await ax_tree(tab, interactable_only=True)

    chats = []
    for el in tree:
        if el.get("role") == "link":
            name = el.get("name", "")
            # Chat links have "Open conversation options" suffix
            if "Open conversation options" in name:
                title = name.replace(" Open conversation options", "")
                chats.append({
                    "title": title,
                    "node_id": int(el.get("_nodeId"))
                })
                if len(chats) >= limit:
                    break

    return chats


async def main():
    parser = argparse.ArgumentParser(description="List ChatGPT chats")
    parser.add_argument("--port", "-p", type=int, help="Connect to existing browser")
    parser.add_argument("--limit", "-n", type=int, default=20, help="Max chats to list")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    chats = await list_chats(port=args.port, limit=args.limit)

    if args.json:
        print(json.dumps(chats, ensure_ascii=False, indent=2))
    else:
        for i, chat in enumerate(chats, 1):
            print(f"{i}. {chat['title']}")
        print(f"\nTotal: {len(chats)} chats")


if __name__ == "__main__":
    asyncio.run(main())
