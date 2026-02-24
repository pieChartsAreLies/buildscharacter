# Hobson Telegram Conversational Capability Design

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement the corresponding implementation plan.

**Goal:** Make Hobson a bidirectional Telegram participant -- receiving messages, responding conversationally, learning from feedback, and handling approval button callbacks.

**Date:** 2026-02-24

## Problem

Hobson is currently outbound-only on Telegram. He can send messages, alerts, and approval requests, but cannot receive messages, respond to questions, or process approval button clicks. The `handle_callback()` function exists but is never registered. Approval state is stored in memory and lost on restart.

The user needs Hobson to act like an employee: available for discussion, capable of taking feedback, and able to learn from mistakes.

## Architecture

Add python-telegram-bot (PTB) long-polling to the existing `main.py` process, running alongside APScheduler and FastAPI. When a message arrives, build conversation context from a new PostgreSQL `messages` table, load standing orders from Obsidian, and invoke the same LangGraph agent with `ainvoke()`.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LLM for conversation | Gemini 2.5 Flash | Same model as workflows. Free tier. Avoids Claude quota pressure from Bob/Tim |
| Polling vs webhook | PTB polling | No public HTTPS endpoint needed. PTB already a dependency |
| Single vs multi-process | Single process | Simple. PTB, APScheduler, and FastAPI coexist in one event loop |
| Memory model | Obsidian Standing Orders file | Human-readable, inspectable, editable. Loaded at every invocation |
| Trigger mode | Every message (dedicated channel) | Assumes dedicated Hobson chat. No @mention filtering needed |
| Context window | Last 20 messages | Enough for conversation threading without excessive token cost |

## Component 1: Message Reception & Storage

**PTB Application:** Create a `telegram.ext.Application` in `main.py` with:
- `MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)` for text messages
- `CallbackQueryHandler(handle_callback)` for approval button presses

**Message Storage:** New `hobson.messages` PostgreSQL table:

```sql
CREATE TABLE hobson.messages (
    id SERIAL PRIMARY KEY,
    chat_id TEXT NOT NULL,
    sender_name TEXT NOT NULL,
    content TEXT NOT NULL,
    is_from_hobson BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_messages_chat_timestamp ON hobson.messages (chat_id, timestamp DESC);
```

Every incoming message stored. Every Hobson response stored with `is_from_hobson=true`. Conversation history survives restarts.

**Context Building:** On each message, fetch last 20 messages from the table for that `chat_id`, format chronologically, pass as conversation history to the agent.

## Component 2: Agent Invocation for Conversation

**Async Fix:** Change `agent.invoke()` to `await agent.ainvoke()` in both `scheduler.py` (workflows) and the new Telegram handler. This stops the event loop from blocking during agent execution.

**Thread ID:** Use `thread_id: "telegram-{chat_id}"` for conversations, separate from workflow thread IDs (`workflow-morning_briefing`, etc.).

**Invocation Flow:**
1. Message arrives via PTB handler
2. Store message in `hobson.messages`
3. Fetch last 20 messages from DB for context
4. Load standing orders from Obsidian via `read_note`
5. Build conversation prompt: system prompt + standing orders + recent messages + new message
6. `await agent.ainvoke()` with `thread_id: "telegram-{chat_id}"`
7. Store Hobson's response in `hobson.messages` with `is_from_hobson=true`
8. Send response via Telegram

**Concurrency Guard:** Track chat IDs currently being processed in a `Set`. PTB's update queue handles message queuing naturally.

## Component 3: Standing Orders (Learning & Memory)

**Obsidian File:** `98 - Hobson Builds Character/Operations/Standing Orders.md`

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

**Mechanism:** System prompt instructs Hobson: "When the user gives feedback, a correction, or a standing instruction, append it to Standing Orders using `append_to_note`. Before making decisions, check Standing Orders first."

Standing orders content loaded into conversation prompt at every invocation (both Telegram conversations and scheduled workflows). Learnings carry forward everywhere.

The user can edit Standing Orders directly in Obsidian at any time.

## Component 4: Approval Button Callbacks

**New table:** `hobson.approvals`

```sql
CREATE TABLE hobson.approvals (
    request_id TEXT PRIMARY KEY,
    action TEXT NOT NULL,
    reasoning TEXT,
    estimated_cost FLOAT DEFAULT 0,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);
```

Replace in-memory `_pending_approvals` dict. `CallbackQueryHandler` registered on PTB Application updates the row and edits the Telegram message. Workflows poll the table for approval status.

Survives restarts. Auditable.

## Component 5: Startup Sequence

`main.py` startup becomes:
1. Connect to PostgreSQL, set up checkpointer
2. Run new DB migrations (messages + approvals tables)
3. Create LangGraph agent
4. Build PTB Application with message handler + callback handler
5. Set up APScheduler with 5 workflows
6. Start all three concurrently: PTB polling + APScheduler + FastAPI health server

## Files Changed

| File | Change |
|------|--------|
| `main.py` | Add PTB Application, run polling alongside scheduler and health server |
| `telegram.py` | Add message handler, callback handler, context builder. Refactor send functions to use shared PTB Application |
| `db.py` | Add messages table methods (store, fetch recent) and approvals table methods (create, update, get status) |
| `scheduler.py` | Change `agent.invoke()` to `await agent.ainvoke()` |
| `agent.py` | Update system prompt to include standing orders and feedback-capture instructions |
| `sql/002_messages_approvals.sql` | New migration for messages + approvals tables |
| Obsidian vault | Seed `Standing Orders.md` |

## What Doesn't Change

All 21 existing tools, all 5 workflow prompts, `config.py` (telegram_bot_token and telegram_chat_id already exist), the health endpoint, Uptime Kuma push monitors.

## Error Handling

If the agent fails during a Telegram conversation, Hobson sends a brief error message to the chat rather than silently failing. Errors logged to `run_log` same as workflows.
