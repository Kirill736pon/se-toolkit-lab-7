"""Bot command handlers."""

from .commands.__init__ import (
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_start,
)

__all__ = [
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
    "handle_start",
]
