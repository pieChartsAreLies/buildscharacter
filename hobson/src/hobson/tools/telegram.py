"""Telegram bot integration for alerts and human-in-the-loop approvals."""

import asyncio
import uuid
from typing import Optional

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from langchain_core.tools import tool

from hobson.config import settings

_bot: Optional[Bot] = None
_pending_approvals: dict[str, Optional[bool]] = {}


def _get_bot() -> Bot:
    global _bot
    if _bot is None:
        _bot = Bot(token=settings.telegram_bot_token)
    return _bot


@tool
def send_message(text: str) -> str:
    """Send a message to the Hobson Telegram group.

    Args:
        text: Message text (supports Telegram markdown)
    """
    bot = _get_bot()
    asyncio.get_event_loop().run_until_complete(
        bot.send_message(
            chat_id=settings.telegram_chat_id,
            text=text,
            parse_mode="Markdown",
        )
    )
    return f"Message sent to Telegram"


@tool
def send_alert(title: str, details: str) -> str:
    """Send an alert notification to the Hobson Telegram group.

    Args:
        title: Alert title (will be bold)
        details: Alert details
    """
    text = f"*{title}*\n\n{details}"
    bot = _get_bot()
    asyncio.get_event_loop().run_until_complete(
        bot.send_message(
            chat_id=settings.telegram_chat_id,
            text=text,
            parse_mode="Markdown",
        )
    )
    return f"Alert sent: {title}"


@tool
def send_approval_request(action: str, reasoning: str, estimated_cost: float = 0.0) -> str:
    """Send an approval request with Approve/Deny buttons.

    Args:
        action: What Hobson wants to do
        reasoning: Why this action is recommended
        estimated_cost: Estimated cost in USD (0.0 if free)
    """
    request_id = str(uuid.uuid4())[:8]
    _pending_approvals[request_id] = None

    cost_line = f"\n*Cost:* ${estimated_cost:.2f}" if estimated_cost > 0 else ""
    text = f"*Approval Request* `{request_id}`\n\n*Action:* {action}\n*Reasoning:* {reasoning}{cost_line}"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Approve", callback_data=f"approve:{request_id}"),
            InlineKeyboardButton("Deny", callback_data=f"deny:{request_id}"),
        ]
    ])

    bot = _get_bot()
    asyncio.get_event_loop().run_until_complete(
        bot.send_message(
            chat_id=settings.telegram_chat_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
    )
    return f"Approval request sent (ID: {request_id}). Waiting for response."


async def handle_callback(update, context):
    """Handle approval/denial button callbacks."""
    query = update.callback_query
    await query.answer()

    action, request_id = query.data.split(":", 1)
    approved = action == "approve"
    _pending_approvals[request_id] = approved

    status = "APPROVED" if approved else "DENIED"
    await query.edit_message_text(
        text=f"{query.message.text}\n\n*Status: {status}*",
        parse_mode="Markdown",
    )


def get_approval_status(request_id: str) -> Optional[bool]:
    """Check if an approval request has been responded to.

    Returns None if pending, True if approved, False if denied.
    """
    return _pending_approvals.get(request_id)
