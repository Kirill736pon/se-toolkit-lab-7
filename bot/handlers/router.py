"""Intent router for dispatching commands to handlers."""

from typing import Callable


def get_handler(command: str) -> Callable[[], str]:
    """Get handler function for a command.
    
    Args:
        command: Command name (e.g., 'start', 'help')
        
    Returns:
        Handler function that returns response text
    """
    from .commands import (
        handle_help,
        handle_health,
        handle_labs,
        handle_scores,
        handle_start,
    )
    
    handlers = {
        "start": handle_start,
        "help": handle_help,
        "health": handle_health,
        "labs": handle_labs,
        "scores": handle_scores,
    }
    
    return handlers.get(command, lambda: "Command not found")
