# Image Generation Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add Gemini Imagen image generation to Hobson's design batch workflow so he produces actual artwork for merch products.

**Architecture:** Two new LangGraph tools (`generate_design_image`, `upload_to_r2`) in a new `image_gen.py` module. `generate_design_image` generates 4 candidate images via Imagen 4.0, uses Gemini Flash vision to rank and select the best one, validates dimensions against product type requirements, and returns the image as base64. `upload_to_r2` uploads to Cloudflare R2 with UUID-prefixed filenames. A new PostgreSQL table `hobson.design_generations` tracks every generation attempt. The design batch workflow prompts are updated with a structured prompt template and product focus directive.

**Tech Stack:** google-genai SDK (Imagen 4.0), boto3 (R2/S3), Pillow (dimension validation), PostgreSQL (provenance), LangGraph @tool decorator

---

### Task 1: Create PostgreSQL table for design generation tracking

This table stores every image generation attempt for debugging and reproduction.

**Files:**
- Create: SQL migration (run on CT 201 via SSH)

**Step 1: Write the CREATE TABLE statement**

```sql
CREATE TABLE hobson.design_generations (
    id SERIAL PRIMARY KEY,
    concept_name TEXT NOT NULL,
    generation_prompt TEXT NOT NULL,
    model_version VARCHAR(100) NOT NULL DEFAULT 'imagen-4.0-generate-001',
    image_url VARCHAR(500),
    r2_filename VARCHAR(500),
    product_type VARCHAR(50),
    generation_status VARCHAR(20) NOT NULL DEFAULT 'success',
    status_reason TEXT,
    image_width INT,
    image_height INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**Step 2: Run the migration on CT 201**

Run from Loki (192.168.2.16):
```bash
ssh root@192.168.2.13  # Freya (CT 201 host)
pct exec 201 -- psql -U hobson -d project_data -c "
CREATE TABLE hobson.design_generations (
    id SERIAL PRIMARY KEY,
    concept_name TEXT NOT NULL,
    generation_prompt TEXT NOT NULL,
    model_version VARCHAR(100) NOT NULL DEFAULT 'imagen-4.0-generate-001',
    image_url VARCHAR(500),
    r2_filename VARCHAR(500),
    product_type VARCHAR(50),
    generation_status VARCHAR(20) NOT NULL DEFAULT 'success',
    status_reason TEXT,
    image_width INT,
    image_height INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"
```

Expected: `CREATE TABLE`

**Step 3: Verify the table exists**

```bash
pct exec 201 -- psql -U hobson -d project_data -c "\d hobson.design_generations"
```

Expected: Table schema with all 11 columns listed.

**Step 4: Commit** (nothing to commit yet -- this is infra-only)

---

### Task 2: Add R2 config fields to Settings

**Files:**
- Modify: `hobson/src/hobson/config.py:32-34` (insert after Cloudflare Analytics block)

**Step 1: Add R2 settings to config.py**

Insert after line 34 (`cloudflare_zone_id`), before line 36 (`# Uptime Kuma`):

```python
    # Cloudflare R2 (design image storage)
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = "hobson-designs"
    r2_public_url: str = ""  # e.g., https://pub-{hash}.r2.dev
```

**Step 2: Verify config loads**

Run from project root:
```bash
cd hobson && python -c "from hobson.config import Settings; s = Settings(); print(s.r2_bucket_name)"
```

Expected: `hobson-designs`

**Step 3: Commit**

```bash
git add hobson/src/hobson/config.py
git commit -m "feat: add R2 config fields for design image storage"
```

---

### Task 3: Add dependencies to pyproject.toml

**Files:**
- Modify: `hobson/pyproject.toml:6-20`

**Step 1: Add google-genai and boto3**

Add these two lines to the `dependencies` list (Pillow is already present as `pillow>=10`):

```
    "google-genai>=1.0",
    "boto3>=1.35",
```

The full dependencies block should look like:

```toml
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
    "python-substack>=0.1",
    "pillow>=10",
    "google-genai>=1.0",
    "boto3>=1.35",
]
```

**Step 2: Commit**

```bash
git add hobson/pyproject.toml
git commit -m "feat: add google-genai and boto3 dependencies for image generation"
```

Note: Actual `pip install` happens during deploy on CT 255.

---

### Task 4: Add design generation logging to HobsonDB

**Files:**
- Modify: `hobson/src/hobson/db.py:176-177` (append after approvals section)
- Create: `hobson/tests/test_tools/test_image_gen.py` (test file)

**Step 1: Write the failing test**

Create `hobson/tests/test_tools/test_image_gen.py`:

```python
"""Tests for image generation helper functions.

Pure-logic functions are duplicated here to avoid importing hobson modules
that pull in pydantic_settings and other CT-255-only dependencies.
"""

import re
import uuid


# --- Copied from hobson/src/hobson/tools/image_gen.py --------------------------
# Keep in sync with the source.

_SANITIZE_RE = re.compile(r"[^a-z0-9-]")

# Minimum pixel dimensions per product type (from Printful specs)
_MIN_DIMENSIONS = {
    "sticker": (1500, 1500),
    "pin": (1000, 1000),
    "small-print": (2400, 3000),
    "poster": (5400, 7200),
    "t-shirt": (4500, 5100),
}


def _sanitize_filename(concept_name: str) -> str:
    """Create a UUID-prefixed, filesystem-safe filename from a concept name."""
    sanitized = _SANITIZE_RE.sub("-", concept_name.lower().strip())
    sanitized = re.sub(r"-+", "-", sanitized).strip("-")
    if not sanitized:
        sanitized = "design"
    return f"{uuid.uuid4()}-{sanitized}.png"


def _check_dimensions(
    width: int, height: int, product_type: str
) -> str | None:
    """Return a warning string if image is below minimum for product type, else None."""
    key = product_type.lower().strip()
    if key not in _MIN_DIMENSIONS:
        return None  # Unknown product type, skip validation
    min_w, min_h = _MIN_DIMENSIONS[key]
    if width < min_w or height < min_h:
        return (
            f"Image {width}x{height} is below minimum {min_w}x{min_h} "
            f"for product type '{key}'"
        )
    return None


# --- End copy -----------------------------------------------------------------


class TestSanitizeFilename:
    """Tests for _sanitize_filename."""

    def test_basic_concept_name(self):
        filename = _sanitize_filename("Rain Day Sticker")
        assert filename.endswith("-rain-day-sticker.png")
        # UUID prefix is 36 chars + hyphen
        assert len(filename) > 36

    def test_special_characters_removed(self):
        filename = _sanitize_filename("It's a 100% great design!!!")
        # Should strip quotes, percent, exclamation
        assert "'" not in filename
        assert "%" not in filename
        assert "!" not in filename
        assert filename.endswith(".png")

    def test_empty_name_gets_default(self):
        filename = _sanitize_filename("   ")
        assert filename.endswith("-design.png")

    def test_uuid_prefix_is_valid(self):
        filename = _sanitize_filename("test")
        uuid_part = filename[:36]
        # Should be a valid UUID4
        parsed = uuid.UUID(uuid_part)
        assert parsed.version == 4

    def test_unique_filenames(self):
        """Two calls with same name produce different filenames (different UUIDs)."""
        f1 = _sanitize_filename("same name")
        f2 = _sanitize_filename("same name")
        assert f1 != f2


class TestCheckDimensions:
    """Tests for _check_dimensions."""

    def test_sticker_meets_minimum(self):
        result = _check_dimensions(1500, 1500, "sticker")
        assert result is None

    def test_sticker_below_minimum(self):
        result = _check_dimensions(1024, 1024, "sticker")
        assert result is not None
        assert "1500x1500" in result
        assert "sticker" in result

    def test_pin_meets_minimum(self):
        result = _check_dimensions(1024, 1024, "pin")
        assert result is None

    def test_unknown_product_type_skips_check(self):
        result = _check_dimensions(100, 100, "unknown-widget")
        assert result is None

    def test_case_insensitive_product_type(self):
        result = _check_dimensions(1500, 1500, "Sticker")
        assert result is None

    def test_poster_below_minimum(self):
        result = _check_dimensions(2048, 2048, "poster")
        assert result is not None
        assert "5400x7200" in result
```

**Step 2: Run tests to verify they fail**

```bash
cd hobson && python -m pytest tests/test_tools/test_image_gen.py -v
```

Expected: All tests PASS (these are self-contained -- the functions are defined in the test file itself). This is the pattern used by the existing `test_git_ops.py`.

**Step 3: Add log_design_generation to db.py**

Append to the end of `hobson/src/hobson/db.py`, after line 176:

```python

    # -- Design generations --

    def log_design_generation(
        self,
        concept_name: str,
        generation_prompt: str,
        model_version: str = "imagen-4.0-generate-001",
        image_url: str | None = None,
        r2_filename: str | None = None,
        product_type: str | None = None,
        generation_status: str = "success",
        status_reason: str | None = None,
        image_width: int | None = None,
        image_height: int | None = None,
    ) -> int:
        with self._conn() as conn:
            row = conn.execute(
                """INSERT INTO hobson.design_generations
                   (concept_name, generation_prompt, model_version, image_url,
                    r2_filename, product_type, generation_status, status_reason,
                    image_width, image_height)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   RETURNING id""",
                (
                    concept_name, generation_prompt, model_version, image_url,
                    r2_filename, product_type, generation_status, status_reason,
                    image_width, image_height,
                ),
            ).fetchone()
            return row["id"]
```

**Step 4: Commit**

```bash
git add hobson/src/hobson/db.py hobson/tests/test_tools/test_image_gen.py
git commit -m "feat: add design generation tracking to DB and test helpers"
```

---

### Task 5: Implement generate_design_image tool

This is the core tool. It generates 4 images via Imagen 4.0, uses Gemini Flash to pick the best one, validates dimensions, and returns the selected image.

**Files:**
- Create: `hobson/src/hobson/tools/image_gen.py`

**Step 1: Create image_gen.py with both tools**

Create `hobson/src/hobson/tools/image_gen.py`:

```python
"""Image generation and R2 upload tools for design batch workflow."""

import base64
import io
import logging
import re
import time
import uuid

import boto3
from google import genai
from google.genai import types
from langchain_core.tools import tool
from PIL import Image

from hobson.config import settings

logger = logging.getLogger(__name__)

_SANITIZE_RE = re.compile(r"[^a-z0-9-]")

# Minimum pixel dimensions per product type (from Printful specs)
_MIN_DIMENSIONS = {
    "sticker": (1500, 1500),
    "pin": (1000, 1000),
    "small-print": (2400, 3000),
    "poster": (5400, 7200),
    "t-shirt": (4500, 5100),
}

_MODEL = "imagen-4.0-generate-001"
_MAX_RETRIES = 3


def _sanitize_filename(concept_name: str) -> str:
    """Create a UUID-prefixed, filesystem-safe filename from a concept name."""
    sanitized = _SANITIZE_RE.sub("-", concept_name.lower().strip())
    sanitized = re.sub(r"-+", "-", sanitized).strip("-")
    if not sanitized:
        sanitized = "design"
    return f"{uuid.uuid4()}-{sanitized}.png"


def _check_dimensions(
    width: int, height: int, product_type: str
) -> str | None:
    """Return a warning string if image is below minimum for product type, else None."""
    key = product_type.lower().strip()
    if key not in _MIN_DIMENSIONS:
        return None
    min_w, min_h = _MIN_DIMENSIONS[key]
    if width < min_w or height < min_h:
        return (
            f"Image {width}x{height} is below minimum {min_w}x{min_h} "
            f"for product type '{key}'"
        )
    return None


def _rank_images_with_vision(
    images: list[bytes], prompt: str
) -> int:
    """Use Gemini Flash to rank candidate images and return index of the best one.

    Falls back to index 0 if the vision call fails.
    """
    if len(images) <= 1:
        return 0

    try:
        client = genai.Client(api_key=settings.google_api_key)
        parts = [
            types.Part.from_text(
                f"You are evaluating {len(images)} candidate images generated from this prompt:\n\n"
                f"\"{prompt}\"\n\n"
                "Rank them by: brand alignment (outdoor/endurance humor), visual clarity, "
                "print-readiness (clean lines, no artifacts), and overall quality.\n\n"
                "Reply with ONLY the number (1-based) of the best image. Nothing else."
            )
        ]
        for i, img_bytes in enumerate(images):
            parts.append(types.Part.from_text(f"\nImage {i + 1}:"))
            parts.append(types.Part.from_bytes(data=img_bytes, mime_type="image/png"))

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=parts,
        )
        choice = int(response.text.strip()) - 1  # Convert 1-based to 0-based
        if 0 <= choice < len(images):
            return choice
        logger.warning("Vision ranker returned out-of-range index %d, using 0", choice)
        return 0
    except Exception as e:
        logger.warning("Vision ranking failed (%s), using first image", e)
        return 0


@tool
async def generate_design_image(
    prompt: str,
    concept_name: str,
    product_type: str = "sticker",
    aspect_ratio: str = "1:1",
) -> str:
    """Generate a design image using Gemini Imagen 4.0.

    Generates 4 candidate images, uses vision AI to select the best one,
    and validates dimensions against product requirements.

    Args:
        prompt: Detailed image generation prompt assembled from the structured template.
        concept_name: Human-readable concept name (for logging and filenames).
        product_type: Target product type for dimension validation (sticker, pin, poster, etc.).
        aspect_ratio: Image aspect ratio. One of "1:1", "3:4", "4:3", "9:16", "16:9".
    """
    from hobson.db import HobsonDB

    db = HobsonDB(settings.database_url)

    # Retry loop for transient API failures
    last_error = None
    for attempt in range(_MAX_RETRIES):
        try:
            client = genai.Client(api_key=settings.google_api_key)
            response = client.models.generate_images(
                model=_MODEL,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=4,
                    aspect_ratio=aspect_ratio,
                    include_rai_reason=True,
                    output_mime_type="image/png",
                ),
            )
            break
        except Exception as e:
            last_error = e
            if attempt < _MAX_RETRIES - 1:
                wait = 2 ** attempt
                logger.warning("Imagen API attempt %d failed (%s), retrying in %ds", attempt + 1, e, wait)
                time.sleep(wait)
            continue
    else:
        # All retries exhausted
        db.log_design_generation(
            concept_name=concept_name,
            generation_prompt=prompt,
            product_type=product_type,
            generation_status="failed",
            status_reason=f"API error after {_MAX_RETRIES} retries: {last_error}",
        )
        return f"ERROR: Image generation failed after {_MAX_RETRIES} retries: {last_error}"

    # Check for safety-filtered or empty response
    if not response.generated_images:
        reason = "No images returned (likely safety filter)"
        db.log_design_generation(
            concept_name=concept_name,
            generation_prompt=prompt,
            product_type=product_type,
            generation_status="filtered",
            status_reason=reason,
        )
        return f"ERROR: {reason}. Try modifying the prompt to avoid content filter triggers."

    # Collect raw bytes from all candidates
    candidate_bytes = []
    for gi in response.generated_images:
        img_data = gi.image.image_bytes
        if isinstance(img_data, str):
            img_data = base64.b64decode(img_data)
        candidate_bytes.append(img_data)

    # Rank with vision model and select best
    best_idx = _rank_images_with_vision(candidate_bytes, prompt)
    selected_bytes = candidate_bytes[best_idx]

    # Check dimensions
    img = Image.open(io.BytesIO(selected_bytes))
    width, height = img.size
    dim_warning = _check_dimensions(width, height, product_type)
    if dim_warning:
        logger.warning(dim_warning)

    # Encode as base64 for return
    image_b64 = base64.b64encode(selected_bytes).decode("utf-8")

    # Log to DB
    db.log_design_generation(
        concept_name=concept_name,
        generation_prompt=prompt,
        product_type=product_type,
        generation_status="success",
        image_width=width,
        image_height=height,
    )

    result = (
        f"Image generated successfully for '{concept_name}'.\n"
        f"Dimensions: {width}x{height} px\n"
        f"Selected image {best_idx + 1} of {len(candidate_bytes)} candidates.\n"
        f"Model: {_MODEL}\n"
    )
    if dim_warning:
        result += f"WARNING: {dim_warning}\n"
    result += f"BASE64:{image_b64}"

    return result


@tool
async def upload_to_r2(
    image_base64: str,
    concept_name: str,
) -> str:
    """Upload a generated design image to Cloudflare R2 and return its public URL.

    Args:
        image_base64: Base64-encoded PNG image bytes (from generate_design_image output after BASE64: prefix).
        concept_name: Human-readable concept name (used in filename after UUID prefix).
    """
    # Strip the BASE64: prefix if present
    if image_base64.startswith("BASE64:"):
        image_base64 = image_base64[7:]

    image_bytes = base64.b64decode(image_base64)
    filename = _sanitize_filename(concept_name)
    r2_key = f"designs/{filename}"

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
        ContentType="image/png",
    )

    public_url = f"{settings.r2_public_url}/{r2_key}"

    # Update the most recent design_generations record with the URL
    from hobson.db import HobsonDB

    db = HobsonDB(settings.database_url)
    try:
        with db._conn() as conn:
            conn.execute(
                """UPDATE hobson.design_generations
                   SET image_url = %s, r2_filename = %s
                   WHERE concept_name = %s AND image_url IS NULL
                   ORDER BY created_at DESC LIMIT 1""",
                (public_url, filename, concept_name),
            )
    except Exception as e:
        logger.warning("Failed to update design_generations with URL: %s", e)

    return f"Uploaded to R2: {public_url}"
```

**Step 2: Verify the module imports cleanly**

This can only be fully tested on CT 255 after dependencies are installed. For now, check syntax:

```bash
python -c "import ast; ast.parse(open('hobson/src/hobson/tools/image_gen.py').read()); print('Syntax OK')"
```

Expected: `Syntax OK`

**Step 3: Run the existing tests to make sure nothing broke**

```bash
cd hobson && python -m pytest tests/ -v
```

Expected: All existing tests still pass.

**Step 4: Commit**

```bash
git add hobson/src/hobson/tools/image_gen.py
git commit -m "feat: add generate_design_image and upload_to_r2 tools"
```

---

### Task 6: Register image tools in agent.py

**Files:**
- Modify: `hobson/src/hobson/agent.py:1-2` (add import)
- Modify: `hobson/src/hobson/agent.py:69-90` (add to _COMMON_TOOLS)

**Step 1: Add import**

After line 17 (`from hobson.tools.git_ops import ...`), add:

```python
from hobson.tools.image_gen import generate_design_image, upload_to_r2
```

**Step 2: Add tools to _COMMON_TOOLS**

Add `generate_design_image` and `upload_to_r2` to the `_COMMON_TOOLS` list, after `list_store_products` (line 83):

```python
    generate_design_image,
    upload_to_r2,
```

**Step 3: Verify syntax**

```bash
python -c "import ast; ast.parse(open('hobson/src/hobson/agent.py').read()); print('Syntax OK')"
```

Expected: `Syntax OK`

**Step 4: Commit**

```bash
git add hobson/src/hobson/agent.py
git commit -m "feat: register image gen tools in agent common tools"
```

---

### Task 7: Update design batch workflow prompts

Both the steady-state and bootstrap prompts need: (1) product focus directive, (2) structured prompt template, (3) image generation step.

**Files:**
- Modify: `hobson/src/hobson/workflows/design_batch.py`

**Step 1: Rewrite DESIGN_BATCH_PROMPT**

Replace the entire content of `design_batch.py` with:

```python
"""Design batch workflow: generate merch concepts and manage the Printful pipeline.

This module provides the structured prompt for the weekly design batch workflow.
When triggered by the scheduler (Monday 2pm ET in steady-state, daily 2pm ET in bootstrap),
the agent ideates design concepts, generates artwork via Imagen, and manages the
Printful product pipeline.
"""

DESIGN_BATCH_PROMPT = """Run the design batch workflow. Follow these steps:

1. **Review current store inventory.** Use list_store_products to see what's
   already in the store. Note gaps in the product line.

2. **Read brand guidelines and past concepts.** Read the brand guidelines from
   '98 - Hobson Builds Character/Strategy/Brand Guidelines.md' and check
   '98 - Hobson Builds Character/Content/Designs/Concepts/' for previous concepts
   to avoid repetition.

3. **Generate 5-10 new design concepts.** For each concept, define:
   - A name (short, punchy, brand-aligned)
   - A description (what the design looks like)
   - Target product type (sticker, pin, small print, t-shirt, poster)
   - The text/copy on the design (if text-based)
   - Why it fits the brand

   Prioritize low-cost, impulse-buy products (stickers, pins, small prints) during
   early inventory building. Save premium items (hoodies, posters) for after you
   have traffic data showing demand.

   Focus on the outdoor/endurance community. Think:
   - Stickers with dry one-liners about suffering outdoors
   - T-shirts with deadpan text about character-building activities
   - Mugs with self-deprecating cold plunge humor
   - Posters with ironic "motivational" quotes

   Examples of on-brand design text:
   - "This builds character" (simple, universal)
   - "I paid money to suffer" (race/event culture)
   - "Day 3 rain is just a vibe check"
   - "Cold plunge enthusiast (still waiting for the benefits)"
   - "Type 2 fun certified"

4. **Save concepts to Obsidian.** Write each concept as a note in
   '98 - Hobson Builds Character/Content/Designs/Concepts/' with:
   - YAML frontmatter: title, status (concept), product_type, created date
   - Full concept description

5. **Rank and select top 3.** Evaluate concepts on:
   - Shareability (would someone post this on Instagram?)
   - Brand alignment (does it match the voice?)
   - Production feasibility (simple designs are better for POD)
   - Market fit (does the target audience want this?)

6. **Generate images for top 3.** For each of your top 3 concepts, write a
   structured image generation prompt using this template:

   - Subject: the core design idea
   - Style: art style matching the brand (minimalist, bold, outdoor-inspired,
     vintage national park poster, vector illustration, line art)
   - Composition: layout for the target product (centered on transparent
     background for stickers, isolated subject for pins, full design for prints)
   - Color palette: from brand guidelines or concept-specific
   - Product context: what product this will go on and its constraints
   - Negative: things to exclude (no text unless the concept IS text-based,
     no borders, no watermarks, no photorealistic faces)

   Assemble these fields into a single detailed prompt, then call
   generate_design_image with the prompt, concept_name, product_type, and
   appropriate aspect_ratio.

   After generation, extract the BASE64 data from the result and call
   upload_to_r2 with the base64 string and concept_name to get a public URL.

7. **Send approval request via Telegram.** Use send_approval_request to present
   the top 3 concepts to the owner. Include the concept name, description,
   target product type, and R2 image URL for each so the owner can see the
   designs before approving.

8. **Log to daily log.** Append to the daily log noting how many concepts were
   generated, the top picks, image generation results, and whether approval
   was requested.

9. **Update design inventory in Obsidian.** Append a summary to
   '98 - Hobson Builds Character/Content/Designs/Concepts/' listing all new
   concepts with their status.

Remember: you are Hobson. Your designs should make people laugh, nod in
recognition, and want to slap them on a water bottle or wear them to their
next trail run. Start with stickers and simple text-based designs.
The goal is volume and iteration, not perfection.
"""

DESIGN_BATCH_BOOTSTRAP_PROMPT = DESIGN_BATCH_PROMPT.replace(
    "7. **Send approval request via Telegram.** Use send_approval_request to present\n"
    "   the top 3 concepts to the owner. Include the concept name, description,\n"
    "   target product type, and R2 image URL for each so the owner can see the\n"
    "   designs before approving.",
    "7. **Create products on Printful.** For your top 3 ranked concepts, use\n"
    "   upload_design_file with the R2 image URL, then create_store_product to\n"
    "   create each one. Note: products may go live immediately, so only push\n"
    "   concepts you are confident in.\n"
    "\n"
    "   Then notify via Telegram with the product names, image URLs, and a note\n"
    "   that the owner should review them on Printful.",
)
```

**Step 2: Verify syntax**

```bash
python -c "import ast; ast.parse(open('hobson/src/hobson/workflows/design_batch.py').read()); print('Syntax OK')"
```

Expected: `Syntax OK`

**Step 3: Verify the .replace() works correctly**

```bash
python -c "
exec(open('hobson/src/hobson/workflows/design_batch.py').read())
assert 'generate_design_image' in DESIGN_BATCH_PROMPT
assert 'upload_to_r2' in DESIGN_BATCH_PROMPT
assert 'generate_design_image' in DESIGN_BATCH_BOOTSTRAP_PROMPT
assert 'upload_to_r2' in DESIGN_BATCH_BOOTSTRAP_PROMPT
assert 'send_approval_request' in DESIGN_BATCH_PROMPT
assert 'send_approval_request' not in DESIGN_BATCH_BOOTSTRAP_PROMPT
assert 'create_store_product' in DESIGN_BATCH_BOOTSTRAP_PROMPT
print('All assertions pass')
"
```

Expected: `All assertions pass`

**Step 4: Commit**

```bash
git add hobson/src/hobson/workflows/design_batch.py
git commit -m "feat: update design batch prompts with image gen, structured template, product focus"
```

---

### Task 8: Infrastructure setup (R2 bucket + credentials)

This task requires manual Cloudflare dashboard work and SSH access to CT 255.

**Step 1: Create R2 bucket in Cloudflare**

In the Cloudflare dashboard:
1. Go to R2 Object Storage
2. Create bucket named `hobson-designs`
3. Under Settings > Public Access, enable public access via `r2.dev` subdomain
4. Note the public URL (format: `https://pub-{hash}.r2.dev`)

**Step 2: Create R2 API token**

In Cloudflare dashboard:
1. Go to R2 > Manage R2 API Tokens
2. Create token with Object Read & Write permission on `hobson-designs` bucket
3. Note the Access Key ID and Secret Access Key

**Step 3: Add credentials to CT 255 .env**

SSH from Loki:
```bash
ssh root@192.168.2.16
pct exec 255 -- bash -c 'cat >> /root/builds-character/hobson/.env << EOF
# Cloudflare R2
R2_ACCOUNT_ID=<your-account-id>
R2_ACCESS_KEY_ID=<your-access-key>
R2_SECRET_ACCESS_KEY=<your-secret-key>
R2_BUCKET_NAME=hobson-designs
R2_PUBLIC_URL=https://pub-<hash>.r2.dev
EOF'
```

Replace `<placeholders>` with actual values from Step 2.

**Step 4: Verify credentials load**

```bash
pct exec 255 -- bash -c 'cd /root/builds-character/hobson && python -c "from hobson.config import settings; print(settings.r2_bucket_name, bool(settings.r2_access_key_id))"'
```

Expected: `hobson-designs True`

---

### Task 9: Deploy and install dependencies on CT 255

**Step 1: Push all code to GitHub**

```bash
git push
```

**Step 2: Pull on CT 255 and install new dependencies**

From Loki:
```bash
ssh root@192.168.2.16
pct exec 255 -- bash -c 'cd /root/builds-character && git pull && cd hobson && pip install -e ".[dev]"'
```

Expected: `google-genai` and `boto3` install successfully.

**Step 3: Restart Hobson service**

```bash
pct exec 255 -- systemctl restart hobson
```

**Step 4: Verify health**

```bash
pct exec 255 -- curl -s http://localhost:8080/health
```

Expected: `{"status":"ok",...}` with updated tool count (now 24 tools: 22 existing + generate_design_image + upload_to_r2).

**Step 5: Check logs for clean startup**

```bash
pct exec 255 -- journalctl -u hobson --no-pager -n 20
```

Expected: No import errors, scheduler starts with all jobs registered.

---

### Task 10: Trigger design batch workflow

**Step 1: Run the design batch manually**

From Loki:
```bash
pct exec 255 -- bash -c 'cd /root/builds-character/hobson && python -c "
import asyncio
from hobson.config import settings
from hobson.agent import create_agent
from hobson.workflows.design_batch import DESIGN_BATCH_BOOTSTRAP_PROMPT

async def run():
    agent = create_agent()
    result = await agent.ainvoke(
        {\"messages\": [{\"role\": \"user\", \"content\": DESIGN_BATCH_BOOTSTRAP_PROMPT}]},
        config={\"configurable\": {\"thread_id\": \"manual-design-batch\"}},
    )
    for msg in result[\"messages\"][-3:]:
        print(type(msg).__name__, \":\", str(msg.content)[:200])

asyncio.run(run())
"'
```

Expected: Agent generates concepts, creates images, uploads to R2, creates Printful products, sends Telegram notification.

**Step 2: Verify in PostgreSQL**

```bash
ssh root@192.168.2.13
pct exec 201 -- psql -U hobson -d project_data -c "SELECT concept_name, generation_status, image_width, image_height, image_url FROM hobson.design_generations ORDER BY created_at DESC LIMIT 5;"
```

Expected: 3 rows with status 'success' and populated image URLs.

**Step 3: Verify in R2**

Check that files exist at the public URLs returned by the query above. Open one in a browser to confirm the image loads.

**Step 4: Update STATE.md**

Update `STATE.md` to reflect image generation is live:
- Current Focus: Image generation active in bootstrap mode
- Status: Design batch now generates actual artwork via Imagen 4.0
- Known Issues: Any issues discovered during testing
