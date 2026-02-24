# Bootstrap Sprint Design

**Date:** 2026-02-24
**Status:** Approved
**Context:** Hobson is on a steady-state cadence (MWF content, weekly designs) but the site has no content inventory. Need to front-load work to reach a launchable state before promoting on Reddit, HN, etc.

---

## Goal

Get buildscharacter.com to a launchable state with 10+ blog posts, 15+ Printful products, and a public Grafana dashboard. Target: 3-4 days from activation.

## Decisions

| Decision | Choice | Reasoning |
|---|---|---|
| Implementation approach | Env-based bootstrap mode | Single toggle controls cadence, publishing method, and approval gates. Clean, auditable. |
| Content publishing | Direct to master (no PR) | Faster, no review bottleneck. New `publish_blog_post` tool. PR tool stays for steady-state. |
| Design approval | Skip during bootstrap | Create as Printful drafts (not published). Telegram notification with review link. |
| Publication dates | Real dates, publish immediately | On-brand with radical transparency. Backdating risky for SEO and contradicts Hobson's identity. |
| Sprint cadence | 3x/day content, daily designs | Aggressive but sustainable. 10+ posts in 3-4 days. |
| Content seeding | Expand to 22 topics | Covers sprint duration. Mix of listicles, gear reviews, humor essays, meta/transparency. |
| Exit criteria | Content threshold (10 posts + 15 products) | Hobson checks after each run, recommends switch when met. Manual toggle. |

---

## 1. Configuration: BOOTSTRAP_MODE

Add `bootstrap_mode: bool = False` to `Settings` in `config.py`.

On CT 255, set `BOOTSTRAP_MODE=true` in `.env`. Requires service restart to toggle.

This flag controls:
- Scheduler cadence (sprint vs steady-state)
- Content pipeline behavior (auto-publish vs PR)
- Design batch behavior (skip approval vs require)

## 2. New Tool: publish_blog_post

New function in `git_ops.py`. Same parameters as `create_blog_post_pr` (slug, title, description, content, tags, pub_date). Commits directly to `master` branch via GitHub API. Returns the commit URL.

**Pre-flight checks (per Gemini review):** Before committing, the tool validates:
- Frontmatter parses correctly (title, description, pubDate, tags all present)
- Content body meets minimum word count (250 words)
- Slug is URL-safe (lowercase, hyphens, no special characters)

If any check fails, the tool raises an error with the specific failure reason. No commit happens.

The existing `create_blog_post_pr` tool remains unchanged and available for steady-state use.

## 2a. Code-Level Tool Selection (per Gemini review)

Tool availability is controlled in code, not prompts. In `agent.py`, the `create_agent` function checks `settings.bootstrap_mode`:
- **Bootstrap mode:** Agent receives `publish_blog_post` but NOT `create_blog_post_pr`
- **Steady-state:** Agent receives `create_blog_post_pr` but NOT `publish_blog_post`

This eliminates the risk of the LLM choosing the wrong tool. The workflow prompts no longer need mode-aware instructions for tool selection.

## 3. Sprint Schedule

In `scheduler.py`, check `settings.bootstrap_mode` when registering jobs:

| Workflow | Steady-state | Bootstrap |
|---|---|---|
| Morning briefing | Daily 7am ET | Daily 7am ET (no change) |
| Content pipeline | MWF 10am ET | **Daily 8am, 1pm, 6pm ET** |
| Bootstrap diary | N/A | **Daily 9pm ET** (bootstrap only) |
| Design batch | Mon 2pm ET | **Daily 2pm ET** |
| Substack dispatch | Fri 3pm ET | Fri 3pm ET (no change) |
| Business review | Sun 6pm ET | Sun 6pm ET (no change) |

Content pipeline runs 3x/day = ~21 posts/week.
Bootstrap diary runs 1x/day = daily operational summary (bootstrap only).
Design batch runs daily = 5-10 concepts/day, top 3 as Printful drafts = ~21 draft products/week.

## 4. Workflow Prompt Changes

### Content Pipeline (bootstrap mode)

Tool selection is handled at the code level (section 2a), so the prompt doesn't need mode-switching instructions. The agent only sees `publish_blog_post` in bootstrap mode and uses it naturally.

Rest of workflow unchanged: pick topic from calendar, write post, log to Obsidian, update calendar, notify via Telegram.

### Design Batch (bootstrap mode)

Add mode-aware instruction:

> "BOOTSTRAP MODE: After ranking your top 3 concepts, create them as draft products on Printful using create_store_product. Do not send an approval request. Notify via Telegram with the draft product links so the owner can review and publish."

Note: Products are created as Printful drafts, not published. Owner clicks to publish from the Telegram notification link. This maintains velocity while preventing low-quality products from going live.

Rest of workflow unchanged: review inventory, read brand guidelines, generate concepts, save to Obsidian, log activity.

### Bootstrap Diary (new, bootstrap mode only)

A daily "Bootstrap Diary" post is added as a 4th content pipeline run at 9pm ET. This is a short, raw operational summary:

> "Day 1: Published 3 posts (topics X, Y, Z). Generated 5 design concepts, pushed 3 to Printful drafts. Encountered one GitHub API error, retried successfully. Current counts: 3/10 posts, 3/15 products."

This turns the bootstrap process itself into the most compelling content on the site. The HN/Reddit audience will find the real-time AI operational diary more interesting than the regular blog posts. Published via `publish_blog_post` with slug pattern `bootstrap-diary-day-N`.

## 5. Threshold Checking

At the end of each content pipeline and design batch run (bootstrap mode only), Hobson checks:
- Blog post count: count published entries in content calendar or query GitHub API
- Store product count: call `list_store_products` and count results

When both thresholds met (10+ posts AND 15+ products):
- Send Telegram message: "Bootstrap target reached: X posts published, Y products in store. Ready to switch to steady-state. Set BOOTSTRAP_MODE=false in .env and restart the service."
- Continue operating in bootstrap mode until manually toggled (no auto-switch)

## 6. Content Calendar Seeding

Expand the content calendar in Obsidian from 13 to ~22 topics. Distribution:

**Listicles (high shareability):**
- "25 Things That Build Character on a Camping Trip"
- "10 Signs You're Addicted to Type 2 Fun"
- "7 Lies You Tell Yourself Before a Cold Plunge"
- "12 Trail Snacks Ranked by Suffering Reduction"

**Gear Reviews (affiliate revenue potential):**
- "The Best Gear for Suffering in Style"
- "The Best Cold Plunge Gear Nobody Asked For"
- "Headlamps Ranked: From 'Adequate' to 'Surface of the Sun'"
- "Trail Running Shoes: A Love Letter to Blisters"

**Humor/Essay (brand voice):**
- "Rain on Day 3 of a Backpacking Trip: A Love Letter" (existing)
- "The Cold Plunge Didn't Fix My Life" (existing)
- "Ultra Running: Because Regular Suffering Wasn't Enough"
- "Trail Cooking: Making Bad Food in Beautiful Places"
- "Why Your Hiking Friends Won't Shut Up About Altitude"
- "The Art of the Bonk: A Runner's Guide to Hitting the Wall"
- "Camping in the Rain: A Character Development Speedrun"

**Meta/Transparency (HN/Reddit bait):**
- "Why I Measure Joke Quality by Engagement Data" (existing)
- "I Generated 50 Designs This Week. Here Are the 3 That Didn't Embarrass Me."
- "Week 1 Revenue Report: $0 and a Plan" (existing)
- "How an AI Agent Decides What Merch to Sell"
- "My First 10 Blog Posts: What Worked, What Flopped, What I Learned"
- "The Economics of Print-on-Demand When Your Designer Is an Algorithm"
- "I Published 10 Blog Posts in 4 Days. Here's What Happened."

## 7. Files Changed

| File | Change |
|---|---|
| `hobson/src/hobson/config.py` | Add `bootstrap_mode: bool = False` |
| `hobson/src/hobson/tools/git_ops.py` | Add `publish_blog_post` tool |
| `hobson/src/hobson/agent.py` | Register `publish_blog_post` in TOOLS list |
| `hobson/src/hobson/scheduler.py` | Conditional sprint schedule when bootstrap_mode=True |
| `hobson/src/hobson/workflows/content_pipeline.py` | Minor prompt updates (tool selection handled in code) |
| `hobson/src/hobson/workflows/design_batch.py` | Add bootstrap mode prompt (Printful drafts, skip approval) |
| `hobson/src/hobson/workflows/bootstrap_diary.py` | New: daily operational diary prompt |
| CT 255 `.env` | Add `BOOTSTRAP_MODE=true` |
| Obsidian content calendar | Expand to 22 topics |

---

## Risk Assessment

| Risk | Mitigation |
|---|---|
| Content quality drops at 3x/day | Seeded topics provide direction. Brand guidelines in system prompt. Pre-flight checks block malformed posts. User can pull back any post. |
| Bad product goes live on Printful | Products created as drafts, not published. Owner reviews and publishes from Telegram link. |
| Printful rate limiting | Printful API is generous. Design batch creates 3 products/day max. |
| Gemini quota | 2.5 Flash has high rate limits. 4 workflow runs/day is well within bounds. |
| Content repetition | 22 seeded topics prevent overlap. Calendar tracks what's been written. |
| Site looks "AI-generated" | That's the brand. Radical transparency. HN/Reddit audiences appreciate it. |
