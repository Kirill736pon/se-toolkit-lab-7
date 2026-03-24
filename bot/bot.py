#!/usr/bin/env python3
"""
Telegram bot entry point with --test mode.

Usage:
    uv run bot.py --test "/start"   # Test a command without Telegram
    uv run bot.py                   # Run the actual Telegram bot
"""

import argparse
import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import settings
from handlers import (
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_start,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def parse_command_args(test_input: str) -> tuple[str, str]:
    """
    Parse command and arguments from test input.

    Args:
        test_input: Full command string (e.g., "/scores lab-04")

    Returns:
        Tuple of (command, argument). E.g., ("/scores", "lab-04")
    """
    parts = test_input.strip().split(maxsplit=1)
    command = parts[0] if parts else ""
    arg = parts[1] if len(parts) > 1 else ""
    return command, arg


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


async def telegram_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Telegram commands."""
    text = update.message.text or ""
    parts = text.split(maxsplit=1)
    command = parts[0]
    arg = parts[1] if len(parts) > 1 else ""

    handler = get_handler(command)
    if handler:
        if command == "/scores":
            response = handler(arg)
        else:
            response = handler()
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("Unknown command. Use /help for available commands.")


def main():
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Test a command (e.g., --test '/start' or --test '/scores lab-04')",
    )
    args = parser.parse_args()

    if args.test:
        # Test mode: parse command and args, call handler, print result
        command, arg = parse_command_args(args.test)
        handler = get_handler(command)
        if handler:
            if command == "/scores":
                print(handler(arg))
            else:
                print(handler())
        else:
            print(f"Unknown command: {command}")
    else:
        # Telegram mode
        logger.info("Starting Telegram bot...")
        app = Application.builder().token(settings.bot_token).build()
        app.add_handler(CommandHandler("start", telegram_handler))
        app.add_handler(CommandHandler("help", telegram_handler))
        app.add_handler(CommandHandler("health", telegram_handler))
        app.add_handler(CommandHandler("labs", telegram_handler))
        app.add_handler(CommandHandler("scores", telegram_handler))
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
