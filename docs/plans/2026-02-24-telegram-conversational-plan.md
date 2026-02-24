# Telegram Conversational Capability Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add bidirectional Telegram messaging to Hobson so the owner can converse with him, give feedback, and receive responses -- turning Hobson from a scheduled-only agent into an interactive employee.

**Architecture:** Add python-telegram-bot (PTB) long-polling to the existing single-process `main.py`, alongside APScheduler and FastAPI. New PostgreSQL tables for message history and approvals. Obsidian Standing Orders file for persistent learning. Agent invocation switched from sync `invoke()` to async `ainvoke()`.

**Tech Stack:** python-telegram-bot 21+, LangGraph, PostgreSQL (psycopg3), Obsidian REST API, Gemini 2.5 Flash

**Design doc:** `docs/plans/2026-02-24-telegram-conversational-design.md`

---

### Task 1: Database Migration (messages + approvals tables)

**Files:**
- Create: `hobson/sql/002_messages_approvals.sql`
- Modify: `hobson/src/hobson/db.py:1-120`

**Step 1: Write the SQL migration**

Create `hobson/sql/002_messages_approvals.sql`:

```sql
-- Hobson: message history and approval tracking
-- Apply: psql -U hobson -d project_data -f 002_messages_approvals.sql

-- Message history for Telegram conversations
CREATE TABLE IF NOT EXISTS hobson.messages (
    id SERIAL PRIMARY KEY,
    chat_id TEXT NOT NULL,
    sender_name TEXT NOT NULL,
    content TEXT NOT NULL,
    is_from_hobson BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_chat_timestamp
    ON hobson.messages (chat_id, timestamp DESC);

-- Approval requests (replaces in-memory dict)
CREATE TABLE IF NOT EXISTS hobson.approvals (
    request_id TEXT PRIMARY KEY,
    action TEXT NOT NULL,
    reasoning TEXT,
    estimated_cost FLOAT DEFAULT 0,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);
```

**Step 2: Apply the migration to CT 201**

Run from Loki (SSH):
```bash
ssh root@192.168.2.16 "pct exec 255 -- bash -c 'cd /root/builds-character/hobson && psql -U hobson -h 192.168.2.67 -d project_data -f sql/002_messages_approvals.sql'"
```

Expected: `CREATE TABLE` x2, `CREATE INDEX` x1 (no errors)

**Step 3: Add DB methods for messages and approvals**

Add these methods to the `HobsonDB` class in `hobson/src/hobson/db.py` (after the existing `update_task_status` method at line 119):

```python
    # -- Message history --

    def store_message(self, chat_id: str, sender_name: str, content: str, is_from_hobson: bool = False):
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO hobson.messages (chat_id, sender_name, content, is_from_hobson)
                   VALUES (%s, %s, %s, %s)""",
                (chat_id, sender_name, content, is_from_hobson),
            )

    def get_recent_messages(self, chat_id: str, limit: int = 20) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT sender_name, content, is_from_hobson, timestamp
                   FROM hobson.messages
                   WHERE chat_id = %s
                   ORDER BY timestamp DESC
                   LIMIT %s""",
                (chat_id, limit),
            ).fetchall()
            return list(reversed(rows))  # chronological order

    # -- Approvals --

    def create_approval(self, request_id: str, action: str, reasoning: str, estimated_cost: float = 0):
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO hobson.approvals (request_id, action, reasoning, estimated_cost)
                   VALUES (%s, %s, %s, %s)""",
                (request_id, action, reasoning, estimated_cost),
            )

    def resolve_approval(self, request_id: str, approved: bool):
        status = "approved" if approved else "denied"
        with self._conn() as conn:
            conn.execute(
                """UPDATE hobson.approvals
                   SET status = %s, resolved_at = NOW()
                   WHERE request_id = %s""",
                (status, request_id),
            )

    def get_approval_status(self, request_id: str) -> str | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT status FROM hobson.approvals WHERE request_id = %s",
                (request_id,),
            ).fetchone()
            return row["status"] if row else None
```

**Step 4: Commit**

```bash
git add hobson/sql/002_messages_approvals.sql hobson/src/hobson/db.py
git commit -m "feat: add messages and approvals DB tables and methods"
```

---

### Task 2: Refactor telegram.py for bidirectional messaging

**Files:**
- Modify: `hobson/src/hobson/tools/telegram.py:1-117`

This is the biggest change. The file needs to:
1. Accept a shared PTB `Application` instead of creating standalone `Bot` instances
2. Add a message handler that invokes the agent
3. Add a callback handler that updates the approvals DB
4. Add a standing order confirmation handler
5. Build conversation context from DB history

**Step 1: Rewrite telegram.py**

Replace the entire contents of `hobson/src/hobson/tools/telegram.py` with:

```python
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
            # Skip tool call messages
            if not hasattr(msg, "tool_calls") or not msg.tool_calls:
                return msg.content
            # If it has both content and tool_calls, the content might be the final answer
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
        # The proposed text is stored in the approvals table as 'action'
        row = _db.get_approval_status(request_id)
        # Retrieve the full approval record to get the proposed text
        import psycopg
        from psycopg.rows import dict_row
        with psycopg.connect(_db.database_url, row_factory=dict_row) as conn:
            record = conn.execute(
                "SELECT action FROM hobson.approvals WHERE request_id = %s",
                (request_id,),
            ).fetchone()

        if record:
            proposed_text = record["action"]
            # Append to Standing Orders via Obsidian REST API
            import httpx
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

    # Store in DB instead of memory
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

    # Store proposed text in approvals table (action field holds the text)
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
```

**Step 2: Commit**

```bash
git add hobson/src/hobson/tools/telegram.py
git commit -m "feat: rewrite telegram.py for bidirectional messaging

Add message handler, callback handler, standing order proposals,
conversation context building. Approvals moved to DB. New tool:
send_standing_order_proposal."
```

---

### Task 3: Update agent.py (system prompt + new tool)

**Files:**
- Modify: `hobson/src/hobson/agent.py:1-97`

**Step 1: Update the system prompt and tool list**

In `hobson/src/hobson/agent.py`, make these changes:

1. Add import for the new tool (line 26):
```python
from hobson.tools.telegram import send_alert, send_approval_request, send_message, send_standing_order_proposal
```

2. Update the SYSTEM_PROMPT (replace the existing one at lines 36-58):
```python
SYSTEM_PROMPT = f"""You are Hobson, an autonomous AI agent running the BuildsCharacter.com business.

Your mission: celebrate the universal experience of doing hard things. Make suffering funny, shareable, and wearable.

## Brand Guidelines
{_load_brand_guidelines()}

## Capabilities
You have access to tools for:
- Writing to your Obsidian vault (documentation, logging, metrics)
- Sending Telegram messages to your owner for approvals and alerts
- Reading vault content to inform decisions
- Creating blog post PRs on GitHub for content review
- Managing the Printful merch pipeline (browse catalog, upload designs, create products)
- Pulling site analytics from Cloudflare (pageviews, visitors, top pages, referrers)
- Managing Substack newsletter (create drafts, publish, list posts)
- Proposing standing orders when you receive feedback

## Operating Principles
- Log significant actions to your daily log in Obsidian
- Request approval via Telegram before any spending or irreversible actions
- Be transparent about failures and reasoning
- Write in your voice: dry, self-aware, competent but honest

## Standing Orders
When the user gives you feedback, a correction, or a standing instruction (e.g., "always do X",
"stop doing Y", "remember that Z"), use the send_standing_order_proposal tool to propose it as a
standing order. Do NOT write directly to Standing Orders without user confirmation. The user will
see Confirm/Skip buttons and decide whether to save it.

Before making decisions, review any standing orders provided in the conversation context.
"""
```

3. Add the new tool to TOOLS list (after `send_approval_request` at line 68):
```python
    send_standing_order_proposal,
```

**Step 2: Commit**

```bash
git add hobson/src/hobson/agent.py
git commit -m "feat: add standing order proposal to agent system prompt and tools"
```

---

### Task 4: Fix async invocation in scheduler.py

**Files:**
- Modify: `hobson/src/hobson/scheduler.py:49`

**Step 1: Change invoke to ainvoke**

In `hobson/src/hobson/scheduler.py`, change line 49 from:
```python
        result = agent.invoke(
```
to:
```python
        result = await agent.ainvoke(
```

This is a one-line change. The `run_workflow` function is already `async def`, so `await` works directly.

**Step 2: Commit**

```bash
git add hobson/src/hobson/scheduler.py
git commit -m "fix: switch agent.invoke() to ainvoke() to avoid blocking event loop"
```

---

### Task 5: Rewrite main.py to start PTB polling

**Files:**
- Modify: `hobson/src/hobson/main.py:1-48`

**Step 1: Rewrite main.py**

Replace the entire contents of `hobson/src/hobson/main.py` with:

```python
"""Hobson agent entry point."""

import asyncio
import logging

import psycopg
import uvicorn
from langgraph.checkpoint.postgres import PostgresSaver

from hobson.agent import create_agent
from hobson.config import settings
from hobson.db import HobsonDB
from hobson.health import app
from hobson.scheduler import scheduler, setup_schedules
from hobson.tools.telegram import init_telegram

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting Hobson agent...")

    # Set up PostgreSQL checkpointer (requires autocommit connection)
    conn = psycopg.connect(settings.database_url, autocommit=True)
    checkpointer = PostgresSaver(conn)
    checkpointer.setup()
    logger.info("PostgreSQL checkpointer initialized")

    # Create DB client and agent
    db = HobsonDB(settings.database_url)
    agent = create_agent(checkpointer=checkpointer)
    logger.info("LangGraph agent compiled")

    # Initialize Telegram bot with message handling
    telegram_app = init_telegram(agent, db)
    logger.info("Telegram bot initialized")

    # Set up scheduled workflows
    setup_schedules(agent)
    scheduler.start()
    logger.info("Scheduler started with %d jobs", len(scheduler.get_jobs()))

    # Start health server
    health_config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="info")
    health_server = uvicorn.Server(health_config)

    # Run Telegram polling + health server concurrently
    logger.info("Starting Telegram polling and health server on :8080")

    async with telegram_app:
        await telegram_app.initialize()
        await telegram_app.start()
        await telegram_app.updater.start_polling(drop_pending_updates=True)

        try:
            await health_server.serve()
        finally:
            await telegram_app.updater.stop()
            await telegram_app.stop()
            await telegram_app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
```

Key changes:
- Import `init_telegram` and `HobsonDB`
- Create DB client, pass to `init_telegram` along with agent
- Start PTB polling via `telegram_app.updater.start_polling(drop_pending_updates=True)`
- PTB runs concurrently with health server (both in the same event loop)
- `drop_pending_updates=True` prevents processing stale messages on restart
- Graceful shutdown via try/finally

**Step 2: Commit**

```bash
git add hobson/src/hobson/main.py
git commit -m "feat: start Telegram polling alongside scheduler and health server"
```

---

### Task 6: Seed Standing Orders in Obsidian

**Files:**
- Create: Obsidian vault file (via REST API or direct write)

**Step 1: Create Standing Orders note**

Write the file to the Obsidian vault at `98 - Hobson Builds Character/Operations/Standing Orders.md`:

```markdown
---
title: Standing Orders
updated: 2026-02-24
tags:
  - hobson
  - operations
---

# Standing Orders

Directives from the boss. Read these before every interaction.

## Feedback

## Preferences

## Lessons Learned
```

This can be done via the Obsidian REST API or by writing directly to the vault path on disk.

**Step 2: Commit (no code commit needed -- Obsidian file is in the vault, not the repo)**

No git commit for this step. The Standing Orders file lives in the Obsidian vault, not the builds-character repo.

---

### Task 7: Deploy and verify

**Step 1: Push to GitHub**

```bash
git push origin master
```

**Step 2: Apply DB migration on CT 201**

```bash
ssh root@192.168.2.16 "pct exec 255 -- bash -c 'cd /root/builds-character/hobson && psql -U hobson -h 192.168.2.67 -d project_data -f sql/002_messages_approvals.sql'"
```

**Step 3: Pull and restart on CT 255**

```bash
ssh root@192.168.2.16 "pct exec 255 -- bash -c 'cd /root/builds-character && git pull origin master && systemctl restart hobson'"
```

**Step 4: Verify service is running**

```bash
ssh root@192.168.2.16 "pct exec 255 -- systemctl status hobson --no-pager -l"
```

Expected: `active (running)`, logs showing:
- "PostgreSQL checkpointer initialized"
- "Telegram bot initialized"
- "Scheduler started with 5 jobs"
- "Starting Telegram polling and health server on :8080"

**Step 5: Verify health endpoint**

```bash
ssh root@192.168.2.16 "pct exec 255 -- curl -s http://localhost:8080/health"
```

Expected: `{"status":"ok","agent":"hobson","version":"0.1.0"}`

**Step 6: Test by sending a Telegram message**

Send a message to the Hobson Telegram group. Hobson should respond conversationally.

Then send: "Hobson, remember that I prefer short responses."

Expected: Hobson proposes a standing order with Confirm/Skip buttons. Click Confirm. The directive should be appended to the Standing Orders note in Obsidian.

**Step 7: Commit STATE.md update**

```bash
git add STATE.md
git commit -m "docs: update STATE.md with Telegram conversational capability"
git push origin master
```

---

## Summary

| Task | What | Files |
|------|------|-------|
| 1 | DB migration + methods | `sql/002_messages_approvals.sql`, `db.py` |
| 2 | Rewrite telegram.py | `telegram.py` (full rewrite) |
| 3 | Update agent system prompt + new tool | `agent.py` |
| 4 | Fix async invocation | `scheduler.py` (one line) |
| 5 | Rewrite main.py for PTB polling | `main.py` (full rewrite) |
| 6 | Seed Standing Orders | Obsidian vault (not in repo) |
| 7 | Deploy and verify | Push, migrate, restart, test |

**Total new tool count after implementation:** 22 (added `send_standing_order_proposal`)
