"""Command handlers for the Telegram bot."""

from services.api_client import api_client


def handle_start() -> str:
    """Handle /start command."""
    return "Welcome! I'm your LMS assistant bot. Use /help to see available commands."


def handle_help() -> str:
    """Handle /help command."""
    return """Available commands:
/start - Start the bot
/help - Show this help message
/health - Check backend health
/labs - List available labs
/scores <lab> - View pass rates for a lab (e.g., /scores lab-04)"""


def handle_health() -> str:
    """Handle /health command."""
    is_healthy, message = api_client.health_check()
    return message


def handle_labs() -> str:
    """Handle /labs command."""
    try:
        labs = api_client.get_labs()
        if not labs:
            return "No labs available."
        
        lines = ["Available labs:"]
        for lab in labs:
            lab_id = lab.get("id", "unknown")
            title = lab.get("title", "Untitled")
            lines.append(f"- {lab_id} — {title}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching labs: {str(e)}"


def handle_scores(lab_id: str = None) -> str:
    """
    Handle /scores command.

    Args:
        lab_id: Lab identifier (e.g., "lab-04"). If None, shows error message.
    """
    if not lab_id:
        return "Usage: /scores <lab-id> (e.g., /scores lab-04)"

    try:
        pass_rates = api_client.get_pass_rates(lab_id)
        if pass_rates is None:
            return f"No data found for lab '{lab_id}'. Check the lab ID."
        if not pass_rates:
            return f"No pass rates available for lab '{lab_id}'."

        lines = [f"Pass rates for {lab_id}:"]
        for task in pass_rates:
            task_name = task.get("task", "Unknown task")
            avg_score = task.get("avg_score", 0)
            attempts = task.get("attempts", 0)
            lines.append(f"- {task_name}: {avg_score:.1f}% ({attempts} attempts)")
        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching scores: {str(e)}"
