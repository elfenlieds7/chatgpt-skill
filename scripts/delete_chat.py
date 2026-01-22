#!/usr/bin/env python3
"""Delete current ChatGPT conversation.

Usage:
    python scripts/delete_chat.py              # delete current chat
    python scripts/delete_chat.py --port 9222  # use existing browser
"""

import argparse
import asyncio
import json

from ai_dev_browser import cdp
from ai_dev_browser.core import connect_browser, get_active_tab
from ai_dev_browser.tools import browser_start, ax_tree, ax_select


async def delete_chat(port: int = None) -> dict:
    """Delete the current chat.

    Args:
        port: If provided, connect to existing browser

    Returns:
        {"deleted": True, "title": str} or {"error": str}
    """
    if port is None:
        result = browser_start(url="https://chatgpt.com")
        if "error" in result:
            return {"error": result["error"]}
        port = result["port"]

    browser = await connect_browser(port=port)
    tab = await get_active_tab(browser)
    await tab.sleep(1)

    # Get chat title before deleting
    title = await tab.evaluate('document.title.replace(" | ChatGPT", "")')

    # Find and click the conversation options button using coordinates
    js = '''
        (function() {
            var btn = document.querySelector('[data-testid="conversation-options-button"]');
            if (!btn) return null;
            var rect = btn.getBoundingClientRect();
            return [rect.x + rect.width/2, rect.y + rect.height/2];
        })()
    '''
    pos = await tab.evaluate(js)

    if not pos or not isinstance(pos, list) or len(pos) != 2:
        return {"error": "Could not find conversation options button"}

    # Extract coordinates from nodriver's format
    x = pos[0].get('value') if isinstance(pos[0], dict) else pos[0]
    y = pos[1].get('value') if isinstance(pos[1], dict) else pos[1]

    # Click options button via CDP
    await tab.send(cdp.input_.dispatch_mouse_event('mousePressed', float(x), float(y), button=cdp.input_.MouseButton.LEFT, click_count=1))
    await tab.send(cdp.input_.dispatch_mouse_event('mouseReleased', float(x), float(y), button=cdp.input_.MouseButton.LEFT, click_count=1))
    await tab.sleep(1.5)

    # Find and click Delete menu item
    tree = await ax_tree(tab, interactable_only=True)
    delete_node_id = None
    for el in tree:
        if el.get('role') == 'menuitem' and el.get('name') == 'Delete':
            delete_node_id = int(el.get('_nodeId'))
            break

    if not delete_node_id:
        return {"error": "Could not find Delete menu item"}

    await ax_select(tab, node_id=delete_node_id)
    await tab.sleep(1)

    # Confirm deletion - look for confirm button in dialog
    tree = await ax_tree(tab, interactable_only=True)
    for el in tree:
        name = el.get('name', '').lower()
        if 'delete' in name and el.get('role') == 'button':
            node_id = int(el.get('_nodeId'))
            await ax_select(tab, node_id=node_id)
            break

    await tab.sleep(1)

    return {"deleted": True, "title": title if isinstance(title, str) else str(title)}


async def main():
    parser = argparse.ArgumentParser(description="Delete current ChatGPT conversation")
    parser.add_argument("--port", "-p", type=int, help="Connect to existing browser")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = await delete_chat(port=args.port)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Deleted: {result['title']}")


if __name__ == "__main__":
    asyncio.run(main())
