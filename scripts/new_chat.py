#!/usr/bin/env python3
"""Start a new ChatGPT conversation.

Usage:
    python scripts/new_chat.py
    python scripts/new_chat.py --port 9222  # use existing browser
"""

import argparse
import asyncio

from ai_dev_browser.core import connect_browser, get_active_tab
from ai_dev_browser.tools import browser_start, ax_tree, ax_select


async def new_chat(port: int = None) -> bool:
    """Start a new chat.

    Args:
        port: If provided, connect to existing browser. Otherwise start new one.

    Returns:
        True if successful
    """
    # Start or connect to browser
    if port is None:
        result = browser_start(url="https://chatgpt.com")
        if "error" in result:
            print(f"Failed to start browser: {result['error']}")
            return False
        port = result["port"]
        print(f"Started browser on port {port}")

    browser = await connect_browser(port=port)
    tab = await get_active_tab(browser)
    await tab.sleep(2)

    # Find and click "New chat" using accessibility tree
    tree = await ax_tree(tab, interactable_only=True)
    for el in tree:
        name = el.get("name", "").lower()
        if "new chat" in name:
            # Use node_id directly for stable click (ref may change if page updates)
            node_id = el.get("_nodeId")
            result = await ax_select(tab, node_id=int(node_id))
            if result.get("clicked"):
                print("New chat started")
                return True

    print("Could not find New chat button")
    return False


async def main():
    parser = argparse.ArgumentParser(description="Start a new ChatGPT conversation")
    parser.add_argument("--port", "-p", type=int, help="Connect to existing browser on this port")
    args = parser.parse_args()

    success = await new_chat(port=args.port)
    exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
