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
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

from config import settings
from handlers import (
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_start,
)
from handlers.intent_router import route as route_intent
from handlers.keyboards import get_start_keyboard

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
            await update.message.reply_text(response)
        elif command == "/start":
            # Send with inline keyboard
            message, keyboard = handle_start_with_keyboard()
            await update.message.reply_text(message, reply_markup=keyboard)
        else:
            response = handler()
            await update.message.reply_text(response)
    else:
        await update.message.reply_text("Unknown command. Use /help for available commands.")


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle natural language messages via LLM intent router."""
    text = update.message.text or ""
    
    # Route through LLM
    response = route_intent(text)
    await update.message.reply_text(response)


async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button clicks."""
    query = update.callback_query
    await query.answer()

    callback_data = query.data
    user_message = ""

    # Map callback data to natural language queries
    if callback_data == "query_labs":
        user_message = "what labs are available"
    elif callback_data == "query_scores_lab04":
        user_message = "show me scores for lab 4"
    elif callback_data == "query_top_lab04":
        user_message = "who are the top 5 students in lab 4"
    elif callback_data == "query_lowest":
        user_message = "which lab has the lowest pass rate"
    elif callback_data == "query_scores":
        user_message = "show me scores for lab 4"
    elif callback_data == "query_top":
        user_message = "who are the top 5 students"
    elif callback_data == "query_groups":
        user_message = "show me group performance for lab 4"

    if user_message:
        response = route_intent(user_message)
        await query.edit_message_text(response)


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
            # Not a slash command - route through LLM
            print(route_intent(args.test))
    else:
        # Telegram mode
        logger.info("Starting Telegram bot...")
        app = Application.builder().token(settings.bot_token).build()
        app.add_handler(CommandHandler("start", telegram_handler))
        app.add_handler(CommandHandler("help", telegram_handler))
        app.add_handler(CommandHandler("health", telegram_handler))
        app.add_handler(CommandHandler("labs", telegram_handler))
        app.add_handler(CommandHandler("scores", telegram_handler))
        # Handle natural language messages
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
        # Handle inline keyboard button clicks
        app.add_handler(CallbackQueryHandler(callback_query_handler))
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
