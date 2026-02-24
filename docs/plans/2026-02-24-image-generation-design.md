# Image Generation Integration Design

**Date:** 2026-02-24
**Status:** Approved

## Goal

Add Gemini Imagen image generation to Hobson's design batch workflow so he can create actual product designs (not just text concepts) and push them to Printful with real artwork.

## Decisions

| Decision | Choice | Reasoning |
|---|---|---|
| Image generation model | Gemini Imagen 4.0 (`imagen-4.0-generate-001`) | Consistent with tiered LLM strategy (Gemini for lower-stakes creative work). No Midjourney dependency. |
| Image hosting | Cloudflare R2 | S3-compatible, free egress, 10GB free storage, already on CF account. No new service. |
| R2 client | boto3 | Standard S3-compatible client. Well-documented, reliable. |
| SDK | google-genai (unified SDK) | New unified SDK replaces deprecated google-generativeai. |
| Images per concept | 4 generated, 1 selected | Generate 4 candidates, use Gemini Flash vision to rank and select best. Reduces unusable output risk. |
| Product focus | Low-cost impulse buys first | Stickers, pins, small prints during early inventory. Premium items after traffic data. |
| Image gen in steady-state | Yes | Include generated images in Telegram approval so owner sees what they're approving. |
| Filename strategy | UUID prefix | `{uuid4}-{sanitized-name}.png` prevents R2 overwrites from name collisions. |
| Data provenance | PostgreSQL | Store generation prompt, model version, image URL, and status for every attempt. |

## Architecture

```
Design Batch Workflow
  |
  1. Review store inventory
  2. Read brand guidelines + past concepts
  3. Generate 5-10 design concepts (text only)
  4. Save concepts to Obsidian
  5. Rank top 3
  |
  NEW STEPS:
  6. For each top 3: write structured Imagen prompt from concept
  7. Call generate_design_image (generates 4, ranks via vision, returns best)
  8. Call upload_to_r2 -> get public URL (UUID-prefixed filename)
  9. Log generation metadata to PostgreSQL
  |
  10. Create Printful product with image URL (bootstrap)
      OR send approval with image URLs (steady-state)
  11. Notify via Telegram
  12. Log activity
```

## New Tools

### generate_design_image

File: `hobson/src/hobson/tools/image_gen.py`

LangGraph tool that calls Gemini Imagen API, generates multiple candidates, and uses Gemini Flash vision to select the best one.

Parameters:
- `prompt` (str): Detailed image generation prompt (agent writes this from concept + brand guidelines)
- `aspect_ratio` (str, default "1:1"): One of "1:1", "3:4", "4:3", "9:16", "16:9"
- `concept_name` (str): Human-readable concept name for logging
- `product_type` (str): Target product type (e.g., "sticker", "pin", "poster") for validation

Returns: dict with `image_base64` (str), `generation_prompt` (str), `model_version` (str).

Implementation:
- Uses `google.genai.Client` with `settings.google_api_key`
- Calls `client.models.generate_images()` with `imagen-4.0-generate-001`
- `number_of_images=4`
- Uses Gemini 2.5 Flash to rank the 4 candidates against the prompt and brand guidelines, selecting the best one
- Validates image dimensions against product type minimum requirements (see Product Image Requirements below)
- Returns the selected image as base64 + metadata
- Error handling:
  - Retries transient API errors (network, rate-limit) with exponential backoff (3 attempts)
  - If safety filters block all images, returns error status with reason (does not crash)
  - If generated image is below minimum resolution for product type, logs warning and returns it anyway (agent decides whether to use)

### upload_to_r2

File: `hobson/src/hobson/tools/image_gen.py` (same file)

LangGraph tool that uploads image bytes to Cloudflare R2 and returns a public URL.

Parameters:
- `image_base64` (str): Base64-encoded image bytes
- `concept_name` (str): Human-readable name (used in filename after UUID prefix)

Returns: Public URL string (e.g., `https://{r2_public_url}/designs/{uuid}-{name}.png`)

Implementation:
- Uses `boto3` S3 client pointed at R2 endpoint (`https://{account_id}.r2.cloudflarestorage.com`)
- Generates filename: `{uuid.uuid4()}-{sanitized_concept_name}.png`
- Decodes base64, uploads to `designs/{filename}` in the bucket
- Sets `ContentType: image/png`
- Returns `{r2_public_url}/designs/{filename}`

## Product Image Requirements

Minimum dimensions by product type (from Printful specs):

| Product Type | Min Width | Min Height | Notes |
|---|---|---|---|
| Sticker | 1500px | 1500px | Die-cut, needs transparent background |
| Pin | 1000px | 1000px | Simple, bold designs work best |
| Small print (8x10) | 2400px | 3000px | 300 DPI at print size |
| Poster (18x24) | 5400px | 7200px | 300 DPI at print size |
| T-shirt | 4500px | 5100px | Front print area |

The agent should check these after generation and log a warning if the image is undersized. During early inventory (stickers, pins), Imagen output should be sufficient.

## Structured Prompt Template

The agent fills in this template when writing Imagen prompts (replaces the free-form "write a prompt" instruction):

```
Subject: [core design idea from concept]
Style: [art style matching brand guidelines, e.g., "minimalist line art", "vintage outdoor poster", "bold vector illustration"]
Composition: [layout guidance, e.g., "centered on transparent background", "isolated subject on white", "full-bleed landscape"]
Color palette: [from brand guidelines or concept-specific]
Product context: [target product type and its constraints]
Negative: [what to exclude, e.g., "no text, no borders, no photorealistic faces, no watermarks"]
```

The agent assembles the final Imagen prompt from these fields. This ensures consistent quality and brand alignment across all generated images.

## Data Provenance

### New PostgreSQL table: `hobson.design_generations`

```sql
CREATE TABLE hobson.design_generations (
    id SERIAL PRIMARY KEY,
    concept_name TEXT NOT NULL,
    generation_prompt TEXT NOT NULL,
    model_version VARCHAR(100) NOT NULL,
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

Every generation attempt is logged, whether it succeeds, fails, or gets filtered. This enables debugging bad designs, reproducing good ones, and tracking generation quality over time.

## Config Changes

Add to `Settings` in `config.py`:

```python
# Cloudflare R2 (design image storage)
r2_account_id: str = ""
r2_access_key_id: str = ""
r2_secret_access_key: str = ""
r2_bucket_name: str = "hobson-designs"
r2_public_url: str = ""  # e.g., https://pub-{hash}.r2.dev
```

## Workflow Prompt Changes

### Both modes (add to base prompt before step 6)

Add product focus directive:
> "Prioritize low-cost, impulse-buy products (stickers, pins, small prints) during early inventory building. Save premium items (hoodies, posters) for after you have traffic data showing demand."

### Both modes (new step after ranking)

Insert structured image generation step:
> "For each of your top 3 concepts, write a structured image generation prompt using this template:
> - Subject: the core design idea
> - Style: art style matching our brand (minimalist, bold, outdoor-inspired)
> - Composition: layout for the target product (centered on transparent background for stickers, etc.)
> - Color palette: from brand guidelines or concept-specific
> - Product context: what product this will go on
> - Negative: things to exclude (no text, no borders, no watermarks)
>
> Generate the image using generate_design_image (which generates 4 candidates and selects the best). Then upload it to R2 using upload_to_r2. Use the returned URL when creating the Printful product."

### Steady-state addition

> "Include the R2 image URLs in your Telegram approval request so the owner can see the designs before approving."

## Dependencies

- `google-genai` (pip install, may already be installed via langchain-google-genai)
- `boto3` (pip install)
- `Pillow` (pip install, for image dimension validation)

## Agent Tool Registration

Add `generate_design_image` and `upload_to_r2` to `_COMMON_TOOLS` in `agent.py` (available in both modes).

## Files Changed

| File | Change |
|---|---|
| `hobson/src/hobson/config.py` | Add R2 settings (5 fields) |
| `hobson/src/hobson/tools/image_gen.py` | New: generate_design_image + upload_to_r2 tools |
| `hobson/src/hobson/agent.py` | Add image tools to _COMMON_TOOLS |
| `hobson/src/hobson/workflows/design_batch.py` | Update both prompts with image gen steps + product focus + structured prompt template |
| CT 255 `.env` | Add R2 credentials |
| `hobson/pyproject.toml` | Add google-genai, boto3, Pillow dependencies |
| PostgreSQL CT 201 | Create `hobson.design_generations` table |

## Infrastructure Setup (Manual)

1. Create R2 bucket `hobson-designs` in Cloudflare dashboard
2. Enable public access on the bucket
3. Create R2 API token (S3 auth) with read/write on the bucket
4. Add credentials to CT 255 `.env`
5. Create `hobson.design_generations` table on CT 201
