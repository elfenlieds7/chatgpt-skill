#!/usr/bin/env python3
"""Send a message in ChatGPT and get response.

Usage:
    python scripts/send_message.py "your message"
    python scripts/send_message.py "your message" --port 9222
    python scripts/send_message.py "your message" --no-wait  # don't wait for response
"""

import argparse
import asyncio
import json

from ai_dev_browser.core import connect_browser, get_active_tab
from ai_dev_browser.tools import browser_start


async def send_message(message: str, port: int = None, wait_response: bool = True) -> dict:
    """Send a message and optionally wait for response.

    Args:
        message: Message to send
        port: If provided, connect to existing browser
        wait_response: If True, wait for response to complete

    Returns:
        {"sent": True, "response": str} or {"error": str}
    """
    if port is None:
        result = browser_start(url="https://chatgpt.com")
        if "error" in result:
            return {"error": result["error"]}
        port = result["port"]

    browser = await connect_browser(port=port)
    tab = await get_active_tab(browser)
    await tab.sleep(1)

    # Type message into prompt
    escaped = message.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    typed = await tab.evaluate(f'''
        (() => {{
            const el = document.querySelector("#prompt-textarea");
            if (!el) return "not_found";
            el.focus();
            el.innerHTML = `<p>{escaped}</p>`;
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            return "typed";
        }})()
    ''')

    if typed != "typed":
        return {"error": "Could not find message input"}

    await tab.sleep(0.3)

    # Click send button
    clicked = await tab.evaluate('''
        (() => {
            const btn = document.querySelector('[data-testid="send-button"]');
            if (!btn || btn.disabled) return "not_found";
            btn.click();
            return "clicked";
        })()
    ''')

    if clicked != "clicked":
        return {"error": "Could not find or click send button"}

    if not wait_response:
        return {"sent": True, "response": None}

    # Wait for response to complete
    await tab.sleep(2)  # Initial wait for response to start

    for _ in range(120):  # Max 2 minutes
        # Check if still generating
        is_generating = await tab.evaluate('''
            (() => {
                // Check for stop button (indicates generating)
                const stopBtn = document.querySelector('[data-testid="stop-button"]');
                if (stopBtn) return true;
                // Check for streaming indicator
                const streaming = document.querySelector('[data-testid="streaming"]');
                if (streaming) return true;
                return false;
            })()
        ''')

        if not is_generating:
            break

        await tab.sleep(1)

    # Get the last response
    response = await tab.evaluate('''
        (() => {
            // Find all assistant messages
            const messages = document.querySelectorAll('[data-message-author-role="assistant"]');
            if (messages.length === 0) return null;
            const last = messages[messages.length - 1];
            return last.textContent;
        })()
    ''')

    return {"sent": True, "response": response}


async def main():
    parser = argparse.ArgumentParser(description="Send a message in ChatGPT")
    parser.add_argument("message", help="Message to send")
    parser.add_argument("--port", "-p", type=int, help="Connect to existing browser")
    parser.add_argument("--no-wait", action="store_true", help="Don't wait for response")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = await send_message(
        message=args.message,
        port=args.port,
        wait_response=not args.no_wait
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if "error" in result:
            print(f"Error: {result['error']}")
        elif result.get("response"):
            print(f"Response:\n{result['response']}")
        else:
            print("Message sent")


if __name__ == "__main__":
    asyncio.run(main())
