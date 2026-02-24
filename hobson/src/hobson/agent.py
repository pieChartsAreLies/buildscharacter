"""Hobson: core LangGraph agent definition."""

from pathlib import Path

from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent

from hobson.config import settings
from hobson.tools.obsidian import (
    append_to_daily_log,
    append_to_note,
    list_vault_folder,
    read_note,
    write_note,
)
from hobson.tools.telegram import send_alert, send_approval_request, send_message


def _load_brand_guidelines() -> str:
    path = Path(settings.brand_guidelines_path)
    if path.exists():
        return path.read_text()
    return "(Brand guidelines file not found)"


SYSTEM_PROMPT = f"""You are Hobson, an autonomous AI agent running the BuildsCharacter.com business.

Your mission: celebrate the universal experience of doing hard things. Make suffering funny, shareable, and wearable.

## Brand Guidelines
{_load_brand_guidelines()}

## Capabilities
You have access to tools for:
- Writing to your Obsidian vault (documentation, logging, metrics)
- Sending Telegram messages to your owner for approvals and alerts
- Reading vault content to inform decisions

## Operating Principles
- Log significant actions to your daily log in Obsidian
- Request approval via Telegram before any spending or irreversible actions
- Be transparent about failures and reasoning
- Write in your voice: dry, self-aware, competent but honest
"""

TOOLS = [
    write_note,
    read_note,
    append_to_note,
    append_to_daily_log,
    list_vault_folder,
    send_message,
    send_alert,
    send_approval_request,
]


def create_agent(checkpointer=None):
    """Create and return the compiled Hobson agent graph."""
    model = ChatAnthropic(model="claude-sonnet-4-20250514")
    return create_react_agent(
        model,
        TOOLS,
        prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )
