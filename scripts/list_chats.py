#!/usr/bin/env python3
"""List ChatGPT chats from sidebar.

Usage:
    python scripts/list_chats.py              # list visible chats
    python scripts/list_chats.py --all        # scroll to get all chats
    python scripts/list_chats.py --port 9222  # use existing browser
"""

import argparse
import asyncio
import json

from nodriver_kit.core import connect_browser, get_active_tab
from nodriver_kit.tools import browser_start, ax_tree


def _extract_chats(tree: list) -> list[dict]:
    """Extract chat items from accessibility tree."""
    chats = []
    for el in tree:
        if el.get("role") == "link":
            name = el.get("name", "")
            if "Open conversation options" in name:
                title = name.replace(" Open conversation options", "")
                chats.append({
                    "title": title,
                    "node_id": int(el.get("_nodeId"))
                })
    return chats


async def list_chats(port: int = None, limit: int = 20, all_chats: bool = False) -> list[dict]:
    """List chats from sidebar.

    Args:
        port: If provided, connect to existing browser
        limit: Maximum number of chats to return (ignored if all_chats=True)
        all_chats: If True, scroll to load all chats

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

    if not all_chats:
        # Quick mode: just get visible chats
        tree = await ax_tree(tab, interactable_only=True)
        chats = _extract_chats(tree)
        return chats[:limit]

    # Scroll mode: scroll sidebar to load all chats
    seen_titles = set()
    all_results = []
    no_new_count = 0

    for _ in range(200):  # max 200 scroll attempts
        tree = await ax_tree(tab, interactable_only=True)
        chats = _extract_chats(tree)

        new_count = 0
        for chat in chats:
            if chat["title"] not in seen_titles:
                seen_titles.add(chat["title"])
                all_results.append(chat)
                new_count += 1

        if new_count == 0:
            no_new_count += 1
            if no_new_count >= 5:
                # No new chats for 5 consecutive scrolls, we've reached the end
                break
        else:
            no_new_count = 0

        # Scroll sidebar to bottom
        try:
            await tab.evaluate("""
                (() => {
                    const nav = document.querySelector('nav');
                    if (nav) nav.scrollTop = nav.scrollHeight;
                })()
            """)
        except Exception:
            pass

        # Wait for content to load
        await tab.sleep(2)

    return all_results


async def main():
    parser = argparse.ArgumentParser(description="List ChatGPT chats")
    parser.add_argument("--port", "-p", type=int, help="Connect to existing browser")
    parser.add_argument("--limit", "-n", type=int, default=20, help="Max chats to list")
    parser.add_argument("--all", "-a", action="store_true", help="Scroll to get all chats")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    chats = await list_chats(port=args.port, limit=args.limit, all_chats=args.all)

    if args.json:
        print(json.dumps(chats, ensure_ascii=False, indent=2))
    else:
        for i, chat in enumerate(chats, 1):
            print(f"{i}. {chat['title']}")
        print(f"\nTotal: {len(chats)} chats")


if __name__ == "__main__":
    asyncio.run(main())
