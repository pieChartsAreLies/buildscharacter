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

   The result is JSON with generation_id and image_base64. Pass the
   image_base64, concept_name, and generation_id to upload_to_r2 to get
   a public URL.

7. **Send approval request via Telegram.** Use send_approval_request to present
   the top 3 concepts to the owner. Include the concept name, description,
   target product type, and R2 image URL (from upload_to_r2 result) for each
   so the owner can see the designs before approving.

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
    "   target product type, and R2 image URL (from upload_to_r2 result) for each\n"
    "   so the owner can see the designs before approving.",
    "7. **Create products on Printful.** For your top 3 ranked concepts, use\n"
    "   upload_design_file with the R2 image URL, then create_store_product to\n"
    "   create each one. Note: products may go live immediately, so only push\n"
    "   concepts you are confident in.\n"
    "\n"
    "   Then notify via Telegram with the product names, image URLs, and a note\n"
    "   that the owner should review them on Printful.",
)
