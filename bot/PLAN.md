# Task 1 Plan: Basic Bot Structure

## Implementation Summary

Task 1 creates the foundational structure for the Telegram bot with testable handlers.

## What Was Built

### 1. Bot Entry Point (`bot/bot.py`)
- `--test` mode for testing handlers without Telegram
- Command router (`get_handler()`) that maps commands to handler functions
- Imports handlers from `handlers` module

### 2. Configuration (`bot/config.py`)
- Pydantic Settings class for loading environment variables
- Reads from `.env.bot.secret` in project root
- Provides type-safe access to: `bot_token`, `lms_api_url`, `lms_api_key`, `llm_api_*`

### 3. Command Handlers (`bot/handlers/`)
- `commands.py` - Handler functions for each slash command
- `__init__.py` - Exports handlers for clean imports
- **Separation of concerns**: handlers are pure functions that return strings, independent of Telegram

### 4. Implemented Commands

| Command | Response | Status |
|---------|----------|--------|
| `/start` | Welcome message | ✅ |
| `/help` | List of commands | ✅ |
| `/health` | "OK" (verifies config) | ✅ |
| `/labs` | Placeholder for Task 2 | ✅ |
| `/scores` | Placeholder for Task 2 | ✅ |

## Architecture Patterns Used

1. **Separation of Concerns** - Handlers don't depend on Telegram API
2. **Dependency Injection** - Settings loaded once, used everywhere
3. **Testability** - `--test` mode allows testing without Telegram

## Testing

```bash
# Test all commands
uv run bot.py --test "/start"
uv run bot.py --test "/help"
uv run bot.py --test "/health"
uv run bot.py --test "/labs"
uv run bot.py --test "/scores"
```

## Acceptance Criteria

- [x] `bot.py` exists with `--test` mode
- [x] All 5 commands return appropriate responses
- [x] Configuration loads from `.env.bot.secret`
- [x] Handlers are in separate module (`handlers/`)
- [x] No hardcoded URLs or API keys

## Next Steps (Task 2)

- Implement real API client for LMS backend
- Connect `/labs` to `GET /items/` endpoint
- Connect `/scores` to `GET /scores/` endpoint
- Add error handling for API failures
