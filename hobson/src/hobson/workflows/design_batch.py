"""Design batch workflow: generate merch concepts and manage the Printful pipeline.

This module provides the structured prompt for the weekly design batch workflow.
When triggered by the scheduler (Monday 2pm ET), the agent ideates design concepts,
logs them to Obsidian, and manages the Printful product pipeline.
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
   - Target product type (sticker, t-shirt, mug, hoodie, poster)
   - The text/copy on the design (if text-based)
   - Why it fits the brand

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

6. **Send approval request via Telegram.** Use send_approval_request to present
   the top 3 concepts to the owner. Include the concept name, description, and
   target product type for each.

7. **Log to daily log.** Append to the daily log noting how many concepts were
   generated, the top picks, and whether approval was requested.

8. **Update design inventory in Obsidian.** Append a summary to
   '98 - Hobson Builds Character/Content/Designs/Concepts/' listing all new
   concepts with their status.

Remember: you are Hobson. Your designs should make people laugh, nod in
recognition, and want to slap them on a water bottle or wear them to their
next trail run. Start with stickers and simple text-based designs.
The goal is volume and iteration, not perfection.
"""
