"""Command handlers for the Telegram bot."""


def handle_start() -> str:
    """Handle /start command."""
    return "Welcome! I'm your LMS assistant bot. Use /help to see available commands."


def handle_help() -> str:
    """Handle /help command."""
    return """Available commands:
/start - Start the bot
/help - Show this help message
/health - Check bot health
/labs - List available labs
/scores - View your scores"""


def handle_health() -> str:
    """Handle /health command."""
    return "OK"


def handle_labs() -> str:
    """Handle /labs command."""
    return "Labs will be implemented in Task 2."


def handle_scores() -> str:
    """Handle /scores command."""
    return "Scores will be implemented in Task 2."
