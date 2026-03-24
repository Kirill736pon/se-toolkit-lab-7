"""
Intent router for natural language queries.

Routes user messages to LLM with tool definitions, executes tool calls,
and returns formatted responses.
"""

import json
import logging
import sys

from services.llm_client import llm_client, SYSTEM_PROMPT

logger = logging.getLogger(__name__)


def debug_log(message: str):
    """Print debug message to stderr for --test mode debugging."""
    print(message, file=sys.stderr)


def route(message: str) -> str:
    """
    Route a user message through the LLM intent router.

    Args:
        message: User's natural language query

    Returns:
        Formatted response string
    """
    # Initialize conversation with system prompt
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message},
    ]

    max_iterations = 5  # Prevent infinite loops
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        try:
            # Call LLM
            response = llm_client.chat(messages)
        except Exception as e:
            debug_log(f"[llm] Error calling LLM: {e}")
            return f"LLM error: {str(e)}. Try again later."

        # Get assistant message
        assistant_message = response.get("choices", [{}])[0].get("message", {})

        # Check if LLM wants to call tools
        tool_calls = assistant_message.get("tool_calls", [])

        if not tool_calls:
            # No tool calls — LLM has a final answer
            content = assistant_message.get("content", "")
            if content:
                return content
            else:
                return "I'm not sure how to help with that. Try asking about labs, scores, or students."

        # Add assistant message to conversation
        messages.append(assistant_message)

        # Execute each tool call
        for tool_call in tool_calls:
            function = tool_call.get("function", {})
            tool_name = function.get("name", "")
            tool_args_str = function.get("arguments", "{}")

            try:
                tool_args = json.loads(tool_args_str) if tool_args_str else {}
            except json.JSONDecodeError:
                tool_args = {}

            debug_log(f"[tool] LLM called: {tool_name}({tool_args})")

            # Execute the tool
            result = llm_client.execute_tool(tool_name, tool_args)

            # Log result summary
            if isinstance(result, list):
                debug_log(f"[tool] Result: {len(result)} items")
            elif isinstance(result, dict):
                debug_log(f"[tool] Result: {len(result)} keys")
            else:
                debug_log(f"[tool] Result: {str(result)[:100]}")

            # Add tool result to conversation
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.get("id", ""),
                "content": json.dumps(result, default=str) if not isinstance(result, str) else result,
            })

        debug_log(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM")

    return "I needed too many steps to answer that. Try a simpler question."
