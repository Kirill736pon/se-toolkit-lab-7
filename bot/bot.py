#!/usr/bin/env python3
"""
Telegram bot entry point with --test mode.

Usage:
    uv run bot.py --test "/start"   # Test a command without Telegram
    uv run bot.py                   # Run the actual Telegram bot
"""

import argparse

from config import settings
from handlers import (
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_start,
)


def get_handler(command: str) -> callable:
    """Get the handler function for a command."""
    handlers = {
        "/start": handle_start,
        "/help": handle_help,
        "/health": handle_health,
        "/labs": handle_labs,
        "/scores": handle_scores,
    }
    return handlers.get(command)


def main():
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Test a command (e.g., --test '/start')",
    )
    args = parser.parse_args()

    if args.test:
        # Test mode: call handler and print result
        handler = get_handler(args.test)
        if handler:
            print(handler())
        else:
            print(f"Unknown command: {args.test}")
    else:
        # Telegram mode: will be implemented later
        print("Telegram bot mode will be implemented in Task 1.")
        print("For now, use --test mode to test handlers.")


if __name__ == "__main__":
    main()
