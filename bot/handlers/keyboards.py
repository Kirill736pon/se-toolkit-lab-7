"""Telegram inline keyboard layouts."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_start_keyboard() -> InlineKeyboardMarkup:
    """
    Create inline keyboard for /start command.

    Shows common queries users might want to try.
    """
    keyboard = [
        [
            InlineKeyboardButton("📚 What labs are available?", callback_data="query_labs"),
        ],
        [
            InlineKeyboardButton("📊 Show scores for lab-04", callback_data="query_scores_lab04"),
        ],
        [
            InlineKeyboardButton("🏆 Top 5 students in lab-04", callback_data="query_top_lab04"),
        ],
        [
            InlineKeyboardButton("📈 Which lab has lowest pass rate?", callback_data="query_lowest"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_help_keyboard() -> InlineKeyboardMarkup:
    """Create inline keyboard for /help command."""
    keyboard = [
        [
            InlineKeyboardButton("Labs", callback_data="query_labs"),
            InlineKeyboardButton("Scores", callback_data="query_scores"),
        ],
        [
            InlineKeyboardButton("Top Students", callback_data="query_top"),
            InlineKeyboardButton("Groups", callback_data="query_groups"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
