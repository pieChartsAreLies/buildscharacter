# Hobson Visibility & Cleanup Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix the empty merch shop, give the operator daily Telegram digests with schedule and pending approvals, and verify Telegram approval callbacks work.

**Architecture:** Add a `publish_product` tool to git_ops.py (mirrors `publish_blog_post` but targets `site/src/data/products/`). Add a `get_pending_approvals` tool for the morning briefing to report on. Enhance the morning briefing prompt to send a structured Telegram digest. Investigate Telegram PTB polling status.

**Tech Stack:** Python 3.11, LangGraph, python-telegram-bot (PTB), GitHub REST API, PostgreSQL, APScheduler

**Prerequisites completed (Obsidian-side, already done this session):**
- Task Dashboard expanded with per-project sections (#BuildsCharacter, #NanoClaw, #Homeminder, #Reflection, #Saxamaphone, #homelab, #Obsidian, #JobHunt)
- Homelab-docs tasks migrated to tagged Obsidian tasks (Homelab Tasks.md, Dev Project Tasks.md)
- Hobson Task Queue cleaned up with #BuildsCharacter tags and Printful storefront checklist

---

### Task 1: Create `publish_product` tool in git_ops.py

**Files:**
- Modify: `hobson/src/hobson/tools/git_ops.py` (add new function after `publish_blog_post`)
- Test: `hobson/tests/test_git_ops.py`

**Context:** `publish_blog_post` (line ~193) writes to `site/src/data/blog/{slug}.md` on master via GitHub API. The new tool does the same thing but targets `site/src/data/products/{slug}.md` with the product content schema (name, description, price, image, printful_url, product_type, status, addedDate).

**Step 1: Write the failing test**

```python
def test_publish_product_validates_slug():
    """publish_product rejects invalid slugs."""
    result = publish_product.invoke({
        "slug": "INVALID SLUG!",
        "name": "Test Product",
        "description": "A test product",
        "price": "14.99",
        "image_url": "https://example.com/image.png",
        "printful_url": "https://buildscharacter.printful.me",
        "product_type": "sticker",
    })
    assert "Invalid slug" in result


def test_publish_product_validates_product_type():
    """publish_product rejects invalid product types."""
    result = publish_product.invoke({
        "slug": "test-product",
        "name": "Test Product",
        "description": "A test product",
        "price": "14.99",
        "image_url": "https://example.com/image.png",
        "printful_url": "https://buildscharacter.printful.me",
        "product_type": "invalid_type",
    })
    assert "Invalid product_type" in result
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/llama/Development/builds-character && python -m pytest hobson/tests/test_git_ops.py -v -k "publish_product"`
Expected: FAIL (function not defined)

**Step 3: Implement `publish_product`**

Add to `hobson/src/hobson/tools/git_ops.py`:

```python
VALID_PRODUCT_TYPES = {"sticker", "mug", "pin", "print", "poster", "t-shirt"}

@tool
def publish_product(
    slug: str,
    name: str,
    description: str,
    price: str,
    image_url: str,
    printful_url: str,
    product_type: str,
) -> str:
    """Publish a product page directly to the site (bootstrap mode).

    Creates a product markdown file at site/src/data/products/{slug}.md
    on the master branch. Cloudflare Pages auto-deploys.

    Args:
        slug: URL-safe product identifier (lowercase, hyphens only)
        name: Product display name
        description: Product description
        price: Retail price as string (e.g. "14.99")
        image_url: Product image or mockup URL
        printful_url: Link to buy on Printful storefront
        product_type: One of: sticker, mug, pin, print, poster, t-shirt
    """
    # Validate slug
    if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', slug):
        return f"Invalid slug '{slug}'. Use lowercase alphanumeric with hyphens only."

    # Validate product_type
    if product_type not in VALID_PRODUCT_TYPES:
        return f"Invalid product_type '{product_type}'. Must be one of: {', '.join(sorted(VALID_PRODUCT_TYPES))}"

    # Validate price is numeric
    try:
        float(price)
    except ValueError:
        return f"Invalid price '{price}'. Must be a number."

    today = datetime.now().strftime("%Y-%m-%d")
    content = f"""---
name: "{name}"
description: "{description}"
price: {price}
image: "{image_url}"
printful_url: "{printful_url}"
product_type: "{product_type}"
status: "active"
addedDate: {today}
---
"""

    path = f"site/src/data/products/{slug}.md"
    encoded = base64.b64encode(content.encode()).decode()

    # Get master SHA
    resp = requests.get(
        f"{GITHUB_API}/repos/{REPO}/git/ref/heads/master",
        headers=HEADERS,
    )
    if resp.status_code != 200:
        return f"Failed to get master ref: {resp.status_code} {resp.text}"
    master_sha = resp.json()["object"]["sha"]

    # Create or update file on master
    resp = requests.put(
        f"{GITHUB_API}/repos/{REPO}/contents/{path}",
        headers=HEADERS,
        json={
            "message": f"product: add {name}",
            "content": encoded,
            "branch": "master",
        },
    )

    if resp.status_code in (200, 201):
        commit_url = resp.json().get("commit", {}).get("html_url", "")
        return f"Product '{name}' published at {path}. Commit: {commit_url}"
    else:
        return f"Failed to publish product: {resp.status_code} {resp.text}"
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/llama/Development/builds-character && python -m pytest hobson/tests/test_git_ops.py -v -k "publish_product"`
Expected: PASS (validation tests pass; API call tests may need mocking)

**Step 5: Register tool in agent.py**

Add import: `from hobson.tools.git_ops import publish_product`
Add to bootstrap tools list alongside `publish_blog_post`.

**Step 6: Commit**

```bash
cd /Users/llama/Development/builds-character
git add hobson/src/hobson/tools/git_ops.py hobson/src/hobson/agent.py hobson/tests/test_git_ops.py
git commit -m "feat: add publish_product tool for writing product pages to site repo"
```

---

### Task 2: Backfill product markdown files for existing Printful products

**Files:**
- Create: `site/src/data/products/this-builds-character-mug.md`
- Create: `site/src/data/products/type-2-fun-certified-mug.md`
- Create: `site/src/data/products/i-paid-money-to-suffer-mug.md`
- Create: `site/src/data/products/another-hill-this-builds-character-tshirt.md`

**Context:** 4 products exist in Printful but have no corresponding markdown files. We need the exact product details (names, prices, image URLs). Get these by SSHing to CT 255 and running the list_store_products Printful API call, or by checking the Printful dashboard.

**Step 1: Get current Printful product details**

SSH to Loki and query Printful API:
```bash
ssh root@192.168.2.16 'pct exec 255 -- bash -c "source /root/builds-character/.env && curl -s -H \"Authorization: Bearer \$PRINTFUL_API_TOKEN\" https://api.printful.com/store/products | python3 -m json.tool"'
```

**Step 2: Create product markdown files**

For each product, create a `.md` file in `site/src/data/products/` with frontmatter matching the content schema. Use the image URLs from R2 (design or mockup images). Example:

```yaml
---
name: "This Builds Character - Mug"
description: "A bold reminder for your morning coffee. Because everything builds character."
price: 14.99
image: "https://pub-16bac62563eb4ef4939d29f3e11305db.r2.dev/[actual-image-path]"
printful_url: "https://buildscharacter.printful.me"
product_type: "mug"
status: "active"
addedDate: 2026-02-24
---
```

Exact names, prices, and image URLs will come from the Printful API response in Step 1.

**Step 3: Verify shop page renders locally**

```bash
cd /Users/llama/Development/builds-character/site && npm run dev
```

Open http://localhost:4321/shop and verify products display.

**Step 4: Commit and push**

```bash
cd /Users/llama/Development/builds-character
git add site/src/data/products/
git commit -m "feat: add product pages for 4 existing Printful products"
git push
```

Cloudflare Pages will auto-deploy. Verify at https://buildscharacter.com/shop.

---

### Task 3: Update design batch workflow to use publish_product

**Files:**
- Modify: `hobson/src/hobson/workflows/design_batch.py`

**Context:** The design batch prompt (step 9) tells the agent to write product markdown files. Now that `publish_product` exists as a registered tool, update the prompt to explicitly reference the tool name so the agent uses it.

**Step 1: Read the current design_batch.py**

Read the file and find the section that describes product markdown creation (around step 9 in the bootstrap variant).

**Step 2: Update the prompt**

In the bootstrap section of the prompt, replace any instructions about manually writing product files with:

```
Step 9: For each product created, call the publish_product tool with:
- slug: lowercase-hyphenated product name (e.g. "type-2-fun-certified-sticker")
- name: Product display name
- description: 1-2 sentence product description
- price: Retail price (string, e.g. "4.99" for stickers, "14.99" for mugs)
- image_url: The mockup URL from step 8 (or the design URL if mockup failed)
- printful_url: "https://buildscharacter.printful.me"
- product_type: One of sticker, mug, pin, print, poster, t-shirt
```

**Step 3: Commit**

```bash
cd /Users/llama/Development/builds-character
git add hobson/src/hobson/workflows/design_batch.py
git commit -m "feat: update design batch to use publish_product tool"
```

---

### Task 4: Add `get_pending_approvals` tool

**Files:**
- Modify: `hobson/src/hobson/tools/telegram.py` (add new tool function)
- Modify: `hobson/src/hobson/agent.py` (register tool)
- Test: `hobson/tests/test_telegram.py`

**Context:** The morning briefing needs to report on pending approvals. The approvals table exists in PostgreSQL (hobson.approvals) but there's no agent-accessible tool to query it. The DB client has `create_approval` and `resolve_approval` but no `list_pending`.

**Step 1: Add `get_pending_approvals` to the DB client**

Check `hobson/src/hobson/db.py` for the HobsonDB class. Add:

```python
def get_pending_approvals(self) -> list[dict]:
    """Get all unresolved approval requests."""
    rows = self._query(
        "SELECT request_id, action, reasoning, estimated_cost, created_at "
        "FROM hobson.approvals WHERE resolved_at IS NULL "
        "ORDER BY created_at DESC"
    )
    return [
        {
            "request_id": r[0],
            "action": r[1],
            "reasoning": r[2],
            "estimated_cost": r[3],
            "created_at": str(r[4]),
        }
        for r in rows
    ]
```

**Step 2: Add `get_pending_approvals` tool to telegram.py**

```python
@tool
def get_pending_approvals() -> str:
    """Get all pending approval requests that haven't been resolved yet.

    Returns a formatted list of pending approvals with their action,
    reasoning, and estimated cost.
    """
    pending = _db.get_pending_approvals()
    if not pending:
        return "No pending approvals."
    lines = [f"**{len(pending)} pending approval(s):**"]
    for a in pending:
        cost = f" (est. ${a['estimated_cost']})" if a.get("estimated_cost") else ""
        lines.append(f"- {a['action']}{cost} — {a['reasoning']} (since {a['created_at']})")
    return "\n".join(lines)
```

**Step 3: Register in agent.py**

Add import and include in the common tools list (not bootstrap-specific — this is always useful).

**Step 4: Run tests**

Run: `cd /Users/llama/Development/builds-character && python -m pytest hobson/tests/ -v`
Expected: All tests pass

**Step 5: Commit**

```bash
cd /Users/llama/Development/builds-character
git add hobson/src/hobson/db.py hobson/src/hobson/tools/telegram.py hobson/src/hobson/agent.py
git commit -m "feat: add get_pending_approvals tool for morning briefing"
```

---

### Task 5: Enhance morning briefing with Telegram daily digest

**Files:**
- Modify: `hobson/src/hobson/workflows/morning_briefing.py`

**Context:** The morning briefing currently: collects traffic, checks store inventory, reviews daily log, writes to Obsidian, updates Dashboard.md, sends a basic Telegram summary. We need to expand the Telegram message to include today's schedule and pending approvals.

**Step 1: Read morning_briefing.py**

Read the full file to understand the current prompt structure.

**Step 2: Update the prompt**

Add to the morning briefing prompt:

```
After completing the standard briefing, send a Telegram daily digest using send_message with this structure:

MORNING DIGEST — [today's date]

SCHEDULE TODAY:
- 8:00 AM: Content Pipeline
- 1:00 PM: Content Pipeline
- 2:00 PM: Design Batch
- 6:00 PM: Content Pipeline
- 9:00 PM: Bootstrap Diary
(Adjust based on current mode: bootstrap vs steady-state. In steady-state, content is MWF 10am only and design batch is Monday 2pm only.)

PENDING APPROVALS:
Call get_pending_approvals to check for any unresolved approval requests. List them here. If none, say "None — all clear."

YESTERDAY'S OUTPUT:
- Blog posts published (count and titles)
- Products created or updated
- Designs generated
- Any failed workflows

NEEDS YOUR ATTENTION:
- Any circuit breakers tripped
- Any approval requests older than 24 hours
- Any anomalies in traffic or metrics
```

**Step 3: Commit**

```bash
cd /Users/llama/Development/builds-character
git add hobson/src/hobson/workflows/morning_briefing.py
git commit -m "feat: expand morning briefing to send daily digest via Telegram"
```

---

### Task 6: Investigate Telegram inbound polling

**Files:**
- Read: `hobson/src/hobson/tools/telegram.py` (check if Application is built and polling started)
- Read: `hobson/src/hobson/main.py` or entry point (check startup sequence)
- Check: Service logs on CT 255

**Context:** STATE.md says PTB polling was implemented, but Dashboard.md (auto-updated daily by Hobson) reports "Telegram is outbound-only." The handlers exist in code (`_handle_message`, `_handle_callback`) but they may not be started.

**Step 1: Check the entry point**

Read the main entry point to see how the Telegram bot is initialized:
```bash
ssh root@192.168.2.16 'pct exec 255 -- cat /root/builds-character/hobson/src/hobson/main.py'
```

Look for: `application.run_polling()` or `application.start()` or similar PTB startup.

**Step 2: Check service logs**

```bash
ssh root@192.168.2.16 'pct exec 255 -- journalctl -u hobson --no-pager -n 100'
```

Look for: PTB startup messages, polling errors, webhook errors.

**Step 3: Check if handlers are registered**

In `telegram.py`, look for `application.add_handler()` calls. Verify:
- `MessageHandler` for `_handle_message`
- `CallbackQueryHandler` for `_handle_callback`

**Step 4: Fix if broken**

If polling isn't started, add the startup call. If handlers aren't registered, register them. The fix depends on what the investigation reveals.

**Step 5: Test with a real message**

Send a test message to the Hobson Telegram bot and verify it responds. Send an approval request and verify the buttons work.

**Step 6: Update Dashboard.md known issues**

After fixing, update the morning briefing prompt to remove the "outbound-only" known issue from Dashboard.md on next run.

**Step 7: Commit**

```bash
cd /Users/llama/Development/builds-character
git add hobson/src/hobson/tools/telegram.py hobson/src/hobson/main.py  # or whatever files changed
git commit -m "fix: enable Telegram inbound polling and approval callbacks"
```

---

### Task 7: Deploy all changes to CT 255

**Step 1: Push to GitHub**

```bash
cd /Users/llama/Development/builds-character && git push
```

**Step 2: Deploy to CT 255**

```bash
ssh root@192.168.2.16 'pct exec 255 -- bash -c "cd /root/builds-character && git pull && systemctl restart hobson"'
```

**Step 3: Verify service is running**

```bash
ssh root@192.168.2.16 'pct exec 255 -- systemctl status hobson'
ssh root@192.168.2.16 'pct exec 255 -- curl -s localhost:8080/health'
```

**Step 4: Verify shop page**

Check https://buildscharacter.com/shop — products should now be visible.

**Step 5: Update STATE.md**

Update with:
- publish_product tool added (27 tools total)
- get_pending_approvals tool added (28 tools total)
- Morning digest enhanced
- Telegram polling status (fixed or confirmed working)
- Product markdown backfill complete
- Shop page displaying products

---

## Summary

| Task | Type | Effort |
|------|------|--------|
| 1. publish_product tool | New code | Medium |
| 2. Backfill product pages | Data entry | Low |
| 3. Update design batch prompt | Prompt edit | Low |
| 4. get_pending_approvals tool | New code | Low |
| 5. Morning digest enhancement | Prompt edit | Low |
| 6. Telegram investigation | Debug | Unknown |
| 7. Deploy + verify | Operations | Low |
