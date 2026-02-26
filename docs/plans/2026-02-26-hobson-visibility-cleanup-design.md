# Hobson Visibility & Cleanup Design

**Date:** 2026-02-26
**Status:** Approved

## Problem

Four days after launch, several operational gaps are reducing visibility into Hobson's day-to-day operations:

1. The Obsidian Task Dashboard lacks per-project granularity (single `#homelab` bucket)
2. Hobson's tasks aren't tagged, so they don't flow into the central dashboard
3. The homelab-docs task list lives outside Obsidian and isn't accessible enough
4. The merch shop shows no products despite 4 items existing in Printful
5. No daily digest tells the operator what Hobson plans to do and what needs attention
6. The Telegram approval workflow may be broken (STATE.md says implemented, Dashboard.md says outbound-only)
7. Printful storefront isn't configured for real transactions

## Workstreams

### 1. Task Dashboard Overhaul (Obsidian)

Expand `60 - Journal/Daily Notes/Task Dashboard.md` with per-project sections:

| Section | Query Tag | Notes |
|---------|-----------|-------|
| High Priority | `priority is high` | Cross-project, keep as-is |
| BuildsCharacter | `#BuildsCharacter` | Hobson business, site, merch |
| NanoClaw | `#NanoClaw` | Bob + Tim bots |
| Homelab | `#homelab` | Infrastructure, containers, networking, physical |
| Homeminder | `#Homeminder` | Home maintenance app |
| Reflection | `#Reflection` | Voice memo app |
| Saxamaphone | `#Saxamaphone` | Music app |
| Job Hunt | `#JobHunt` | Keep existing |
| Obsidian | `#Obsidian` | Keep existing |
| Everything Else | excludes all above | Catch-all, sorted by tag |

Each section query: `tags includes #Tag`, `priority is not high`, `not done`.

### 2. Task Migration

Convert homelab-docs `tasks.md` entries from markdown tables into tagged Obsidian checkbox tasks.

**Destinations:**
- BuildsCharacter tasks: `98 - Hobson Builds Character/Operations/Task Queue.md`
- NanoClaw tasks: a NanoClaw project note
- Homelab infra + physical tasks: `30 - Projects/Homelab/Tasks.md` (new)
- Other dev project tasks: respective project notes or the homelab tasks note

**Format:** `- [ ] #BuildsCharacter Verify Printful storefront checkout`

After migration, remove `docs/operations/tasks.md` from the homelab doc site.

### 3. Hobson Task Queue Cleanup

Retag all tasks in `98 - Hobson Builds Character/Operations/Task Queue.md` with `#BuildsCharacter`. Remove stale items, update completed status, add current tasks including Printful storefront setup checklist.

### 4. Merch Shop Investigation + Fix

**Hypothesis:** Hobson creates products in Printful via API but the Astro shop page reads from `site/src/data/products/*.md` content collection files. If those files weren't written or deployed, the shop appears empty.

**Investigation:**
1. Check if product `.md` files exist in `site/src/data/products/`
2. Check design batch workflow for product file writing step
3. Check for git push step after product file creation
4. Check Cloudflare Pages deploy status

**Fix:** Close whatever gap exists in the pipeline.

### 5. Hobson Morning Digest Enhancement

Expand the morning briefing workflow (7am ET) to send a Telegram digest:
- Today's scheduled runs and times
- Pending approvals awaiting response
- Yesterday's output (posts, designs, products)
- Blockers/failures and circuit breaker status

Modification to `morning_briefing.py` on CT 255.

### 6. Telegram Approval Investigation

Investigate the contradiction between STATE.md (claims inbound polling implemented) and Dashboard.md (reports outbound-only):
1. Check if PTB polling is actually running
2. Check approval callback handler code
3. Test with a real approval request
4. Fix whatever is broken

## Execution Order

1. Task Dashboard overhaul (Obsidian, immediate)
2. Task migration + Hobson Task Queue cleanup (Obsidian, immediate)
3. Merch shop investigation (CT 255 + site repo)
4. Morning digest enhancement (CT 255 code change)
5. Telegram approval investigation (CT 255 code change)
6. Printful storefront setup (manual, operator tasks)
