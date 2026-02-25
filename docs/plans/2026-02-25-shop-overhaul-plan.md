# Shop Overhaul + "Build Character" Rebrand Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Overhaul the BuildsCharacter.com shop with "Build Character" rebrand, sticker-first product strategy, Printful mockup images, and artwork resolution fix.

**Architecture:** Four workstreams executed sequentially: (1) text rebrand across brand/prompt/site files, (2) delete old products, (3) add LANCZOS upscaling to image generation pipeline, (4) add Printful Mockup Generator API integration. Each workstream is independently committable.

**Tech Stack:** Python 3.11, Pillow (PIL), httpx, Printful API v2, Astro, Cloudflare R2

---

### Task 1: Rebrand to "Build Character"

Update all references from "This Builds Character" / "This builds character" to "Build Character" / "Build character" across three files.

**Files:**
- Modify: `brand/brand_guidelines.md:37` (design text example)
- Modify: `hobson/src/hobson/workflows/design_batch.py:37` (prompt example)
- Modify: `site/src/pages/shop.astro:13` (page subtitle)

**Step 1: Edit brand_guidelines.md**

In `brand/brand_guidelines.md`, line 37, change the design text example:

```
Old: - "This builds character" (simple, universal)
New: - "Build character" (simple, universal)
```

Also line 60, update the blog headline example:

```
Old: - "Parenting Is Just Saying 'It Builds Character' Until They Move Out"
New: - "Parenting Is Just Saying 'Build Character' Until They Move Out"
```

**Step 2: Edit design_batch.py**

In `hobson/src/hobson/workflows/design_batch.py`, line 37, change the prompt example:

```
Old:    - "This builds character" (simple, universal)
New:    - "Build character" (simple, universal)
```

**Step 3: Edit shop.astro**

In `site/src/pages/shop.astro`, line 13, update the subtitle:

```
Old: <p class="text-slate mb-8">Wearable suffering. Stickers, shirts, and gear for people who voluntarily do hard things.</p>
New: <p class="text-slate mb-8">Wearable suffering. Stickers and gear for people who voluntarily do hard things.</p>
```

**Step 4: Commit**

```bash
git add brand/brand_guidelines.md hobson/src/hobson/workflows/design_batch.py site/src/pages/shop.astro
git commit -m "rebrand: update 'This Builds Character' to 'Build Character'"
```

---

### Task 2: Delete old product files

Remove all 4 existing product markdown files. Clean slate for sticker-first relaunch.

**Files:**
- Delete: `site/src/data/products/this-builds-character-mug.md`
- Delete: `site/src/data/products/type-2-fun-certified-mug.md`
- Delete: `site/src/data/products/i-paid-money-to-suffer-mug.md`
- Delete: `site/src/data/products/another-hill-this-builds-character-tshirt.md`

**Step 1: Delete files**

```bash
rm site/src/data/products/this-builds-character-mug.md
rm site/src/data/products/type-2-fun-certified-mug.md
rm site/src/data/products/i-paid-money-to-suffer-mug.md
rm site/src/data/products/another-hill-this-builds-character-tshirt.md
```

**Step 2: Verify shop shows empty state**

```bash
cd site && npx astro build 2>&1 | tail -5
```

Expected: Build succeeds. Shop page should render the "coming soon" empty state since no product files exist.

**Step 3: Commit**

```bash
git add -u site/src/data/products/
git commit -m "shop: remove all existing products for sticker-first relaunch"
```

---

### Task 3: Add LANCZOS upscaling to image_gen.py

Add automatic upscaling when generated images are below Printful minimums.

**Files:**
- Modify: `hobson/src/hobson/tools/image_gen.py`

**Step 1: Add _upscale_if_needed function**

Add this function after `_check_dimensions` (after line 87) in `hobson/src/hobson/tools/image_gen.py`:

```python
def _upscale_if_needed(
    img: Image.Image, product_type: str
) -> tuple[Image.Image, bool]:
    """Upscale image to meet Printful minimums if needed.

    Returns (image, was_upscaled). The returned image is either the original
    (if already large enough) or an upscaled copy using LANCZOS resampling.
    """
    key = product_type.lower().strip()
    if key not in _MIN_DIMENSIONS:
        return img, False
    min_w, min_h = _MIN_DIMENSIONS[key]
    width, height = img.size
    if width >= min_w and height >= min_h:
        return img, False

    # Calculate scale factor to meet both minimum dimensions
    scale = max(min_w / width, min_h / height)
    new_w = int(width * scale)
    new_h = int(height * scale)
    upscaled = img.resize((new_w, new_h), Image.LANCZOS)
    logger.info(
        "Upscaled %s from %dx%d to %dx%d (%.1fx) for product type '%s'",
        product_type, width, height, new_w, new_h, scale, key,
    )
    return upscaled, True
```

**Step 2: Modify generate_design_image to use upscaling**

In `generate_design_image`, replace lines 248-252 (the dimension check block):

```python
    # Check dimensions
    img = Image.open(io.BytesIO(selected_bytes))
    width, height = img.size
    dim_warning = _check_dimensions(width, height, product_type)
    if dim_warning:
        logger.warning(dim_warning)
```

With:

```python
    # Upscale if below Printful minimums, then check final dimensions
    img = Image.open(io.BytesIO(selected_bytes))
    img, was_upscaled = _upscale_if_needed(img, product_type)
    if was_upscaled:
        # Re-encode upscaled image to bytes for upload
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        selected_bytes = buf.getvalue()
    width, height = img.size
    dim_warning = _check_dimensions(width, height, product_type)
    if dim_warning:
        logger.warning(dim_warning)
```

**Step 3: Commit**

```bash
git add hobson/src/hobson/tools/image_gen.py
git commit -m "feat: auto-upscale images below Printful minimums via LANCZOS"
```

---

### Task 4: Add upscaling tests

Test the `_upscale_if_needed` function following the project's "copy from source" test pattern.

**Files:**
- Modify: `hobson/tests/test_tools/test_image_gen.py`

**Step 1: Add _upscale_if_needed copy and tests**

Add after the `# --- End copy ---` comment (line 51) in `test_image_gen.py`, before the existing test classes. First, add the function copy:

```python
def _upscale_if_needed(
    img: Image.Image, product_type: str
) -> tuple[Image.Image, bool]:
    """Upscale image to meet Printful minimums if needed.

    Returns (image, was_upscaled). The returned image is either the original
    (if already large enough) or an upscaled copy using LANCZOS resampling.
    """
    key = product_type.lower().strip()
    if key not in _MIN_DIMENSIONS:
        return img, False
    min_w, min_h = _MIN_DIMENSIONS[key]
    width, height = img.size
    if width >= min_w and height >= min_h:
        return img, False

    scale = max(min_w / width, min_h / height)
    new_w = int(width * scale)
    new_h = int(height * scale)
    upscaled = img.resize((new_w, new_h), Image.LANCZOS)
    return upscaled, True
```

Also add the PIL import at the top of the file (after `import uuid`):

```python
from PIL import Image
```

Then add the test class after the existing test classes:

```python
class TestUpscaleIfNeeded:
    """Tests for _upscale_if_needed."""

    def _make_image(self, width: int, height: int) -> Image.Image:
        """Create a test image of given dimensions."""
        return Image.new("RGBA", (width, height), (255, 0, 0, 255))

    def test_sticker_below_minimum_is_upscaled(self):
        img = self._make_image(1024, 1024)
        result, was_upscaled = _upscale_if_needed(img, "sticker")
        assert was_upscaled is True
        assert result.size[0] >= 1500
        assert result.size[1] >= 1500

    def test_sticker_at_minimum_not_upscaled(self):
        img = self._make_image(1500, 1500)
        result, was_upscaled = _upscale_if_needed(img, "sticker")
        assert was_upscaled is False
        assert result.size == (1500, 1500)

    def test_sticker_above_minimum_not_upscaled(self):
        img = self._make_image(2000, 2000)
        result, was_upscaled = _upscale_if_needed(img, "sticker")
        assert was_upscaled is False
        assert result.size == (2000, 2000)

    def test_unknown_product_type_not_upscaled(self):
        img = self._make_image(100, 100)
        result, was_upscaled = _upscale_if_needed(img, "unknown-widget")
        assert was_upscaled is False
        assert result.size == (100, 100)

    def test_pin_at_1024_meets_minimum(self):
        """Pin minimum is 1000x1000, so 1024x1024 should not upscale."""
        img = self._make_image(1024, 1024)
        result, was_upscaled = _upscale_if_needed(img, "pin")
        assert was_upscaled is False

    def test_case_insensitive_product_type(self):
        img = self._make_image(1024, 1024)
        result, was_upscaled = _upscale_if_needed(img, "Sticker")
        assert was_upscaled is True
        assert result.size[0] >= 1500

    def test_upscale_preserves_aspect_ratio(self):
        """A 1024x1024 image upscaled for stickers should remain square."""
        img = self._make_image(1024, 1024)
        result, _ = _upscale_if_needed(img, "sticker")
        assert result.size[0] == result.size[1]
```

**Step 2: Run tests to verify they pass**

```bash
cd hobson && python -m pytest tests/test_tools/test_image_gen.py -v
```

Expected: All existing tests pass. All new `TestUpscaleIfNeeded` tests pass.

**Step 3: Commit**

```bash
git add hobson/tests/test_tools/test_image_gen.py
git commit -m "test: add upscaling tests for _upscale_if_needed"
```

---

### Task 5: Add Printful Mockup Generator tools

Add `get_mockup_styles` and `generate_product_mockup` to the Printful tools.

**Files:**
- Modify: `hobson/src/hobson/tools/printful.py`

**Step 1: Add imports**

Add at the top of `hobson/src/hobson/tools/printful.py`, after the existing imports (line 3):

```python
import json
import logging
import time

import boto3
```

And add after `from hobson.config import settings` (line 5):

```python
logger = logging.getLogger(__name__)
```

**Step 2: Add get_mockup_styles tool**

Add after the `list_store_products` function (after line 210):

```python
@tool
def get_mockup_styles(catalog_product_id: int) -> str:
    """Get available mockup styles for a catalog product.

    Returns style IDs and names that can be used with generate_product_mockup.
    Prioritizes default mockup styles.

    Args:
        catalog_product_id: The Printful catalog product ID.
    """
    with httpx.Client(headers=_headers(), timeout=30) as client:
        resp = client.get(
            f"{_API_BASE}/v2/catalog-products/{catalog_product_id}/mockup-styles",
            params={"default_mockup_styles": "true", "limit": 20},
        )
        resp.raise_for_status()
        data = resp.json().get("data", [])

    if not data:
        return f"No mockup styles found for product {catalog_product_id}."

    lines = []
    for placement in data:
        placement_name = placement.get("placement", "?")
        for style in placement.get("mockup_styles", []):
            lines.append(
                f"- Style {style['id']}: {style.get('view_name', '?')} "
                f"(category: {style.get('category_name', '?')}, "
                f"placement: {placement_name})"
            )

    return f"Found {len(lines)} mockup styles for product {catalog_product_id}:\n" + "\n".join(lines)
```

**Step 3: Add _upload_mockup_to_r2 helper**

Add after `get_mockup_styles`:

```python
def _upload_mockup_to_r2(image_bytes: bytes, concept_name: str) -> str:
    """Upload mockup image bytes to R2 and return public URL."""
    import re as _re
    import uuid as _uuid

    sanitized = _re.sub(r"[^a-z0-9-]", "-", concept_name.lower().strip())
    sanitized = _re.sub(r"-+", "-", sanitized).strip("-") or "mockup"
    filename = f"{_uuid.uuid4()}-{sanitized}-mockup.jpg"
    r2_key = f"mockups/{filename}"

    s3 = boto3.client(
        "s3",
        endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
    )

    s3.put_object(
        Bucket=settings.r2_bucket_name,
        Key=r2_key,
        Body=image_bytes,
        ContentType="image/jpeg",
    )

    return f"{settings.r2_public_url}/{r2_key}"
```

**Step 4: Add generate_product_mockup tool**

Add after `_upload_mockup_to_r2`:

```python
_MOCKUP_POLL_INTERVAL = 5  # seconds
_MOCKUP_POLL_TIMEOUT = 120  # seconds


@tool
def generate_product_mockup(
    catalog_product_id: int,
    catalog_variant_id: int,
    design_image_url: str,
    concept_name: str = "product",
) -> str:
    """Generate a realistic product mockup image via Printful's Mockup Generator.

    Creates a mockup showing the design on the actual product (e.g., sticker on
    a surface, mug on a desk). The mockup image is uploaded to R2 for permanent
    storage since Printful's generated URLs are temporary.

    On failure or timeout, falls back to the raw design image URL.

    Args:
        catalog_product_id: Printful catalog product ID.
        catalog_variant_id: Printful catalog variant ID.
        design_image_url: Public URL of the design image (from R2).
        concept_name: Human-readable name for the concept (used in filenames).
    """
    headers = _headers()

    # Step 1: Get default mockup style
    try:
        with httpx.Client(headers=headers, timeout=30) as client:
            resp = client.get(
                f"{_API_BASE}/v2/catalog-products/{catalog_product_id}/mockup-styles",
                params={"default_mockup_styles": "true", "limit": 5},
            )
            resp.raise_for_status()
            data = resp.json().get("data", [])
    except Exception as e:
        logger.warning("Failed to fetch mockup styles: %s. Falling back to design URL.", e)
        return json.dumps({
            "status": "fallback",
            "image_url": design_image_url,
            "reason": f"Mockup styles fetch failed: {e}",
        })

    if not data or not data[0].get("mockup_styles"):
        logger.warning("No mockup styles available for product %d", catalog_product_id)
        return json.dumps({
            "status": "fallback",
            "image_url": design_image_url,
            "reason": "No mockup styles available",
        })

    # Pick first default style
    placement_info = data[0]
    style = placement_info["mockup_styles"][0]
    style_id = style["id"]
    placement = placement_info.get("placement", "front")

    # Step 2: Create mockup task
    payload = {
        "format": "jpg",
        "products": [
            {
                "source": "catalog",
                "mockup_style_ids": [style_id],
                "catalog_product_id": catalog_product_id,
                "catalog_variant_ids": [catalog_variant_id],
                "placements": [
                    {
                        "placement": placement,
                        "technique": placement_info.get("technique", "dtg"),
                        "layers": [
                            {
                                "type": "file",
                                "url": design_image_url,
                            }
                        ],
                    }
                ],
            }
        ],
    }

    try:
        with httpx.Client(headers=headers, timeout=30) as client:
            resp = client.post(f"{_API_BASE}/v2/mockup-generator", json=payload)
            resp.raise_for_status()
            task_data = resp.json().get("data", [])
    except Exception as e:
        logger.warning("Mockup task creation failed: %s. Falling back.", e)
        return json.dumps({
            "status": "fallback",
            "image_url": design_image_url,
            "reason": f"Mockup task creation failed: {e}",
        })

    if not task_data:
        return json.dumps({
            "status": "fallback",
            "image_url": design_image_url,
            "reason": "No task data returned from mockup generator",
        })

    task_id = task_data[0].get("id") if isinstance(task_data, list) else task_data.get("id")
    if not task_id:
        # Try alternate response shapes
        task_id = task_data.get("task_id") if isinstance(task_data, dict) else None
    if not task_id:
        return json.dumps({
            "status": "fallback",
            "image_url": design_image_url,
            "reason": "Could not extract task ID from mockup response",
        })

    # Step 3: Poll for completion
    elapsed = 0
    mockup_url = None
    while elapsed < _MOCKUP_POLL_TIMEOUT:
        time.sleep(_MOCKUP_POLL_INTERVAL)
        elapsed += _MOCKUP_POLL_INTERVAL

        try:
            with httpx.Client(headers=headers, timeout=30) as client:
                resp = client.get(
                    f"{_API_BASE}/v2/mockup-tasks",
                    params={"id": str(task_id)},
                )
                resp.raise_for_status()
                tasks = resp.json().get("data", [])
        except Exception as e:
            logger.warning("Mockup poll failed at %ds: %s", elapsed, e)
            continue

        if not tasks:
            continue

        task = tasks[0]
        status = task.get("status", "")

        if status == "completed":
            variant_mockups = task.get("catalog_variant_mockups", [])
            if variant_mockups:
                mockups = variant_mockups[0].get("mockups", [])
                if mockups:
                    mockup_url = mockups[0].get("mockup_url")
            break
        elif status == "failed":
            reasons = task.get("failure_reasons", [])
            reason_str = "; ".join(r.get("detail", "unknown") for r in reasons)
            logger.warning("Mockup task %s failed: %s", task_id, reason_str)
            return json.dumps({
                "status": "fallback",
                "image_url": design_image_url,
                "reason": f"Mockup generation failed: {reason_str}",
            })

    if not mockup_url:
        return json.dumps({
            "status": "fallback",
            "image_url": design_image_url,
            "reason": f"Mockup poll timed out after {_MOCKUP_POLL_TIMEOUT}s",
        })

    # Step 4: Download mockup and re-upload to R2 (Printful URLs are temporary)
    try:
        with httpx.Client(timeout=30) as client:
            img_resp = client.get(mockup_url)
            img_resp.raise_for_status()
            mockup_bytes = img_resp.content

        r2_url = _upload_mockup_to_r2(mockup_bytes, concept_name)
    except Exception as e:
        logger.warning("Mockup download/upload failed: %s. Using Printful URL.", e)
        r2_url = mockup_url  # Use temporary URL as last resort

    return json.dumps({
        "status": "success",
        "image_url": r2_url,
        "mockup_style_id": style_id,
        "task_id": task_id,
    })
```

**Step 5: Commit**

```bash
git add hobson/src/hobson/tools/printful.py
git commit -m "feat: add Printful mockup generator tools (get_mockup_styles, generate_product_mockup)"
```

---

### Task 6: Register new tools in agent.py

Import and register the two new Printful tools.

**Files:**
- Modify: `hobson/src/hobson/agent.py:19-25` (Printful imports)
- Modify: `hobson/src/hobson/agent.py:80-86` (tool list)

**Step 1: Update Printful imports**

In `hobson/src/hobson/agent.py`, replace lines 19-25:

```python
from hobson.tools.printful import (
    create_store_product,
    get_catalog_product_variants,
    list_catalog_products,
    list_store_products,
    upload_design_file,
)
```

With:

```python
from hobson.tools.printful import (
    create_store_product,
    generate_product_mockup,
    get_catalog_product_variants,
    get_mockup_styles,
    list_catalog_products,
    list_store_products,
    upload_design_file,
)
```

**Step 2: Add tools to _COMMON_TOOLS**

In `_COMMON_TOOLS` list, after `list_store_products,` (line 84), add:

```python
    get_mockup_styles,
    generate_product_mockup,
```

**Step 3: Commit**

```bash
git add hobson/src/hobson/agent.py
git commit -m "feat: register mockup generator tools in agent"
```

---

### Task 7: Update design_batch.py with mockup generation step

Update both the steady-state and bootstrap prompts to generate mockups after product creation, and use the mockup URL in product data files.

**Files:**
- Modify: `hobson/src/hobson/workflows/design_batch.py`

**Step 1: Update DESIGN_BATCH_PROMPT**

In `design_batch.py`, replace step 8 (the "Write product data file" section, lines 80-102). The new step 8 becomes the mockup generation, and the old step 8 becomes step 9 (with updated image source). Replace lines 80-116:

```python
8. **Generate product mockups.** For each product created on Printful, call
   generate_product_mockup with the catalog_product_id, catalog_variant_id,
   design image URL (from generate_design_image result), and concept name.

   This generates a realistic photo of the design on the actual product
   (e.g., sticker on a laptop, mug on a desk). The mockup image is
   automatically uploaded to R2 for permanent storage.

   If mockup generation fails, the tool falls back to the raw design URL.
   Either way, you get an image_url in the response to use in step 9.

9. **Write product data file.** For each product created on Printful, write a
   markdown file to 'site/src/data/products/{slug}.md' using create_blog_post_pr
   (steady-state) or publish_blog_post (bootstrap). The file must have this
   exact frontmatter format:

   ---
   name: "Product Name"
   description: "One sentence product description"
   price: 14.99
   image: "https://pub-16bac62563eb4ef4939d29f3e11305db.r2.dev/mockups/..."
   printful_url: "https://buildscharacter.printful.me"
   product_type: "sticker"
   status: "active"
   addedDate: YYYY-MM-DD
   ---

   The slug should be lowercase-hyphenated (e.g., 'build-character-sticker.md').
   The price must be a number (not a string). The image URL is from the
   generate_product_mockup result (step 8), NOT the raw design URL.
   The addedDate is today's date.

   Double-check: name is a string, price is a number with no quotes, image and
   printful_url are valid URLs, product_type matches the enum (sticker, mug, pin,
   print, poster, t-shirt), status is "active".

10. **Log to daily log.** Append to the daily log noting how many concepts were
    generated, the top picks, image generation results, mockup results, and
    whether approval was requested.

11. **Update design inventory in Obsidian.** Append a summary to
    '98 - Hobson Builds Character/Content/Designs/Concepts/' listing all new
    concepts with their status.

Remember: you are Hobson. Your designs should make people laugh, nod in
recognition, and want to slap them on a water bottle or wear them to their
next trail run. Start with stickers and simple text-based designs.
The goal is volume and iteration, not perfection.
"""
```

**Step 2: Update DESIGN_BATCH_BOOTSTRAP_PROMPT**

The bootstrap variant replaces step 7 (approval -> create on Printful). The `.replace()` call at the bottom of the file needs updating since the text it's replacing changed.

Replace the entire `DESIGN_BATCH_BOOTSTRAP_PROMPT` block (lines 118-130) with:

```python
DESIGN_BATCH_BOOTSTRAP_PROMPT = DESIGN_BATCH_PROMPT.replace(
    "7. **Send approval request via Telegram.** Use send_approval_request to present\n"
    "   the top 3 concepts to the owner. Include the concept name, description,\n"
    "   target product type, and image URL (from generate_design_image result) for\n"
    "   each so the owner can see the designs before approving.",
    "7. **Create products on Printful.** For your top 3 ranked concepts, use\n"
    "   upload_design_file with the image URL from generate_design_image, then\n"
    "   create_store_product to create each one. Note: products may go live\n"
    "   immediately, so only push concepts you are confident in.\n"
    "\n"
    "   Then notify via Telegram with the product names, image URLs, and a note\n"
    "   that the owner should review them on Printful.",
)
```

Note: This `.replace()` block is identical to what's already there. The only reason to touch it is if the step 7 text in `DESIGN_BATCH_PROMPT` changed. Since we didn't change step 7, this stays as-is. Verify by inspecting the file after step 1.

**Step 3: Commit**

```bash
git add hobson/src/hobson/workflows/design_batch.py
git commit -m "feat: add mockup generation step to design batch workflow"
```

---

### Task 8: Run tests and verify

**Files:**
- Test: `hobson/tests/test_tools/test_image_gen.py`

**Step 1: Run full test suite**

```bash
cd hobson && python -m pytest tests/ -v
```

Expected: All tests pass (existing + new upscaling tests).

**Step 2: Verify Python syntax on modified files**

```bash
cd hobson && python -c "import ast; ast.parse(open('src/hobson/tools/image_gen.py').read()); print('image_gen.py: OK')"
cd hobson && python -c "import ast; ast.parse(open('src/hobson/tools/printful.py').read()); print('printful.py: OK')"
cd hobson && python -c "import ast; ast.parse(open('src/hobson/agent.py').read()); print('agent.py: OK')"
cd hobson && python -c "import ast; ast.parse(open('src/hobson/workflows/design_batch.py').read()); print('design_batch.py: OK')"
```

Expected: All files parse without syntax errors.

---

### Task 9: Update STATE.md and deploy

**Files:**
- Modify: `STATE.md`

**Step 1: Update STATE.md**

Add under the status section:

```markdown
- [x] Shop Overhaul (2026-02-25)
  - [x] Rebranded "This Builds Character" to "Build Character" across brand guidelines, prompts, and site
  - [x] Removed all existing products (3 mugs, 1 t-shirt) for sticker-first relaunch
  - [x] Added LANCZOS auto-upscaling in image_gen.py (1024->1500+ for stickers)
  - [x] Added Printful Mockup Generator integration (get_mockup_styles, generate_product_mockup)
  - [x] Registered 2 new tools in agent (24 -> 26 tools)
  - [x] Updated design batch workflow with mockup generation step
```

Update the infrastructure table row for Hobson service to show 26 tools.

Update Known Issues: remove the "Imagen outputs 1024x1024; below Printful minimum" line (now handled by upscaling).

**Step 2: Commit all remaining changes**

```bash
git add STATE.md
git commit -m "docs: update STATE.md with shop overhaul completion"
```

**Step 3: Push and deploy to CT 255**

```bash
git push origin master
```

Then deploy to CT 255:
```bash
ssh root@192.168.2.16 'pct exec 255 -- bash -c "cd /root/builds-character && git pull && systemctl restart hobson"'
```

Verify:
```bash
ssh root@192.168.2.16 'pct exec 255 -- systemctl status hobson --no-pager'
```

Expected: Service active (running).

---

## Post-Implementation: Manual Printful Setup

After deploying, the user needs to verify in the Printful dashboard (https://www.printful.com/dashboard):

1. Store settings > Payment gateway connected (Stripe or PayPal)
2. Shipping settings configured (regions, methods)
3. Billing > Payment method on file
4. Storefront > `buildscharacter.printful.me` set to active
5. Products > Review/delete old mugs and t-shirt
6. Store branding > Update name/logo to reflect "Build Character"
