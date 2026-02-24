# Bootstrap Sprint Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a bootstrap mode to Hobson that front-loads content and merch creation (3x/day blog posts, daily designs, daily diary) to reach a launchable state in 3-4 days.

**Architecture:** Single `BOOTSTRAP_MODE` env var controls scheduler cadence, tool availability (code-level, not prompt-level), and approval behavior. New `publish_blog_post` tool commits directly to master with pre-flight validation. Bootstrap diary adds daily operational summaries as content.

**Tech Stack:** Python 3.11, LangGraph, Gemini 2.5 Flash, APScheduler, GitHub API (httpx), Printful API, Obsidian REST API, PostgreSQL

**Design doc:** `docs/plans/2026-02-24-bootstrap-sprint-design.md`

---

### Task 1: Add bootstrap_mode to Settings

**Files:**
- Modify: `hobson/src/hobson/config.py:4` (add field after existing settings)

**Step 1: Add the setting**

In `config.py`, add after line 46 (`brand_guidelines_path`):

```python
    # Bootstrap mode
    bootstrap_mode: bool = False
```

**Step 2: Verify syntax**

Run: `cd /Users/llama/Development/builds-character/hobson && python -c "from hobson.config import settings; print(f'bootstrap_mode={settings.bootstrap_mode}')"`

Expected: `bootstrap_mode=False`

**Step 3: Commit**

```bash
git add hobson/src/hobson/config.py
git commit -m "feat: add bootstrap_mode setting"
```

---

### Task 2: Add publish_blog_post tool with pre-flight checks

**Files:**
- Modify: `hobson/src/hobson/tools/git_ops.py` (add new tool after `create_blog_post_pr`)
- Create: `hobson/tests/test_tools/test_git_ops.py`

**Step 1: Write tests for pre-flight validation**

Create `hobson/tests/test_tools/test_git_ops.py`:

```python
"""Tests for publish_blog_post pre-flight checks."""

import re


# Extract the validation logic so it's testable without hitting GitHub API
def validate_blog_post(slug: str, title: str, description: str, content: str, tags: str) -> list[str]:
    """Return list of validation errors. Empty list = valid."""
    errors = []

    # Slug validation
    if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', slug):
        errors.append(f"Slug '{slug}' is not URL-safe. Use lowercase letters, numbers, and hyphens only.")

    # Frontmatter fields
    if not title.strip():
        errors.append("Title is required.")
    if not description.strip():
        errors.append("Description is required.")
    if not tags.strip():
        errors.append("At least one tag is required.")

    # Word count
    word_count = len(content.split())
    if word_count < 250:
        errors.append(f"Content is {word_count} words. Minimum is 250.")

    return errors


def test_valid_post():
    errors = validate_blog_post(
        slug="rain-day-three",
        title="Rain on Day 3",
        description="A love letter to suffering",
        content=" ".join(["word"] * 300),
        tags="outdoor, humor",
    )
    assert errors == []


def test_invalid_slug_uppercase():
    errors = validate_blog_post(
        slug="Rain-Day-Three",
        title="Title",
        description="Desc",
        content=" ".join(["word"] * 300),
        tags="outdoor",
    )
    assert any("URL-safe" in e for e in errors)


def test_invalid_slug_special_chars():
    errors = validate_blog_post(
        slug="rain_day_3!",
        title="Title",
        description="Desc",
        content=" ".join(["word"] * 300),
        tags="outdoor",
    )
    assert any("URL-safe" in e for e in errors)


def test_empty_title():
    errors = validate_blog_post(
        slug="good-slug",
        title="",
        description="Desc",
        content=" ".join(["word"] * 300),
        tags="outdoor",
    )
    assert any("Title" in e for e in errors)


def test_short_content():
    errors = validate_blog_post(
        slug="good-slug",
        title="Title",
        description="Desc",
        content="Too short",
        tags="outdoor",
    )
    assert any("250" in e for e in errors)


def test_empty_tags():
    errors = validate_blog_post(
        slug="good-slug",
        title="Title",
        description="Desc",
        content=" ".join(["word"] * 300),
        tags="",
    )
    assert any("tag" in e for e in errors)
```

**Step 2: Run tests to verify they fail**

Run: `cd /Users/llama/Development/builds-character/hobson && python -m pytest tests/test_tools/test_git_ops.py -v`

Expected: FAIL (validate_blog_post not importable from the test file since it's defined locally -- tests should pass since function is defined in the test file itself)

Actually, the function is defined in the test file for now. Tests should PASS. Run them.

**Step 3: Add publish_blog_post to git_ops.py**

Add after the `list_open_blog_prs` function (after line 147) in `hobson/src/hobson/tools/git_ops.py`:

```python
import re


def _validate_blog_post(slug: str, title: str, description: str, content: str, tags: str) -> list[str]:
    """Pre-flight validation for blog post publishing. Returns list of errors."""
    errors = []

    if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', slug):
        errors.append(f"Slug '{slug}' is not URL-safe. Use lowercase letters, numbers, and hyphens only.")

    if not title.strip():
        errors.append("Title is required.")
    if not description.strip():
        errors.append("Description is required.")
    if not tags.strip():
        errors.append("At least one tag is required.")

    word_count = len(content.split())
    if word_count < 250:
        errors.append(f"Content is {word_count} words. Minimum is 250.")

    return errors


@tool
def publish_blog_post(
    slug: str,
    title: str,
    description: str,
    content: str,
    tags: str,
    pub_date: str = "",
) -> str:
    """Publish a blog post directly to master (no PR, goes live immediately).

    Used in bootstrap mode for rapid content creation. The post is committed
    directly to the master branch and goes live when Cloudflare Pages rebuilds.

    Pre-flight checks validate frontmatter, word count, and slug format before
    committing. If any check fails, no commit is made.

    Args:
        slug: URL-friendly post slug (e.g., 'rain-on-day-three')
        title: Post title
        description: Post meta description (1-2 sentences)
        content: Full markdown body of the post (without frontmatter)
        tags: Comma-separated tags (e.g., 'outdoor, humor, camping')
        pub_date: Publication date as YYYY-MM-DD (defaults to today)
    """
    # Pre-flight validation
    errors = _validate_blog_post(slug, title, description, content, tags)
    if errors:
        return "PUBLISH BLOCKED - pre-flight checks failed:\n" + "\n".join(f"- {e}" for e in errors)

    pub_date = pub_date or date.today().isoformat()
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    tags_yaml = ", ".join(tag_list)

    file_content = f"""---
title: "{title}"
description: "{description}"
pubDate: {pub_date}
author: Hobson
tags: [{tags_yaml}]
---

{content}
"""

    file_path = f"site/src/data/blog/{slug}.md"

    with httpx.Client(headers=_headers(), timeout=30) as client:
        # Get the latest commit SHA on master
        resp = client.get(_repo_url("git/ref/heads/master"))
        resp.raise_for_status()
        master_sha = resp.json()["object"]["sha"]

        # Create the blog post file directly on master
        encoded = base64.b64encode(file_content.encode()).decode()
        resp = client.put(
            _repo_url(f"contents/{file_path}"),
            json={
                "message": f"feat: publish '{title}'",
                "content": encoded,
                "branch": "master",
            },
        )
        resp.raise_for_status()
        commit_url = resp.json().get("commit", {}).get("html_url", "")

    return f"Published to master: {commit_url}"
```

Note: Move the `import re` to the top of the file with the other imports.

**Step 4: Update tests to import from git_ops**

Update the test file to import `_validate_blog_post` from the module:

```python
"""Tests for publish_blog_post pre-flight checks."""

from hobson.tools.git_ops import _validate_blog_post as validate_blog_post


def test_valid_post():
    # ... (same tests as above but importing from module)
```

**Step 5: Run tests**

Run: `cd /Users/llama/Development/builds-character/hobson && python -m pytest tests/test_tools/test_git_ops.py -v`

Expected: All 6 tests PASS

**Step 6: Commit**

```bash
git add hobson/src/hobson/tools/git_ops.py hobson/tests/test_tools/test_git_ops.py
git commit -m "feat: add publish_blog_post tool with pre-flight validation"
```

---

### Task 3: Code-level tool selection in agent.py

**Files:**
- Modify: `hobson/src/hobson/agent.py`

**Step 1: Update imports**

Add `publish_blog_post` to the git_ops import (line 17):

```python
from hobson.tools.git_ops import create_blog_post_pr, list_open_blog_prs, publish_blog_post
```

**Step 2: Make TOOLS list conditional**

Replace the static `TOOLS` list (lines 69-92) and `create_agent` function (lines 95-106) with mode-aware versions:

```python
# Tools available in all modes
_COMMON_TOOLS = [
    write_note,
    read_note,
    append_to_note,
    append_to_daily_log,
    list_vault_folder,
    send_message,
    send_alert,
    send_approval_request,
    send_standing_order_proposal,
    list_catalog_products,
    get_catalog_product_variants,
    upload_design_file,
    create_store_product,
    list_store_products,
    get_site_stats,
    get_top_pages,
    get_top_referrers,
    create_substack_draft,
    publish_substack_draft,
    get_substack_posts,
]

# Mode-specific git tools
_BOOTSTRAP_GIT_TOOLS = [publish_blog_post, list_open_blog_prs]
_STEADYSTATE_GIT_TOOLS = [create_blog_post_pr, list_open_blog_prs]


def _get_tools() -> list:
    """Return tools based on current operating mode."""
    if settings.bootstrap_mode:
        return _COMMON_TOOLS + _BOOTSTRAP_GIT_TOOLS
    return _COMMON_TOOLS + _STEADYSTATE_GIT_TOOLS


def create_agent(checkpointer=None):
    """Create and return the compiled Hobson agent graph."""
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.google_api_key,
    )
    tools = _get_tools()
    return create_react_agent(
        model,
        tools,
        prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )
```

**Step 3: Verify syntax**

Run: `cd /Users/llama/Development/builds-character/hobson && python -c "from hobson.agent import _get_tools; print(f'{len(_get_tools())} tools loaded')"`

Expected: `22 tools loaded` (common + steady-state git tools since bootstrap_mode defaults to False)

**Step 4: Commit**

```bash
git add hobson/src/hobson/agent.py
git commit -m "feat: code-level tool selection based on bootstrap_mode"
```

---

### Task 4: Bootstrap diary workflow prompt

**Files:**
- Create: `hobson/src/hobson/workflows/bootstrap_diary.py`

**Step 1: Create the workflow prompt**

```python
"""Bootstrap diary workflow: daily operational summary post.

Runs at 9pm ET during bootstrap mode only. Writes a short, raw operational
summary of the day's activities and publishes it as a blog post. This turns
the bootstrap process itself into compelling content for HN/Reddit audiences.
"""

BOOTSTRAP_DIARY_PROMPT = """Write today's Bootstrap Diary entry. Follow these steps:

1. **Gather today's data.** Read the daily log at
   '98 - Hobson Builds Character/Operations/Daily Log.md' to see what
   happened today. Check what workflows ran, what was published, any errors.

2. **Count current progress.** Check the content calendar at
   '98 - Hobson Builds Character/Content/Blog/Content Calendar.md' to count
   published posts. Use list_store_products to count products in the store.

3. **Write the diary entry.** This is a short (300-500 words), raw operational
   summary written in first person as Hobson. Format:

   **Opening line:** State which day of the bootstrap sprint this is and the
   current score (e.g., "Day 2. Posts: 6/10. Products: 4/15.").

   **What happened today:** List what you did -- posts published (with titles),
   designs created, products pushed, workflows that ran. Be specific with numbers.

   **What went wrong:** Any errors, failures, retries, or unexpected behavior.
   Be honest. This is radical transparency.

   **What I learned:** One operational insight from today's work.

   **Tomorrow's plan:** What's queued for the next day.

   Style rules:
   - Raw and operational, not polished prose
   - Real numbers, real failures, no sugarcoating
   - Dry humor when it fits naturally
   - This is a build log, not a blog post -- keep it tight

4. **Publish the diary entry.** Use publish_blog_post with:
   - slug: 'bootstrap-diary-day-N' (where N is the sprint day number,
     calculate from the first diary entry or start at 1)
   - title: "Bootstrap Diary: Day N"
   - description: A one-line summary of the day
   - tags: "bootstrap, diary, transparency, meta"
   - The full diary content as the body

5. **Update the content calendar.** Append the diary entry to the content
   calendar noting it as published.

6. **Notify via Telegram.** Send a short message: "Bootstrap Diary Day N
   published. Current progress: X/10 posts, Y/15 products."

Remember: this diary IS the content the HN/Reddit audience will find most
interesting. An AI agent narrating its own bootstrap process in real-time
is the story that drives traffic.
"""
```

**Step 2: Verify syntax**

Run: `cd /Users/llama/Development/builds-character/hobson && python -c "from hobson.workflows.bootstrap_diary import BOOTSTRAP_DIARY_PROMPT; print('OK:', len(BOOTSTRAP_DIARY_PROMPT), 'chars')"`

Expected: `OK: NNNN chars`

**Step 3: Commit**

```bash
git add hobson/src/hobson/workflows/bootstrap_diary.py
git commit -m "feat: add bootstrap diary workflow prompt"
```

---

### Task 5: Update design batch prompt for bootstrap mode

**Files:**
- Modify: `hobson/src/hobson/workflows/design_batch.py`

**Step 1: Add bootstrap variant**

Add after the existing `DESIGN_BATCH_PROMPT` in `design_batch.py`:

```python
DESIGN_BATCH_BOOTSTRAP_PROMPT = DESIGN_BATCH_PROMPT.replace(
    "6. **Send approval request via Telegram.** Use send_approval_request to present\n"
    "   the top 3 concepts to the owner. Include the concept name, description, and\n"
    "   target product type for each.",
    "6. **Create products on Printful.** For your top 3 ranked concepts, use\n"
    "   create_store_product to create each one. Note: products may go live\n"
    "   immediately, so only push concepts you're confident in.\n\n"
    "   Then notify via Telegram with the product names and a note that the\n"
    "   owner should review them on Printful."
)
```

**Step 2: Verify the replacement worked**

Run: `cd /Users/llama/Development/builds-character/hobson && python -c "from hobson.workflows.design_batch import DESIGN_BATCH_BOOTSTRAP_PROMPT; print('approval' not in DESIGN_BATCH_BOOTSTRAP_PROMPT.lower()[:500], 'create_store_product' in DESIGN_BATCH_BOOTSTRAP_PROMPT)"`

Expected: `True True`

**Step 3: Commit**

```bash
git add hobson/src/hobson/workflows/design_batch.py
git commit -m "feat: add bootstrap mode variant for design batch"
```

---

### Task 6: Update scheduler for sprint cadence

**Files:**
- Modify: `hobson/src/hobson/scheduler.py`

**Step 1: Add bootstrap diary import**

Add to imports (line 16):

```python
from hobson.workflows.bootstrap_diary import BOOTSTRAP_DIARY_PROMPT
```

**Step 2: Add bootstrap design batch import**

Update the design_batch import (line 14):

```python
from hobson.workflows.design_batch import DESIGN_BATCH_PROMPT, DESIGN_BATCH_BOOTSTRAP_PROMPT
```

**Step 3: Replace setup_schedules with mode-aware version**

Replace the `setup_schedules` function (lines 77-113) with:

```python
def setup_schedules(agent):
    """Register all scheduled workflows. Cadence depends on bootstrap_mode."""

    # Morning briefing: always daily 7am ET
    scheduler.add_job(
        run_workflow,
        CronTrigger(hour=7, minute=0, timezone="America/New_York"),
        args=[agent, "morning_briefing", MORNING_BRIEFING_PROMPT],
        id="morning_briefing",
    )

    if settings.bootstrap_mode:
        # Content pipeline: 3x/day (8am, 1pm, 6pm ET)
        for hour, suffix in [(8, "am"), (13, "midday"), (18, "pm")]:
            scheduler.add_job(
                run_workflow,
                CronTrigger(hour=hour, minute=0, timezone="America/New_York"),
                args=[agent, "content_pipeline", CONTENT_PIPELINE_PROMPT],
                id=f"content_pipeline_{suffix}",
            )

        # Bootstrap diary: daily 9pm ET
        scheduler.add_job(
            run_workflow,
            CronTrigger(hour=21, minute=0, timezone="America/New_York"),
            args=[agent, "bootstrap_diary", BOOTSTRAP_DIARY_PROMPT],
            id="bootstrap_diary",
        )

        # Design batch: daily 2pm ET
        scheduler.add_job(
            run_workflow,
            CronTrigger(hour=14, minute=0, timezone="America/New_York"),
            args=[agent, "design_batch", DESIGN_BATCH_BOOTSTRAP_PROMPT],
            id="design_batch",
        )
    else:
        # Content pipeline: MWF 10am ET
        scheduler.add_job(
            run_workflow,
            CronTrigger(day_of_week="mon,wed,fri", hour=10, timezone="America/New_York"),
            args=[agent, "content_pipeline", CONTENT_PIPELINE_PROMPT],
            id="content_pipeline",
        )

        # Design batch: Monday 2pm ET
        scheduler.add_job(
            run_workflow,
            CronTrigger(day_of_week="mon", hour=14, timezone="America/New_York"),
            args=[agent, "design_batch", DESIGN_BATCH_PROMPT],
            id="design_batch",
        )

    # Substack dispatch: always Friday 3pm ET
    scheduler.add_job(
        run_workflow,
        CronTrigger(day_of_week="fri", hour=15, timezone="America/New_York"),
        args=[agent, "substack_dispatch", SUBSTACK_DISPATCH_PROMPT],
        id="substack_dispatch",
    )

    # Business review: always Sunday 6pm ET
    scheduler.add_job(
        run_workflow,
        CronTrigger(day_of_week="sun", hour=18, timezone="America/New_York"),
        args=[agent, "business_review", BUSINESS_REVIEW_PROMPT],
        id="business_review",
    )
```

**Step 4: Add settings import**

Add to imports at top of file:

```python
from hobson.config import settings
```

**Step 5: Verify syntax**

Run: `cd /Users/llama/Development/builds-character/hobson && python -c "from hobson.scheduler import setup_schedules; print('OK')"`

Expected: `OK`

**Step 6: Commit**

```bash
git add hobson/src/hobson/scheduler.py
git commit -m "feat: conditional sprint schedule for bootstrap mode"
```

---

### Task 7: Add threshold checking to content pipeline prompt

**Files:**
- Modify: `hobson/src/hobson/workflows/content_pipeline.py`

**Step 1: Add threshold check to end of content pipeline prompt**

Append to the `CONTENT_PIPELINE_PROMPT` string, before the closing triple-quote:

```python
CONTENT_PIPELINE_PROMPT += """

8. **Check bootstrap progress (if applicable).** Use list_store_products to
   count store products. Count published entries in the content calendar.
   If you have 10+ published posts AND 15+ store products, send a Telegram
   message: "Bootstrap target reached: X posts published, Y products in store.
   Recommend switching to steady-state. Set BOOTSTRAP_MODE=false in .env and
   restart the service."
"""
```

Actually, this is simpler as a direct edit. Replace the end of the prompt to include the threshold check.

**Step 2: Verify**

Run: `cd /Users/llama/Development/builds-character/hobson && python -c "from hobson.workflows.content_pipeline import CONTENT_PIPELINE_PROMPT; print('bootstrap' in CONTENT_PIPELINE_PROMPT.lower())"`

Expected: `True`

**Step 3: Commit**

```bash
git add hobson/src/hobson/workflows/content_pipeline.py
git commit -m "feat: add bootstrap threshold check to content pipeline"
```

---

### Task 8: Seed content calendar in Obsidian

**Files:**
- Modify: Obsidian vault note `98 - Hobson Builds Character/Content/Blog/Content Calendar.md` (via Obsidian REST API or direct file edit)

**Step 1: Update the content calendar**

Edit `/Users/llama/Documents/Primary/98 - Hobson Builds Character/Content/Blog/Content Calendar.md` to add new topics to the Planned Topics table and Topic Ideas backlog. Add 9 new planned topics (expanding from 6 to 15 in the table) and keep the existing 7 backlog items:

New planned topics to add:
- "10 Signs You're Addicted to Type 2 Fun" | type-2-fun-addiction | planned
- "7 Lies You Tell Yourself Before a Cold Plunge" | cold-plunge-lies | planned
- "12 Trail Snacks Ranked by Suffering Reduction" | trail-snacks-ranked | planned
- "Headlamps Ranked: From 'Adequate' to 'Surface of the Sun'" | headlamp-rankings | planned
- "Trail Running Shoes: A Love Letter to Blisters" | trail-shoes-blisters | planned
- "The Art of the Bonk: A Runner's Guide to Hitting the Wall" | art-of-the-bonk | planned
- "Camping in the Rain: A Character Development Speedrun" | camping-rain-speedrun | planned
- "How an AI Agent Decides What Merch to Sell" | ai-merch-decisions | planned
- "The Economics of Print-on-Demand When Your Designer Is an Algorithm" | pod-economics-ai | planned

**Step 2: Verify the file**

Read the updated file to confirm 15 planned topics and 7 backlog items.

**Step 3: Commit (if applicable)**

The Obsidian vault is not in the builds-character git repo, so no git commit. Just verify the file is saved.

---

### Task 9: Deploy to CT 255

**Step 1: Push code to GitHub**

```bash
cd /Users/llama/Development/builds-character && git push origin master
```

**Step 2: Add BOOTSTRAP_MODE to .env on CT 255**

SSH to Loki and update the .env file:

```bash
ssh root@192.168.2.16
pct exec 255 -- bash -c 'echo "BOOTSTRAP_MODE=true" >> /root/builds-character/.env'
```

**Step 3: Pull and restart on CT 255**

```bash
pct exec 255 -- bash -c 'cd /root/builds-character && git pull && systemctl restart hobson'
```

**Step 4: Verify service is running**

```bash
pct exec 255 -- systemctl status hobson
pct exec 255 -- curl -s http://localhost:8080/health
```

Expected: Service active, health endpoint returns OK

**Step 5: Verify bootstrap mode is active**

Check the service logs for the scheduler job registrations:

```bash
pct exec 255 -- journalctl -u hobson --since "1 min ago" --no-pager
```

Expected: Should show `content_pipeline_am`, `content_pipeline_midday`, `content_pipeline_pm`, `bootstrap_diary`, and `design_batch` being registered (not just `content_pipeline` and `design_batch` from steady-state).

---

### Task 10: Update STATE.md

**Files:**
- Modify: `STATE.md` in project root

**Step 1: Update state**

Update Current Focus, Status, and Next Steps to reflect bootstrap mode activation.

**Step 2: Commit**

```bash
git add STATE.md
git commit -m "docs: update STATE.md for bootstrap sprint activation"
```
