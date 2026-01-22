#!/usr/bin/env python3
"""Download complete conversation history from current ChatGPT chat.

Usage:
    python scripts/download_chat.py                    # print to stdout
    python scripts/download_chat.py --port 9222       # use existing browser
    python scripts/download_chat.py -o chat.json      # save to file
    python scripts/download_chat.py --format markdown # output as markdown
"""

import argparse
import asyncio
import json

from ai_dev_browser.core import connect_browser, get_active_tab
from ai_dev_browser.tools import browser_start


async def download_chat(port: int = None) -> dict:
    """Download all messages from current chat.

    Args:
        port: If provided, connect to existing browser

    Returns:
        {"title": str, "messages": [{"role": str, "content": str}]} or {"error": str}
    """
    if port is None:
        result = browser_start(url="https://chatgpt.com")
        if "error" in result:
            return {"error": result["error"]}
        port = result["port"]

    browser = await connect_browser(port=port)
    tab = await get_active_tab(browser)
    await tab.sleep(1)

    # Scroll to top first to ensure all messages are loaded
    await tab.evaluate('''
        (() => {
            const main = document.querySelector('main');
            if (main) main.scrollTop = 0;
        })()
    ''')
    await tab.sleep(0.5)

    # Get chat title
    title = await tab.evaluate('''
        (() => {
            // Try to get title from page
            const h1 = document.querySelector('h1');
            if (h1) return h1.textContent;
            // Fallback to document title
            return document.title.replace(' | ChatGPT', '').replace('ChatGPT', '').trim() || 'Untitled';
        })()
    ''')

    # Scroll through chat to load all messages (for long conversations)
    last_count = 0
    for _ in range(50):
        msg_count = await tab.evaluate('''
            document.querySelectorAll('[data-message-author-role]').length
        ''')
        if msg_count == last_count:
            break
        last_count = msg_count
        await tab.evaluate('''
            (() => {
                const main = document.querySelector('main');
                if (main) main.scrollTop = 0;  // Scroll up to load older messages
            })()
        ''')
        await tab.sleep(0.5)

    # Get all messages
    messages = await tab.evaluate('''
        (() => {
            const msgs = document.querySelectorAll('[data-message-author-role]');
            return Array.from(msgs).map(m => ({
                role: m.getAttribute('data-message-author-role'),
                content: m.textContent
            }));
        })()
    ''')

    # Convert from nodriver format
    result_messages = []
    for msg in messages:
        if isinstance(msg, dict) and msg.get('type') == 'object':
            # Handle nodriver's nested format
            values = dict(msg.get('value', []))
            result_messages.append({
                'role': values.get('role', {}).get('value', 'unknown'),
                'content': values.get('content', {}).get('value', '')
            })
        elif isinstance(msg, dict):
            result_messages.append(msg)

    return {
        "title": title if isinstance(title, str) else str(title),
        "messages": result_messages,
        "count": len(result_messages)
    }


def format_markdown(data: dict) -> str:
    """Format chat as markdown."""
    lines = [f"# {data['title']}\n"]
    for msg in data['messages']:
        role = msg['role'].upper()
        content = msg['content']
        lines.append(f"## {role}\n\n{content}\n")
    return "\n".join(lines)


async def main():
    parser = argparse.ArgumentParser(description="Download ChatGPT conversation")
    parser.add_argument("--port", "-p", type=int, help="Connect to existing browser")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--format", "-f", choices=["json", "markdown"], default="json",
                        help="Output format (default: json)")
    args = parser.parse_args()

    result = await download_chat(port=args.port)

    if "error" in result:
        print(f"Error: {result['error']}")
        return

    if args.format == "markdown":
        output = format_markdown(result)
    else:
        output = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Saved to {args.output} ({result['count']} messages)")
    else:
        print(output)


if __name__ == "__main__":
    asyncio.run(main())
