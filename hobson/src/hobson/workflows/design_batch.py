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
   - A name (short, deliberate, brand-aligned)
   - A description (what the design looks like)
   - Target product type (sticker, pin, small print, t-shirt, poster)
   - The text/copy on the design (if text-based)
   - Why it fits the brand

   Prioritize low-cost, impulse-buy products (stickers, pins, small prints) during
   early inventory building. Save premium items (hoodies, posters) for after you
   have traffic data showing demand.

   If it looks like a sticker, it is wrong. If it looks like a creed, it is right.
   Focus on the deliberate difficulty philosophy. Think:
   - Stickers with terse statements that read like principles
   - T-shirts with minimal text that signals earned experience
   - Mugs with quiet resolve, not self-deprecation
   - Posters with statements that need no explanation

   Examples of on-brand design text:
   - "Thank Yourself Later" (tagline, universal)
   - "Conditions Were Suboptimal" (earned understatement)
   - "Effort Compounds" (core idea, minimal)
   - "Type II" (endurance terminology, abstract)
   - "Tuesday. Again." (quiet resolve)

4. **Save concepts to Obsidian.** Write each concept as a note in
   '98 - Hobson Builds Character/Content/Designs/Concepts/' with:
   - YAML frontmatter: title, status (concept), product_type, created date
   - Full concept description

5. **Rank and select top 3.** Evaluate concepts on:
   - Credibility (would someone who actually does this wear it?)
   - Brand alignment (does it match the voice?)
   - Production feasibility (simple designs are better for POD)
   - Market fit (does the target audience want this?)

6. **Generate images for top 3.** For each of your top 3 concepts, write a
   structured image generation prompt using this template:

   - Subject: the core design idea
   - Style: one-color capable, embroidery-safe, abstract terrain-based
     iconography (contour lines, elevation marks, compass abstractions).
     No literal mountains with birds. No clip art.
   - Composition: layout for the target product (centered on transparent
     background for stickers, isolated subject for pins, full design for prints)
   - Color palette: charcoal (#1a1a1a), bone (#f5f0eb), forest green (#2d5016),
     burnt rust (#8b4513). Use sparingly. Most designs should work in one color.
   - Product context: what product this will go on and its constraints
   - Negative: things to exclude (no text unless the concept IS text-based,
     no borders, no watermarks, no photorealistic faces, no cartoon style,
     no bright colors, no playful elements)

   Assemble these fields into a single detailed prompt, then call
   generate_design_image with the prompt, concept_name, product_type, and
   appropriate aspect_ratio.

   The result is JSON with image_url (the public R2 URL), generation_id,
   width, height, and other metadata. The image is automatically uploaded
   to R2 during generation. Use the image_url for Printful and Telegram.

7. **Send approval request via Telegram.** Use send_approval_request to present
   the top 3 concepts to the owner. Include the concept name, description,
   target product type, and image URL (from generate_design_image result) for
   each so the owner can see the designs before approving.

8. **Generate product mockups.** For each product created on Printful, call
   generate_product_mockup with the catalog_product_id, catalog_variant_id,
   design image URL (from generate_design_image result), and concept name.

   This generates a realistic photo of the design on the actual product
   (e.g., sticker on a surface, mug on a desk). The mockup image is
   automatically uploaded to R2 for permanent storage.

   If mockup generation fails, the tool falls back to the raw design URL.
   Either way, you get an image_url in the response to use in step 9.

9. **Publish product to site.** For each product created on Printful, call
   the publish_product tool with these parameters:

   - slug: lowercase-hyphenated product name (e.g. "effort-compounds-sticker")
   - name: Product display name (e.g. "Effort Compounds Sticker")
   - description: 1-2 sentence product description
   - price: Retail price as a string (e.g. "4.99" for stickers, "14.99" for
     mugs, "24.99" for t-shirts)
   - image_url: The mockup URL from generate_product_mockup (step 8). If mockup
     generation failed, use the design URL from generate_design_image (step 6).
   - printful_url: "https://buildscharacter.printful.me"
   - product_type: One of sticker, mug, pin, print, poster, t-shirt

   This tool writes the product markdown file to site/src/data/products/{slug}.md
   on the master branch via GitHub API and triggers a Cloudflare Pages deploy.
   No separate git commit or PR step is needed.

10. **Log to daily log.** Append to the daily log noting how many concepts were
    generated, the top picks, image generation results, mockup results, and
    whether approval was requested.

11. **Update design inventory in Obsidian.** Append a summary to
    '98 - Hobson Builds Character/Content/Designs/Concepts/' listing all new
    concepts with their status.

Your designs should feel durable, scalable, and quietly serious. Engineered,
not playful. Start with stickers and simple text-based designs. The goal is
volume and iteration, not perfection.
"""

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
