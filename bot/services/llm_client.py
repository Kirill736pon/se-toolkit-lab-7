"""
LLM client for intent routing.

Sends messages to the LLM with tool definitions and handles tool calls.
"""

import json
import logging
import sys
from typing import Any

import httpx

from config import settings

logger = logging.getLogger(__name__)


# Tool definitions for all 9 backend endpoints
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get list of all labs and tasks. Use this to discover what labs are available.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of enrolled learners and their groups. Use for questions about students or enrollment.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submissions per day timeline for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group performance (scores and student counts) for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"},
                    "limit": {"type": "integer", "description": "Number of top learners to return, e.g. 5"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. 'lab-01', 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL sync to refresh data from autochecker. Use when user asks to update or sync data.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# System prompt for the LLM
SYSTEM_PROMPT = """You are a helpful assistant for a Learning Management System (LMS). 
You have access to tools that let you query data about labs, students, scores, and analytics.

When a user asks a question:
1. First understand what they're asking
2. Call the appropriate tools to get the data
3. Analyze the results
4. Provide a clear, helpful answer based on the data

If the user's message is a greeting or doesn't relate to LMS data, respond naturally without calling tools.

Available tools:
- get_items: List all labs and tasks
- get_learners: List enrolled students and groups
- get_scores: Score distribution for a lab
- get_pass_rates: Per-task pass rates for a lab
- get_timeline: Submissions per day for a lab
- get_groups: Per-group performance for a lab
- get_top_learners: Top N students for a lab
- get_completion_rate: Completion percentage for a lab
- trigger_sync: Refresh data from autochecker

Always call tools when the user asks about specific data. For comparison questions (e.g., "which lab has the lowest pass rate"), 
you may need to call tools multiple times for different labs."""


class LLMClient:
    """Client for the LLM API with tool calling support."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    def chat(self, messages: list[dict]) -> dict:
        """
        Send a chat request to the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.

        Returns:
            LLM response dict with 'choices' containing the assistant message.
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": TOOLS,
            "tool_choice": "auto",
        }

        response = self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        return response.json()

    def execute_tool(self, tool_name: str, arguments: dict) -> Any:
        """
        Execute a tool by calling the appropriate backend endpoint.

        Args:
            tool_name: Name of the tool (e.g., "get_items", "get_pass_rates")
            arguments: Tool arguments dict

        Returns:
            Tool execution result
        """
        from services.api_client import api_client

        tool_methods = {
            "get_items": lambda: api_client.get("/items/"),
            "get_learners": lambda: api_client.get("/learners/"),
            "get_scores": lambda: api_client.get(f"/analytics/scores?lab={arguments.get('lab', '')}"),
            "get_pass_rates": lambda: api_client.get(f"/analytics/pass-rates?lab={arguments.get('lab', '')}"),
            "get_timeline": lambda: api_client.get(f"/analytics/timeline?lab={arguments.get('lab', '')}"),
            "get_groups": lambda: api_client.get(f"/analytics/groups?lab={arguments.get('lab', '')}"),
            "get_top_learners": lambda: api_client.get(f"/analytics/top-learners?lab={arguments.get('lab', '')}&limit={arguments.get('limit', 5)}"),
            "get_completion_rate": lambda: api_client.get(f"/analytics/completion-rate?lab={arguments.get('lab', '')}"),
            "trigger_sync": lambda: api_client._client.post("/pipeline/sync").json(),
        }

        if tool_name not in tool_methods:
            return f"Unknown tool: {tool_name}"

        try:
            result = tool_methods[tool_name]()
            return result
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"


# Global LLM client instance
llm_client = LLMClient(
    settings.llm_api_key,
    settings.llm_api_base_url,
    settings.llm_api_model,
)
