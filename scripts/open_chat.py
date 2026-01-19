#!/usr/bin/env python3
"""Open a ChatGPT conversation by fuzzy matching title.

Usage:
    python scripts/open_chat.py "猫"
    python scripts/open_chat.py "Tom" --exact
    python scripts/open_chat.py "猫" --port 9222  # use existing browser
"""

import argparse
import asyncio

from nodriver_kit.core import connect_browser, get_active_tab
from nodriver_kit.tools import browser_start, ax_tree, ax_select


async def open_chat(query: str, port: int = None, exact: bool = False) -> dict:
    """Open a chat by matching title.

    Args:
        query: Search string to match against chat titles
        port: If provided, connect to existing browser
        exact: If True, require exact match; otherwise fuzzy match

    Returns:
        {"success": bool, "title": str or None, "error": str or None}
    """
    if port is None:
        result = browser_start(url="https://chatgpt.com")
        if "error" in result:
            return {"success": False, "title": None, "error": result["error"]}
        port = result["port"]

    browser = await connect_browser(port=port)
    tab = await get_active_tab(browser)
    await tab.sleep(2)

    # Get accessibility tree
    tree = await ax_tree(tab, interactable_only=True)

    # Find matching chat
    for el in tree:
        if el.get("role") == "link":
            name = el.get("name", "")
            if "Open conversation options" in name:
                title = name.replace(" Open conversation options", "")

                matched = (query == title) if exact else (query.lower() in title.lower())
                if matched:
                    # Click using node_id for stability
                    node_id = el.get("_nodeId")
                    result = await ax_select(tab, node_id=int(node_id))
                    if result.get("clicked"):
                        return {"success": True, "title": title, "error": None}
                    else:
                        return {"success": False, "title": title, "error": "Click failed"}

    return {"success": False, "title": None, "error": f"No chat matching '{query}'"}


async def main():
    parser = argparse.ArgumentParser(description="Open ChatGPT chat by title")
    parser.add_argument("query", help="Search string to match chat title")
    parser.add_argument("--port", "-p", type=int, help="Connect to existing browser")
    parser.add_argument("--exact", action="store_true", help="Require exact match")
    args = parser.parse_args()

    result = await open_chat(args.query, port=args.port, exact=args.exact)

    if result["success"]:
        print(f"Opened: {result['title']}")
    else:
        print(f"Error: {result['error']}")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
