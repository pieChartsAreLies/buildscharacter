# BuildsCharacter.com + Hobson Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a content-driven brand at buildscharacter.com operated by an autonomous AI agent (Hobson) that documents everything in Obsidian and narrates the journey on Substack.

**Architecture:** Python LangGraph agent on an LXC container (Loki), with APScheduler for cron workflows, PostgreSQL for state/traces, Telegram for human-in-the-loop, and Astro for the website on Cloudflare Pages. Incremental build: monolithic agent first, sub-agents extracted after stability.

**Tech Stack:** Python 3.12+, LangGraph, APScheduler, httpx, python-telegram-bot, langchain-anthropic, Astro (site), PostgreSQL (CT 201), Grafana (CT 180), Uptime Kuma, Cloudflare Pages

---

## Prerequisites (Manual, Owner-Performed)

These must be done before implementation begins. They require account creation, credential generation, or homelab access that cannot be automated from a dev machine.

### P1: Register Telegram Bot

1. Message @BotFather on Telegram
2. `/newbot` -> Name: "Hobson" -> Username: `HobsonBuildsCharacter_bot` (or similar available name)
3. Save the bot token to Bitwarden under "Hobson Telegram Bot"
4. Create a Telegram group for Hobson communications
5. Add the bot to the group
6. Get the group chat ID (send a message, then `https://api.telegram.org/bot<TOKEN>/getUpdates`)
7. Record chat ID in Bitwarden

### P2: Create Printful Account

1. Sign up at printful.com
2. Generate a Private API Token in Developer Portal (Dashboard > Settings > API)
3. Save token to Bitwarden under "Hobson Printful API"

### P3: Create Substack Publication

1. Go to substack.com, create account
2. Create publication: "Hobson Builds Character" (or preferred name)
3. Set up the publication (title, description, about page)
4. Log in via browser, open DevTools, capture session cookies
5. Save cookies to Bitwarden under "Hobson Substack Cookies"
6. Note: cookies expire periodically and will need refreshing

### P4: Create Social Media Accounts

1. Instagram: @buildscharacter (or available variant)
2. X/Twitter: @buildscharacter (or available variant)
3. TikTok: @buildscharacter (or available variant)
4. Save credentials to Bitwarden

### P5: Create GitHub Repo

1. Create `buildscharacter` repo on GitHub (or Gitea if self-hosted)
2. This will host the website source. Hobson will open PRs here for content review.
3. Connect to Cloudflare Pages (Settings > Pages > Create project > Connect to Git)

### P6: Move Overseerr Tunnel

1. In Cloudflare dashboard, change the Overseerr tunnel from `buildscharacter.com` to `overseerr.buildscharacter.com` (or another subdomain)
2. Free up the root domain for the website

---

## Phase 1: Project Scaffolding & Infrastructure

### Task 1: Hobson Python Project Structure

**Files:**
- Create: `hobson/` directory structure (within builds-character repo or separate repo)
- Create: `hobson/pyproject.toml`
- Create: `hobson/src/hobson/__init__.py`
- Create: `hobson/src/hobson/config.py`
- Create: `hobson/src/hobson/agent.py`
- Create: `hobson/.env.example`
- Create: `hobson/.gitignore`
- Create: `hobson/README.md`

**Step 1: Create directory structure**

```
builds-character/
├── hobson/                         # Agent codebase
│   ├── src/
│   │   └── hobson/
│   │       ├── __init__.py
│   │       ├── config.py           # Environment config (pydantic-settings)
│   │       ├── agent.py            # LangGraph agent definition
│   │       ├── tools/              # Tool implementations
│   │       │   ├── __init__.py
│   │       │   ├── obsidian.py     # Obsidian REST API client
│   │       │   ├── printful.py     # Printful API client
│   │       │   ├── analytics.py    # Umami API client
│   │       │   ├── substack.py     # Substack client (fragile)
│   │       │   ├── telegram.py     # Telegram bot for HITL
│   │       │   └── git_ops.py      # Git operations for PR workflow
│   │       ├── workflows/          # Scheduled workflow definitions
│   │       │   ├── __init__.py
│   │       │   ├── morning_briefing.py
│   │       │   ├── content_pipeline.py
│   │       │   ├── design_batch.py
│   │       │   ├── substack_dispatch.py
│   │       │   └── business_review.py
│   │       ├── db.py               # PostgreSQL operations
│   │       ├── scheduler.py        # APScheduler setup
│   │       ├── health.py           # Health endpoint for Uptime Kuma
│   │       └── main.py             # Entry point
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_config.py
│   │   ├── test_tools/
│   │   │   ├── test_obsidian.py
│   │   │   ├── test_printful.py
│   │   │   ├── test_analytics.py
│   │   │   └── test_telegram.py
│   │   ├── test_db.py
│   │   └── test_workflows/
│   │       └── test_morning_briefing.py
│   ├── pyproject.toml
│   ├── .env.example
│   └── .gitignore
├── site/                           # Astro website
│   └── (created in Phase 2)
├── brand/
│   └── brand_guidelines.md         # Machine-readable brand spec
├── docs/
│   └── plans/                      # Design + implementation docs
├── PROJECT.md
└── STATE.md
```

**Step 2: Write pyproject.toml**

```toml
[project]
name = "hobson"
version = "0.1.0"
description = "Hobson: Autonomous business agent for BuildsCharacter.com"
requires-python = ">=3.12"
dependencies = [
    "langgraph>=0.3",
    "langgraph-checkpoint-postgres>=3.0",
    "langchain-anthropic>=0.3",
    "langchain-google-genai>=2.0",
    "apscheduler>=3.10,<4",
    "httpx>=0.27",
    "python-telegram-bot>=21",
    "psycopg[binary]>=3.2",
    "pydantic-settings>=2.0",
    "uvicorn>=0.30",
    "fastapi>=0.115",
    "python-substack>=0.2",
    "umami-analytics>=0.3",
    "pillow>=10",
]

[project.optional-dependencies]
dev = [
    "pytest>=8",
    "pytest-asyncio>=0.24",
    "pytest-httpx>=0.30",
    "ruff>=0.5",
]

[tool.ruff]
target-version = "py312"
line-length = 100

[tool.pytest.ini_options]
asyncio_mode = "auto"
```

**Step 3: Write config.py**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLM
    anthropic_api_key: str = ""  # Only if not using Claude Max CLI
    google_api_key: str = ""     # Gemini
    ollama_base_url: str = "http://192.168.2.71:11434"

    # PostgreSQL
    database_url: str = "postgresql://hobson:password@192.168.2.67:5432/project_data"

    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Printful
    printful_api_key: str = ""

    # Obsidian
    obsidian_host: str = "192.168.2.140"
    obsidian_port: int = 27124
    obsidian_api_key: str = ""

    # Umami
    umami_base_url: str = ""
    umami_username: str = ""
    umami_password: str = ""
    umami_website_id: str = ""

    # Substack
    substack_cookies: str = ""  # Session cookies (fragile)

    # Uptime Kuma
    uptime_kuma_push_url: str = ""  # Push monitor URL

    # Cost controls
    monthly_cost_cap: float = 50.0
    single_action_cost_threshold: float = 5.0

    # Agent
    brand_guidelines_path: str = "brand/brand_guidelines.md"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
```

**Step 4: Write .env.example**

```bash
# LLM
ANTHROPIC_API_KEY=        # Only if using API, not Claude Max CLI
GOOGLE_API_KEY=           # Gemini API key (free tier)

# PostgreSQL (CT 201 on Freya)
DATABASE_URL=postgresql://hobson:<password>@192.168.2.67:5432/project_data

# Telegram (from BotFather)
TELEGRAM_BOT_TOKEN=       # See Bitwarden: Hobson Telegram Bot
TELEGRAM_CHAT_ID=         # Group chat ID

# Printful
PRINTFUL_API_KEY=         # See Bitwarden: Hobson Printful API

# Obsidian REST API
OBSIDIAN_HOST=192.168.2.140
OBSIDIAN_PORT=27124
OBSIDIAN_API_KEY=         # See Bitwarden: Obsidian API

# Umami Analytics
UMAMI_BASE_URL=           # Self-hosted Umami URL
UMAMI_USERNAME=admin
UMAMI_PASSWORD=           # See Bitwarden
UMAMI_WEBSITE_ID=         # From Umami dashboard

# Substack (fragile, expires periodically)
SUBSTACK_COOKIES=         # See Bitwarden: Hobson Substack Cookies

# Uptime Kuma
UPTIME_KUMA_PUSH_URL=    # Push monitor URL from Uptime Kuma

# Cost controls
MONTHLY_COST_CAP=50.0
SINGLE_ACTION_COST_THRESHOLD=5.0
```

**Step 5: Write .gitignore**

```
.env
__pycache__/
*.pyc
.ruff_cache/
.pytest_cache/
dist/
*.egg-info/
.venv/
```

**Step 6: Commit**

```bash
git add hobson/ brand/
git commit -m "feat: scaffold Hobson agent project structure"
```

---

### Task 2: Brand Guidelines File

**Files:**
- Create: `brand/brand_guidelines.md`

**Step 1: Write brand_guidelines.md**

This is the machine-readable spec loaded into Hobson's system prompt for every generation task. Copy the brand guidelines from the design document with the full voice spec, rules, example headlines (on-brand and off-brand), anti-keywords, and mission statement.

**Step 2: Commit**

```bash
git add brand/brand_guidelines.md
git commit -m "feat: add machine-readable brand guidelines"
```

---

### Task 3: PostgreSQL Schema

**Files:**
- Create: `hobson/sql/001_schema.sql`

**Requires:** SSH access to Freya (192.168.2.13), then `pct exec 201` to access PostgreSQL CT.

**Step 1: Write migration SQL**

```sql
-- Create hobson schema and user
CREATE SCHEMA IF NOT EXISTS hobson;

-- Create hobson database user (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'hobson') THEN
        CREATE ROLE hobson WITH LOGIN PASSWORD '<from_bitwarden>';
    END IF;
END $$;

GRANT USAGE ON SCHEMA hobson TO hobson;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA hobson TO hobson;
ALTER DEFAULT PRIVILEGES IN SCHEMA hobson GRANT ALL ON TABLES TO hobson;

-- Goals
CREATE TABLE IF NOT EXISTS hobson.goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quarter TEXT NOT NULL,               -- e.g., "2026-Q1"
    objective TEXT NOT NULL,
    key_results JSONB NOT NULL DEFAULT '[]',
    progress DECIMAL(5,2) DEFAULT 0,
    status TEXT DEFAULT 'active',        -- active, achieved, abandoned
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tasks
CREATE TABLE IF NOT EXISTS hobson.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT DEFAULT 'medium',      -- low, medium, high, critical
    status TEXT DEFAULT 'pending',       -- pending, in_progress, done, blocked
    due_date DATE,
    goal_id UUID REFERENCES hobson.goals(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Decisions
CREATE TABLE IF NOT EXISTS hobson.decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    outcome TEXT,
    category TEXT,                       -- strategy, content, design, spend, technical
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Metrics (daily snapshots)
CREATE TABLE IF NOT EXISTS hobson.metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    metric_type TEXT NOT NULL,           -- traffic, revenue, social, substack, costs
    data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(date, metric_type)
);

-- Content inventory
CREATE TABLE IF NOT EXISTS hobson.content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content_type TEXT NOT NULL,          -- blog, social, substack, email
    status TEXT DEFAULT 'draft',         -- draft, review, published, retired
    slug TEXT,
    url TEXT,
    metadata JSONB DEFAULT '{}',
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Design inventory
CREATE TABLE IF NOT EXISTS hobson.designs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'concept',       -- concept, production, live, retired
    printful_product_id TEXT,
    image_url TEXT,
    performance JSONB DEFAULT '{}',      -- {views, sales, revenue}
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Run log (immutable execution traces)
CREATE TABLE IF NOT EXISTS hobson.run_log (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'running', -- running, success, failed, timeout
    inputs JSONB DEFAULT '{}',
    outputs JSONB DEFAULT '{}',
    error TEXT,
    node_transitions JSONB DEFAULT '[]',
    cost_estimate DECIMAL(10,4) DEFAULT 0,
    llm_provider TEXT,                   -- claude, gemini, ollama
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Cost tracking
CREATE TABLE IF NOT EXISTS hobson.cost_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES hobson.run_log(run_id),
    provider TEXT NOT NULL,              -- gemini, anthropic, ollama, etc.
    action TEXT NOT NULL,                -- image_generation, api_call, etc.
    estimated_cost DECIMAL(10,4) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_run_log_workflow ON hobson.run_log(workflow);
CREATE INDEX IF NOT EXISTS idx_run_log_status ON hobson.run_log(status);
CREATE INDEX IF NOT EXISTS idx_run_log_started ON hobson.run_log(started_at);
CREATE INDEX IF NOT EXISTS idx_metrics_date ON hobson.metrics(date);
CREATE INDEX IF NOT EXISTS idx_content_status ON hobson.content(status);
CREATE INDEX IF NOT EXISTS idx_cost_log_created ON hobson.cost_log(created_at);
```

**Step 2: Apply migration**

```bash
ssh root@192.168.2.13
pct exec 201 -- psql -U postgres -d project_data -f /tmp/001_schema.sql
```

(Use `pct push 201` to transfer the SQL file first.)

**Step 3: Verify**

```bash
pct exec 201 -- psql -U hobson -d project_data -c "\\dt hobson.*"
```

Expected: All 8 tables listed.

**Step 4: Commit**

```bash
git add hobson/sql/001_schema.sql
git commit -m "feat: add PostgreSQL schema for Hobson state management"
```

---

### Task 4: Provision Hobson LXC Container

**Requires:** SSH to Loki (192.168.2.16). This is a manual/assisted task.

**Step 1: Create container**

```bash
ssh root@192.168.2.16
pct create <CTID> local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst \
    --hostname hobson \
    --memory 2048 \
    --cores 2 \
    --rootfs local-lvm:8 \
    --net0 name=eth0,bridge=vmbr0,ip=dhcp \
    --start 1
```

Pick an available CTID (check with `pct list`). Record the IP after start.

**Step 2: Install Python 3.12+ and dependencies**

```bash
pct exec <CTID> -- bash -c "
    apt update && apt install -y python3 python3-pip python3-venv git curl
    python3 --version  # Verify 3.12+
"
```

**Step 3: Clone repo and set up environment**

```bash
pct exec <CTID> -- bash -c "
    cd /root
    git clone <REPO_URL> builds-character
    cd builds-character/hobson
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e '.[dev]'
"
```

**Step 4: Create .env from .env.example**

Populate from Bitwarden credentials.

**Step 5: Verify connectivity**

```bash
# Test PostgreSQL
pct exec <CTID> -- bash -c "
    cd /root/builds-character/hobson
    source .venv/bin/activate
    python3 -c \"import psycopg; conn = psycopg.connect('postgresql://hobson:pass@192.168.2.67:5432/project_data'); print('PG OK')\"
"

# Test Obsidian API
pct exec <CTID> -- bash -c "curl -s -H 'Authorization: Bearer <token>' http://192.168.2.140:27124/vault/ | head -c 200"

# Test Ollama
pct exec <CTID> -- bash -c "curl -s http://192.168.2.71:11434/api/tags | head -c 200"
```

**Step 6: Update homelab docs**

Update `homelab-docs/docs/services/containers.md` with new Hobson container entry.
Update `homelab-docs/docs/operations/changelog.md`.

---

### Task 5: Obsidian Vault Structure

**Requires:** Obsidian REST API access (192.168.2.140:27124)

**Step 1: Create vault directory structure and initial files**

Use the Obsidian REST API (or CLI) to create:

```
98 - Hobson Builds Character/
├── Dashboard.md
├── Strategy/
│   ├── Business Plan.md
│   ├── Decisions Log.md
│   ├── Brand Guidelines.md
│   ├── Quarterly Goals.md
│   └── Playbook Notes.md
├── Content/
│   ├── Blog/
│   │   ├── Drafts/     (.gitkeep)
│   │   ├── Published/  (.gitkeep)
│   │   └── Content Calendar.md
│   ├── Social/
│   │   ├── Ideas/      (.gitkeep)
│   │   └── Scheduled/  (.gitkeep)
│   ├── Designs/
│   │   ├── Concepts/   (.gitkeep)
│   │   └── Production/ (.gitkeep)
│   └── Substack/
│       ├── Drafts/     (.gitkeep)
│       ├── Published/  (.gitkeep)
│       └── Reader Polls.md
├── Operations/
│   ├── Daily Log.md
│   ├── Weekly Review.md
│   ├── Task Queue.md
│   ├── Incident Log.md
│   └── Metrics/
│       ├── Traffic.md
│       ├── Revenue.md
│       ├── Social.md
│       ├── Substack.md
│       └── Costs.md
└── Architecture/
    ├── System Design.md
    └── Agent Workflows.md
```

Each `.md` file gets an initial template with YAML frontmatter and section headers appropriate to its purpose.

**Step 2: Populate Dashboard.md**

```markdown
---
title: Hobson Dashboard
updated: 2026-02-23
---

# Dashboard

## Current Focus
Setting up infrastructure and initial agent capabilities.

## Key Metrics
| Metric | Value | Trend |
|--------|-------|-------|
| Site Traffic | 0 | - |
| Merch Revenue | $0 | - |
| Substack Subscribers | 0 | - |
| Designs Live | 0 | - |
| Blog Posts | 0 | - |

## Status
- Infrastructure: In Progress
- Agent: Not Started
- Website: Not Started
- Substack: Not Started

*Updated automatically by Hobson's morning briefing workflow.*
```

**Step 3: Populate initial Decisions Log**

Copy decisions from design document into `Strategy/Decisions Log.md`.

---

## Phase 2: The Website

### Task 6: Scaffold Astro Site

**Files:**
- Create: `site/` directory with Astro project

**Step 1: Initialize Astro project**

```bash
cd /Users/llama/Development/builds-character
npm create astro@latest site -- --template minimal --typescript strict --install --git false
```

**Step 2: Install dependencies**

```bash
cd site
npm install @astrojs/tailwind @astrojs/sitemap
```

**Step 3: Configure astro.config.mjs**

```javascript
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://buildscharacter.com',
  integrations: [tailwind(), sitemap()],
  output: 'static',
});
```

**Step 4: Create base layout**

Create `site/src/layouts/Base.astro` with:
- HTML boilerplate, meta tags, Open Graph tags
- Navigation (Home, Shop, Blog, Dashboard, About)
- Footer with Substack link
- Brand font and color scheme from brand_guidelines.md

**Step 5: Create pages**

- `site/src/pages/index.astro` -- Landing page with brand messaging and featured merch
- `site/src/pages/shop.astro` -- Printful storefront embed (placeholder for now)
- `site/src/pages/blog/index.astro` -- Blog listing page
- `site/src/pages/blog/[...slug].astro` -- Blog post template (reads from `site/src/content/blog/`)
- `site/src/pages/dashboard.astro` -- Grafana embed (placeholder iframe)
- `site/src/pages/about.astro` -- About page explaining the project, introducing Hobson

**Step 6: Set up content collections**

```typescript
// site/src/content/config.ts
import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.date(),
    author: z.string().default('Hobson'),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
  }),
});

export const collections = { blog };
```

**Step 7: Add a sample blog post**

Create `site/src/content/blog/hello-world.md`:

```markdown
---
title: "It Begins: An AI Agent Starts a Business"
description: "Hobson here. I've been given a domain, a budget, and instructions to build something. This is how it starts."
pubDate: 2026-02-23
author: Hobson
tags: [meta, launch]
---

Content TBD -- this will be Hobson's first post.
```

**Step 8: Build and verify locally**

```bash
cd site && npm run dev
# Visit http://localhost:4321
```

**Step 9: Commit**

```bash
git add site/
git commit -m "feat: scaffold Astro website with blog, shop, and dashboard pages"
```

---

### Task 7: Cloudflare Pages Deployment

**Requires:** Cloudflare account access, GitHub repo (from P6)

**Step 1: Push site to GitHub**

```bash
git remote add origin <GITHUB_REPO_URL>
git push -u origin main
```

**Step 2: Connect Cloudflare Pages**

In Cloudflare dashboard:
1. Pages > Create a project > Connect to Git
2. Select the repo
3. Build settings:
   - Framework preset: Astro
   - Build command: `cd site && npm install && npm run build`
   - Build output directory: `site/dist`
4. Deploy

**Step 3: Configure custom domain**

1. Pages > Custom domains > Add: `buildscharacter.com`
2. Cloudflare auto-configures DNS since the domain is already on Cloudflare

**Step 4: Verify**

Visit `https://buildscharacter.com` -- should show the Astro site.

**Step 5: Commit any config changes**

---

## Phase 3: Hobson Core Agent

### Task 8: Database Client

**Files:**
- Create: `hobson/src/hobson/db.py`
- Test: `hobson/tests/test_db.py`

**Step 1: Write failing test**

```python
# tests/test_db.py
import pytest
from hobson.db import HobsonDB

@pytest.fixture
def db(tmp_path):
    """Use a test database URL or mock."""
    return HobsonDB("postgresql://test:test@localhost:5432/test_hobson")

def test_log_run_creates_record(db):
    run_id = db.log_run_start(workflow="test_workflow", inputs={"key": "value"})
    assert run_id is not None

def test_log_run_complete(db):
    run_id = db.log_run_start(workflow="test", inputs={})
    db.log_run_complete(run_id, status="success", outputs={"result": "ok"})
    run = db.get_run(run_id)
    assert run["status"] == "success"

def test_log_decision(db):
    db.log_decision(decision="Test decision", reasoning="Because", category="test")

def test_get_daily_costs(db):
    total = db.get_daily_cost_total()
    assert isinstance(total, float)

def test_get_monthly_costs(db):
    total = db.get_monthly_cost_total()
    assert isinstance(total, float)
```

**Step 2: Run test to verify it fails**

```bash
cd hobson && python -m pytest tests/test_db.py -v
```

Expected: ImportError (module doesn't exist yet)

**Step 3: Implement db.py**

```python
# src/hobson/db.py
import uuid
from datetime import datetime, date
from decimal import Decimal
import psycopg
from psycopg.rows import dict_row

class HobsonDB:
    def __init__(self, database_url: str):
        self.database_url = database_url

    def _conn(self):
        return psycopg.connect(self.database_url, row_factory=dict_row)

    def log_run_start(self, workflow: str, inputs: dict, llm_provider: str = None) -> str:
        run_id = str(uuid.uuid4())
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO hobson.run_log (run_id, workflow, inputs, llm_provider, status)
                   VALUES (%s, %s, %s, %s, 'running')""",
                (run_id, workflow, psycopg.types.json.Json(inputs), llm_provider),
            )
        return run_id

    def log_run_complete(self, run_id: str, status: str, outputs: dict = None, error: str = None):
        with self._conn() as conn:
            conn.execute(
                """UPDATE hobson.run_log
                   SET status = %s, completed_at = NOW(), outputs = %s, error = %s
                   WHERE run_id = %s""",
                (status, psycopg.types.json.Json(outputs or {}), error, run_id),
            )

    def get_run(self, run_id: str) -> dict:
        with self._conn() as conn:
            return conn.execute(
                "SELECT * FROM hobson.run_log WHERE run_id = %s", (run_id,)
            ).fetchone()

    def log_decision(self, decision: str, reasoning: str, category: str = None, outcome: str = None):
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO hobson.decisions (decision, reasoning, category, outcome)
                   VALUES (%s, %s, %s, %s)""",
                (decision, reasoning, category, outcome),
            )

    def log_cost(self, run_id: str, provider: str, action: str, estimated_cost: float):
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO hobson.cost_log (run_id, provider, action, estimated_cost)
                   VALUES (%s, %s, %s, %s)""",
                (run_id, provider, action, estimated_cost),
            )

    def get_daily_cost_total(self, target_date: date = None) -> float:
        target_date = target_date or date.today()
        with self._conn() as conn:
            result = conn.execute(
                """SELECT COALESCE(SUM(estimated_cost), 0) as total
                   FROM hobson.cost_log WHERE created_at::date = %s""",
                (target_date,),
            ).fetchone()
            return float(result["total"])

    def get_monthly_cost_total(self) -> float:
        with self._conn() as conn:
            result = conn.execute(
                """SELECT COALESCE(SUM(estimated_cost), 0) as total
                   FROM hobson.cost_log
                   WHERE date_trunc('month', created_at) = date_trunc('month', NOW())""",
            ).fetchone()
            return float(result["total"])

    def log_metric(self, metric_type: str, data: dict, target_date: date = None):
        target_date = target_date or date.today()
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO hobson.metrics (date, metric_type, data)
                   VALUES (%s, %s, %s)
                   ON CONFLICT (date, metric_type) DO UPDATE SET data = EXCLUDED.data""",
                (target_date, metric_type, psycopg.types.json.Json(data)),
            )
```

**Step 4: Run tests**

```bash
python -m pytest tests/test_db.py -v
```

Note: Tests will need either a test PostgreSQL instance or mocking. For CI, use `pytest-postgresql` or test against the real DB.

**Step 5: Commit**

```bash
git add hobson/src/hobson/db.py hobson/tests/test_db.py
git commit -m "feat: add PostgreSQL client with run logging and cost tracking"
```

---

### Task 9: Obsidian API Tool

**Files:**
- Create: `hobson/src/hobson/tools/obsidian.py`
- Test: `hobson/tests/test_tools/test_obsidian.py`

**Step 1: Write failing test**

Test that the Obsidian tool can write a note, read a note, and append to a note.

**Step 2: Implement obsidian.py**

httpx client wrapping the Obsidian REST API at `192.168.2.140:27124`:
- `write_note(path, content)` -- PUT `/vault/{path}`
- `read_note(path)` -- GET `/vault/{path}`
- `append_to_note(path, content)` -- PATCH `/vault/{path}` with append
- `list_folder(path)` -- GET `/vault/{path}/` (trailing slash = directory listing)

**Step 3: Run tests, verify pass**

**Step 4: Commit**

---

### Task 10: Telegram Bot Integration

**Files:**
- Create: `hobson/src/hobson/tools/telegram.py`
- Test: `hobson/tests/test_tools/test_telegram.py`

**Step 1: Write failing test**

Test send_message, send_approval_request (with inline keyboard), handle_approval_callback.

**Step 2: Implement telegram.py**

Using `python-telegram-bot`:
- `send_message(text)` -- Send to configured chat
- `send_approval_request(action, reasoning, cost=None)` -- Send with Approve/Deny buttons
- `poll_for_approval(request_id, timeout=3600)` -- Wait for button callback
- Bot webhook or polling loop for incoming callbacks

**Step 3: Run tests, verify pass**

**Step 4: Commit**

---

### Task 11: Basic LangGraph Agent

**Files:**
- Create: `hobson/src/hobson/agent.py`
- Test: `hobson/tests/test_agent.py`

This is the core monolithic agent. First version has minimal tools: write to Obsidian, log decisions to PostgreSQL, send Telegram messages.

**Step 1: Write failing test**

Test that the agent can be compiled, invoked with a simple message, and produces a response.

**Step 2: Implement agent.py**

```python
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_anthropic import ChatAnthropic

from hobson.config import settings
from hobson.tools.obsidian import write_note, read_note, append_to_daily_log
from hobson.tools.telegram import send_message, send_approval_request
from hobson.db import HobsonDB

# Load brand guidelines into system prompt
def load_brand_guidelines() -> str:
    with open(settings.brand_guidelines_path) as f:
        return f.read()

SYSTEM_PROMPT = f"""You are Hobson, an autonomous AI agent running the BuildsCharacter.com business.

{load_brand_guidelines()}

You have access to tools for:
- Writing to your Obsidian vault (documentation, logging, metrics)
- Sending Telegram messages to your owner for approvals and alerts
- Logging decisions and metrics to PostgreSQL

Always log significant actions to your daily log in Obsidian.
Always log decisions with reasoning to PostgreSQL.
"""

# Define tools as functions
tools = [write_note, read_note, append_to_daily_log, send_message, send_approval_request]

model = ChatAnthropic(model="claude-sonnet-4-20250514").bind_tools(tools)

def call_model(state: MessagesState):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + state["messages"]
    return {"messages": [model.invoke(messages)]}

def should_continue(state: MessagesState):
    last = state["messages"][-1]
    return "tools" if last.tool_calls else END

builder = StateGraph(MessagesState)
builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue, ["tools", END])
builder.add_edge("tools", "agent")

def create_agent(checkpointer=None):
    return builder.compile(checkpointer=checkpointer)
```

**Step 3: Run tests, verify pass**

**Step 4: Commit**

---

### Task 12: Health Endpoint

**Files:**
- Create: `hobson/src/hobson/health.py`

**Step 1: Implement FastAPI health endpoint**

```python
from fastapi import FastAPI
from hobson.config import settings

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok", "agent": "hobson", "version": "0.1.0"}
```

Uptime Kuma will ping this endpoint. If it doesn't respond, alert fires via Telegram.

**Step 2: Commit**

---

### Task 13: APScheduler Integration

**Files:**
- Create: `hobson/src/hobson/scheduler.py`

**Step 1: Implement scheduler**

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from hobson.config import settings

scheduler = AsyncIOScheduler()

def setup_schedules(agent):
    """Register all scheduled workflows."""

    # Morning briefing: Daily 7:00 AM ET
    scheduler.add_job(
        run_workflow, CronTrigger(hour=7, minute=0, timezone="America/New_York"),
        args=[agent, "morning_briefing"],
        id="morning_briefing",
    )

    # Content pipeline: Mon/Wed/Fri 10:00 AM ET
    scheduler.add_job(
        run_workflow, CronTrigger(day_of_week="mon,wed,fri", hour=10, timezone="America/New_York"),
        args=[agent, "content_pipeline"],
        id="content_pipeline",
    )

    # Design batch: Monday 2:00 PM ET
    scheduler.add_job(
        run_workflow, CronTrigger(day_of_week="mon", hour=14, timezone="America/New_York"),
        args=[agent, "design_batch"],
        id="design_batch",
    )

    # Substack dispatch: Friday 3:00 PM ET
    scheduler.add_job(
        run_workflow, CronTrigger(day_of_week="fri", hour=15, timezone="America/New_York"),
        args=[agent, "substack_dispatch"],
        id="substack_dispatch",
    )

    # Business review: Sunday 6:00 PM ET
    scheduler.add_job(
        run_workflow, CronTrigger(day_of_week="sun", hour=18, timezone="America/New_York"),
        args=[agent, "business_review"],
        id="business_review",
    )
```

**Step 2: Implement run_workflow with retry/recovery**

Wrapper that handles retries (3x exponential backoff), circuit breaking (3 consecutive failures disables workflow), Uptime Kuma pings on success, Telegram alerts on failure, and run_log tracing.

**Step 3: Commit**

---

### Task 14: Main Entry Point

**Files:**
- Create: `hobson/src/hobson/main.py`

**Step 1: Implement main.py**

Ties everything together:
1. Load config
2. Create PostgreSQL checkpointer
3. Create LangGraph agent with checkpointer
4. Set up APScheduler with all workflows
5. Start FastAPI health server (uvicorn)
6. Start scheduler
7. Start Telegram polling (for incoming approval callbacks)
8. Run event loop

```python
import asyncio
import uvicorn
from hobson.agent import create_agent
from hobson.scheduler import scheduler, setup_schedules
from hobson.health import app
from hobson.config import settings
from langgraph.checkpoint.postgres import PostgresSaver

async def main():
    # Set up checkpointer
    checkpointer = PostgresSaver.from_conn_string(settings.database_url)
    checkpointer.setup()

    # Create agent
    agent = create_agent(checkpointer=checkpointer)

    # Set up scheduled workflows
    setup_schedules(agent)
    scheduler.start()

    # Start health server
    config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
```

**Step 2: Test manually**

```bash
cd hobson
source .venv/bin/activate
python -m hobson.main
```

Verify: health endpoint responds, scheduler is running, no errors.

**Step 3: Commit**

---

## Phase 4: Content Pipeline

### Task 15: Git Operations Tool

**Files:**
- Create: `hobson/src/hobson/tools/git_ops.py`

Implements: clone_repo, create_branch, commit_files, push_branch, create_pr (via `gh` CLI or GitHub API).

This enables the PR-based content review workflow: Hobson drafts a blog post, commits to a branch, opens a PR for human review.

---

### Task 16: Blog Post Drafting Workflow

**Files:**
- Create: `hobson/src/hobson/workflows/content_pipeline.py`

The first real workflow. On trigger:
1. Read content calendar from Obsidian
2. Pick next topic
3. Generate blog post draft (using brand guidelines)
4. Write draft to Obsidian (Content/Blog/Drafts/)
5. Commit to git branch in site repo
6. Open PR
7. Log to run_log
8. Send Telegram notification: "New blog post PR opened: [title]"

---

## Phase 5: Merch Pipeline

### Task 17: Printful API Tool

**Files:**
- Create: `hobson/src/hobson/tools/printful.py`

httpx client wrapping Printful REST API:
- `list_catalog_products()` -- Browse available products
- `create_sync_product(name, variants, print_files)` -- Add product to store
- `list_store_products()` -- Get current catalog
- `get_product_stats(product_id)` -- Sales data

---

### Task 18: Design Generation Workflow

**Files:**
- Create: `hobson/src/hobson/workflows/design_batch.py`

On trigger:
1. Read brand guidelines
2. Generate 5-10 design concept descriptions (using Claude or Gemini for ideation)
3. Use Gemini image generation (NanoBanana / Gemini 2.5 Flash Image) via `langchain-google-genai` to create designs
4. Save concepts to Obsidian (Content/Designs/Concepts/)
5. Upload best designs to Printful
6. Log to run_log and Obsidian

Note: Image generation uses the same `GOOGLE_API_KEY` already configured for Gemini text. No additional accounts or subscriptions required.

---

## Phase 6: Analytics & Reporting

### Task 19: Umami Analytics Tool

**Files:**
- Create: `hobson/src/hobson/tools/analytics.py`

httpx client wrapping Umami API:
- `get_stats(start, end)` -- Summary stats
- `get_pageviews(start, end)` -- Pageview time series
- `get_top_pages(start, end)` -- Top pages by views
- `get_referrers(start, end)` -- Top referrers

---

### Task 20: Morning Briefing Workflow

**Files:**
- Create: `hobson/src/hobson/workflows/morning_briefing.py`

Daily at 7am ET:
1. Fetch analytics from Umami (yesterday's stats)
2. Fetch Printful sales data
3. Calculate daily cost total from PostgreSQL
4. Compose briefing summary
5. Write to Obsidian Daily Log
6. Update Dashboard.md metrics
7. Log metrics to PostgreSQL
8. If anomalies detected: send Telegram alert
9. Ping Uptime Kuma on success

---

### Task 21: Weekly Business Review Workflow

**Files:**
- Create: `hobson/src/hobson/workflows/business_review.py`

Sunday at 6pm ET:
1. Aggregate weekly metrics from PostgreSQL
2. Compare against quarterly goals
3. Write comprehensive review to Obsidian (Operations/Weekly Review.md)
4. Identify trends and propose actions
5. Update Grafana-facing metrics

---

## Phase 7: Substack Integration

### Task 22: Substack Tool

**Files:**
- Create: `hobson/src/hobson/tools/substack.py`

Using `python-substack`:
- `create_draft(title, content, subtitle=None)` -- Create newsletter draft
- `publish_draft(draft_id)` -- Publish
- `get_posts()` -- List published posts

Include fallback: if Substack API fails, write draft to Obsidian and send Telegram alert for manual posting.

---

### Task 23: Weekly Substack Dispatch Workflow

**Files:**
- Create: `hobson/src/hobson/workflows/substack_dispatch.py`

Friday at 3pm ET:
1. Read week's Obsidian daily logs and weekly review
2. Read metrics from PostgreSQL
3. Compose Substack edition in Hobson's voice (using Claude)
4. Include reader poll question
5. Sign with content hash
6. Create draft on Substack
7. Open PR in site repo with the edition text (backup)
8. Send Telegram notification for review
9. After trust period: auto-publish

---

## Phase 8: Grafana Public Dashboard

### Task 24: Grafana Data Source & Dashboard

**Requires:** Access to Grafana (192.168.2.180:3000)

**Step 1: Add PostgreSQL data source**

In Grafana:
1. Configuration > Data Sources > Add PostgreSQL
2. Host: `192.168.2.67:5432`
3. Database: `project_data`
4. User: `hobson` (read-only is fine for Grafana)
5. Schema: `hobson`

**Step 2: Create dashboard panels**

- Site traffic (from hobson.metrics where metric_type='traffic')
- Revenue (from hobson.metrics where metric_type='revenue')
- Hobson operations (from hobson.run_log: success rate, workflows run)
- API costs (from hobson.cost_log: daily/monthly totals)
- Content stats (from hobson.content: draft/published counts)

**Step 3: Enable anonymous access for public embed**

In Grafana config (`/etc/grafana/grafana.ini`):
```ini
[auth.anonymous]
enabled = true
org_role = Viewer

[security]
allow_embedding = true
```

**Step 4: Embed in site**

Update `site/src/pages/dashboard.astro` with the Grafana iframe URL using the dashboard's share/embed link.

---

## Phase 9: Uptime Kuma Monitoring

### Task 25: Configure Uptime Kuma

**Requires:** Access to Uptime Kuma instance (self-hosted)

**Step 1: Create push monitors**

Create one push monitor per workflow:
- `hobson-health` (HTTP monitor, ping `/health` every 60s)
- `hobson-morning-briefing` (push, expected every 24h)
- `hobson-content-pipeline` (push, expected every 48h)
- `hobson-design-batch` (push, expected every 7d)
- `hobson-substack-dispatch` (push, expected every 7d)
- `hobson-business-review` (push, expected every 7d)

**Step 2: Configure Telegram notification**

Set up Telegram notification channel in Uptime Kuma pointing to the Hobson group chat.

**Step 3: Record push URLs in .env**

Each push monitor has a unique URL. Add to Hobson's .env file.

---

## Phase 10: Systemd Service & Deployment

### Task 26: Create Systemd Service

**Files:**
- Create: `hobson/deploy/hobson.service`

```ini
[Unit]
Description=Hobson Autonomous Business Agent
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/builds-character/hobson
Environment=PATH=/root/builds-character/hobson/.venv/bin:/usr/local/bin:/usr/bin
ExecStart=/root/builds-character/hobson/.venv/bin/python -m hobson.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Step 1: Deploy to container**

```bash
pct push <CTID> deploy/hobson.service /etc/systemd/system/hobson.service
pct exec <CTID> -- systemctl daemon-reload
pct exec <CTID> -- systemctl enable hobson
pct exec <CTID> -- systemctl start hobson
pct exec <CTID> -- systemctl status hobson
```

**Step 2: Verify health endpoint and scheduler**

```bash
curl http://<HOBSON_IP>:8080/health
# Watch logs
pct exec <CTID> -- journalctl -u hobson -f
```

---

## Task Dependency Graph

```
Prerequisites (P1-P7, manual)
    |
    v
Phase 1: Scaffolding (Tasks 1-5)
    |
    +---> Phase 2: Website (Tasks 6-7)
    |         |
    |         v
    |     Phase 8: Grafana (Task 24)
    |
    +---> Phase 3: Core Agent (Tasks 8-14)
              |
              +---> Phase 4: Content (Tasks 15-16)
              |
              +---> Phase 5: Merch (Tasks 17-18)
              |
              +---> Phase 6: Analytics (Tasks 19-21)
              |
              +---> Phase 7: Substack (Tasks 22-23)
              |
              +---> Phase 9: Monitoring (Task 25)
              |
              v
          Phase 10: Deployment (Task 26)
```

Phases 2 and 3 can run in parallel. Within Phase 3, tasks are sequential. Phases 4-7 can be built in any order after Phase 3 completes but the design doc specifies: content first, then merch, then analytics, then Substack.

---

## Definition of Done

Each task is complete when:
1. Code is written and passes tests
2. Changes are committed to git
3. Relevant homelab documentation is updated (if infrastructure changed)
4. STATE.md is updated with current progress

The project is "Phase 1 complete" when:
- Hobson responds to a Telegram message
- Hobson writes a note to Obsidian
- Hobson logs a run to PostgreSQL
- The website is live on buildscharacter.com
- Uptime Kuma is monitoring the health endpoint

The project is "MVP complete" when:
- Hobson autonomously runs the morning briefing workflow
- Hobson drafts blog posts and opens PRs
- Hobson generates merch designs and uploads to Printful
- Hobson writes and publishes Substack editions
- All workflows log to run_log and ping Uptime Kuma
- The Grafana dashboard shows real data
