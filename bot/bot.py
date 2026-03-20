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
    command = update.message.text.split()[0] if update.message.text else "/start"
    handler = get_handler(command)
    if handler:
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
