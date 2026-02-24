"""Telegram bot: bidirectional messaging, approvals, and standing order learning."""

import logging
import traceback
import uuid
from typing import Optional

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from langchain_core.tools import tool

from hobson.config import settings
from hobson.db import HobsonDB

logger = logging.getLogger(__name__)

# Module-level references set by init_telegram()
_app: Optional[Application] = None
_agent = None
_db: Optional[HobsonDB] = None
_processing_chats: set[str] = set()

STANDING_ORDERS_PATH = "98 - Hobson Builds Character/Operations/Standing Orders.md"


def init_telegram(agent, db: HobsonDB) -> Application:
    """Build and return the PTB Application with all handlers."""
    global _app, _agent, _db
    _agent = agent
    _db = db

    _app = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .build()
    )

    _app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _handle_message))
    _app.add_handler(CallbackQueryHandler(_handle_callback))

    return _app


def _format_history(messages: list[dict]) -> str:
    """Format recent messages as conversation context."""
    lines = []
    for msg in messages:
        sender = "Hobson" if msg["is_from_hobson"] else msg["sender_name"]
        lines.append(f"{sender}: {msg['content']}")
    return "\n".join(lines)


async def _load_standing_orders() -> str:
    """Load standing orders from Obsidian (async-safe via httpx)."""
    import httpx

    url = f"http://{settings.obsidian_host}:{settings.obsidian_port}/vault/{STANDING_ORDERS_PATH}"
    headers = {
        "Authorization": f"Bearer {settings.obsidian_api_key}",
        "Accept": "text/markdown",
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                return resp.text
    except Exception:
        pass
    return "(Standing orders not available)"


async def _handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming Telegram text messages."""
    if not update.message or not update.message.text:
        return

    chat_id = str(update.message.chat_id)
    sender = update.message.from_user
    sender_name = sender.first_name or sender.username or "Unknown"
    text = update.message.text

    # Concurrency guard
    if chat_id in _processing_chats:
        return
    _processing_chats.add(chat_id)

    try:
        # Store incoming message
        _db.store_message(chat_id, sender_name, text)

        # Build context
        recent = _db.get_recent_messages(chat_id, limit=20)
        history = _format_history(recent)
        standing_orders = await _load_standing_orders()

        conversation_prompt = (
            f"## Standing Orders\n{standing_orders}\n\n"
            f"## Recent Conversation\n{history}\n\n"
            f"## Current Message\n{sender_name}: {text}\n\n"
            "Respond to the current message. You are having a conversation with your boss "
            "via Telegram. Be concise, direct, and in-character.\n\n"
            "IMPORTANT: If the user gives you feedback, a correction, or a standing instruction "
            "(e.g., 'always do X', 'stop doing Y', 'remember that Z'), you MUST propose it as a "
            "standing order. Use send_standing_order_proposal to send a confirmation message with "
            "the proposed text. Do NOT write directly to Standing Orders without confirmation."
        )

        # Invoke agent
        result = await _agent.ainvoke(
            {"messages": [{"role": "user", "content": conversation_prompt}]},
            config={"configurable": {"thread_id": f"telegram-{chat_id}"}},
        )

        # Extract response text from agent output
        response_text = _extract_response(result)

        # Store and send response
        _db.store_message(chat_id, "Hobson", response_text, is_from_hobson=True)
        await update.message.reply_text(response_text, parse_mode="Markdown")

        # Log the conversation turn
        logger.info(f"Telegram conversation: {sender_name} -> Hobson in chat {chat_id}")

    except Exception as e:
        error_msg = f"Something went wrong. Check the logs.\n`{type(e).__name__}`"
        logger.error(f"Telegram handler error: {e}\n{traceback.format_exc()}")
        try:
            await update.message.reply_text(error_msg)
        except Exception:
            pass
    finally:
        _processing_chats.discard(chat_id)


def _extract_response(result) -> str:
    """Extract the final text response from a LangGraph agent result."""
    messages = result.get("messages", [])
    # Walk backwards to find the last AI message that isn't a tool call
    for msg in reversed(messages):
        if hasattr(msg, "content") and isinstance(msg.content, str) and msg.content.strip():
            if not hasattr(msg, "tool_calls") or not msg.tool_calls:
                return msg.content
            if msg.content.strip():
                return msg.content
    return "(No response generated)"


async def _handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle approval/denial and standing order confirmation button callbacks."""
    query = update.callback_query
    await query.answer()

    data = query.data
    parts = data.split(":", 1)
    if len(parts) != 2:
        return

    action, request_id = parts

    if action in ("approve", "deny"):
        approved = action == "approve"
        _db.resolve_approval(request_id, approved)
        status = "APPROVED" if approved else "DENIED"
        await query.edit_message_text(
            text=f"{query.message.text}\n\n*Status: {status}*",
            parse_mode="Markdown",
        )
        logger.info(f"Approval {request_id}: {status}")

    elif action == "confirm_order":
        # Standing order confirmed -- write to Obsidian
        import httpx
        from psycopg.rows import dict_row
        import psycopg

        with psycopg.connect(_db.database_url, row_factory=dict_row) as conn:
            record = conn.execute(
                "SELECT action FROM hobson.approvals WHERE request_id = %s",
                (request_id,),
            ).fetchone()

        if record:
            proposed_text = record["action"]
            url = f"http://{settings.obsidian_host}:{settings.obsidian_port}/vault/{STANDING_ORDERS_PATH}"
            headers = {
                "Authorization": f"Bearer {settings.obsidian_api_key}",
                "Content-Type": "application/json",
            }
            async with httpx.AsyncClient(timeout=10) as client:
                await client.patch(
                    url,
                    json={"content": f"\n- {proposed_text}", "operation": "append"},
                    headers=headers,
                )

            _db.resolve_approval(request_id, True)
            await query.edit_message_text(
                text=f"{query.message.text}\n\n*Standing order saved.*",
                parse_mode="Markdown",
            )
            logger.info(f"Standing order confirmed and saved: {proposed_text}")

    elif action == "skip_order":
        _db.resolve_approval(request_id, False)
        await query.edit_message_text(
            text=f"{query.message.text}\n\n*Skipped.*",
            parse_mode="Markdown",
        )


# -- Agent tools (used by LangGraph during workflows and conversation) --

@tool
def send_message(text: str) -> str:
    """Send a message to the Hobson Telegram group.

    Args:
        text: Message text (supports Telegram markdown)
    """
    import asyncio
    bot = Bot(token=settings.telegram_bot_token)
    asyncio.get_event_loop().run_until_complete(
        bot.send_message(
            chat_id=settings.telegram_chat_id,
            text=text,
            parse_mode="Markdown",
        )
    )
    return "Message sent to Telegram"


@tool
def send_alert(title: str, details: str) -> str:
    """Send an alert notification to the Hobson Telegram group.

    Args:
        title: Alert title (will be bold)
        details: Alert details
    """
    text = f"*{title}*\n\n{details}"
    import asyncio
    bot = Bot(token=settings.telegram_bot_token)
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

    if _db:
        _db.create_approval(request_id, action, reasoning, estimated_cost)

    cost_line = f"\n*Cost:* ${estimated_cost:.2f}" if estimated_cost > 0 else ""
    text = f"*Approval Request* `{request_id}`\n\n*Action:* {action}\n*Reasoning:* {reasoning}{cost_line}"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Approve", callback_data=f"approve:{request_id}"),
            InlineKeyboardButton("Deny", callback_data=f"deny:{request_id}"),
        ]
    ])

    import asyncio
    bot = Bot(token=settings.telegram_bot_token)
    asyncio.get_event_loop().run_until_complete(
        bot.send_message(
            chat_id=settings.telegram_chat_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
    )
    return f"Approval request sent (ID: {request_id}). Waiting for response."


@tool
def send_standing_order_proposal(category: str, proposed_text: str) -> str:
    """Propose a new standing order for confirmation. Use when the user gives feedback or instructions.

    Args:
        category: One of 'Feedback', 'Preferences', or 'Lessons Learned'
        proposed_text: The concise directive to add to Standing Orders
    """
    request_id = str(uuid.uuid4())[:8]

    if _db:
        _db.create_approval(request_id, proposed_text, f"Standing order: {category}", 0)

    text = (
        f"*Standing Order Proposal*\n\n"
        f"*Category:* {category}\n"
        f"*Directive:* {proposed_text}"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Confirm", callback_data=f"confirm_order:{request_id}"),
            InlineKeyboardButton("Skip", callback_data=f"skip_order:{request_id}"),
        ]
    ])

    import asyncio
    bot = Bot(token=settings.telegram_bot_token)
    asyncio.get_event_loop().run_until_complete(
        bot.send_message(
            chat_id=settings.telegram_chat_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
    )
    return f"Standing order proposal sent (ID: {request_id}). Waiting for confirmation."
