# Shop Overhaul + "Build Character" Rebrand

> Design document for overhauling the BuildsCharacter.com shop: rebranding to "Build Character," switching to a sticker-first product strategy, adding Printful mockup images, and fixing artwork resolution issues.

## Problem Statement

The current shop has four issues:
1. Product images show raw artwork (flat PNGs), not products. Customers can't see what they're buying.
2. Artwork quality is inconsistent: some designs have checkered transparency artifacts, others don't.
3. Product mix is wrong: 3 mugs + 1 t-shirt, zero stickers. Stickers should be the primary SKU (cheap, impulse buys, low risk).
4. Branding uses "This Builds Character" when "Build Character" is tighter and more effective.

Additionally, the Printful storefront (`buildscharacter.printful.me`) hasn't been verified as functional for actual customer orders.

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Product images | Printful Mockup Generator API | Automated, realistic, consistent. Shows designs on actual products. |
| Sticker resolution gap | Pillow LANCZOS upscale (1024->1500+) | Zero new dependencies (Pillow already imported). Quality is fine for bold/graphic sticker designs. |
| Existing products | Remove all 4 | Clean slate. Relaunch with stickers only. |
| Branding | "Build Character" (drop "This") | Simpler, cleaner, more direct. Domain stays buildscharacter.com. |

## Workstream 1: Rebrand to "Build Character"

Update "This Builds Character" to "Build Character" across:
- `brand/brand_guidelines.md` -- example headlines, example design text, any references
- `hobson/src/hobson/workflows/design_batch.py` -- prompt examples that reference the old phrasing
- `site/src/pages/shop.astro` -- page subtitle/description copy
- Product markdown files (being deleted anyway, but verify no stale references elsewhere)

The domain `buildscharacter.com` stays unchanged. The Printful storefront URL stays unchanged. These are infrastructure, not brand copy.

## Workstream 2: LANCZOS Upscaling in Image Generation

Modify `hobson/src/hobson/tools/image_gen.py`:

**Current behavior:** Imagen 4.0 generates 1024x1024 images. `_check_dimensions()` logs a warning if below Printful minimums but does nothing about it. Stickers require 1500x1500.

**New behavior:** After image selection and before R2 upload, if the image is below the minimum dimensions for its target product type, upscale using `PIL.Image.resize()` with `Image.LANCZOS` resampling to meet the minimum. Log the upscale operation. Upload the upscaled version.

This unblocks stickers as a product type with zero new dependencies.

## Workstream 3: Printful Mockup Generator Integration

Add new functions to `hobson/src/hobson/tools/printful.py`:

### `get_mockup_styles(catalog_product_id: int) -> str`
- Calls `GET /v2/catalog-products/{id}/mockup-styles`
- Returns available style IDs and names for a product
- Used to discover which mockup style to request

### `generate_product_mockup(catalog_product_id: int, catalog_variant_id: int, design_image_url: str) -> str`
- Calls `get_mockup_styles` internally to discover available styles
- **Style selection logic:** Use the default mockup style (`default_mockup_styles=true` query param). If no default exists, pick the first style in the list. No LLM decision-making needed.
- Calls `POST /v2/mockup-generator` to create a mockup task
- **Polling spec:** Poll `GET /v2/mockup-tasks?id={task_id}` every 5 seconds, max 2 minutes total. Terminal states: "completed" (success) or "failed" (give up).
- Downloads the mockup image from Printful's temporary URL
- Uploads it to R2 for permanence (Printful tmp URLs expire)
- **Fallback on failure:** If mockup generation fails or times out, return the raw design image URL instead. The `image` field in the product markdown always gets a valid URL either way. Log a warning so failures are visible.
- Returns JSON with the permanent R2 mockup URL (or raw design URL on fallback)

### Design batch workflow update
Update `design_batch.py` prompt to:
1. After creating a Printful product, call `get_mockup_styles` to find available styles
2. Call `generate_product_mockup` to get a realistic product image
3. Use the mockup URL (not the raw design URL) as the `image` field in the product markdown

## Workstream 4: Shop Cleanup + Printful Pipeline

### Code changes
- Delete all 4 product markdown files from `site/src/data/products/`
- No schema changes needed (`sticker` is already in the `product_type` enum)

### Manual Printful setup (human task, not code)
The user needs to verify in the Printful dashboard:
1. Payment gateway connected (Stripe or PayPal) for customer checkout
2. Shipping settings configured
3. Billing information set up
4. Storefront (`buildscharacter.printful.me`) set to active
5. Existing mugs/t-shirt products reviewed and removed from the Printful store
6. Store branding updated to reflect "Build Character"

## File Changes Summary

| File | Action | What |
|---|---|---|
| `brand/brand_guidelines.md` | Edit | Rebrand references to "Build Character" |
| `hobson/src/hobson/tools/image_gen.py` | Edit | Add LANCZOS upscaling after image selection |
| `hobson/src/hobson/tools/printful.py` | Edit | Add `get_mockup_styles` and `generate_product_mockup` tools |
| `hobson/src/hobson/workflows/design_batch.py` | Edit | Update prompt: rebrand text + mockup generation step |
| `site/src/pages/shop.astro` | Edit | Rebrand page copy |
| `site/src/data/products/*.md` | Delete | Remove all 4 existing product files |

## Risks

| Risk | Mitigation |
|---|---|
| Printful mockup API is async; could be slow or fail | Poll every 5s, max 2min. On failure/timeout, fall back to raw design URL. No special schema field needed. |
| LANCZOS upscale from 1024->1500 could look soft on detailed designs | Acceptable for bold text/graphic sticker designs. Revisit if quality is visibly bad. |
| Printful tmp mockup URLs expire | Download and re-upload to R2 for permanent storage |
| Printful storefront not configured for checkout | Documented as manual human task with specific checklist |
