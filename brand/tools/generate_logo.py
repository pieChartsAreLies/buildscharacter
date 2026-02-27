"""Generate logo candidates using Gemini Imagen 4.0.

Usage: GOOGLE_API_KEY=<key> python3 generate_logo.py [batch_name]

Generates 4 candidates per prompt, saves all to brand/candidates/<batch_name>/
"""

import os
import sys
import base64
from pathlib import Path

from google import genai
from google.genai import types

API_KEY = os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    print("ERROR: Set GOOGLE_API_KEY environment variable")
    sys.exit(1)

BATCH_NAME = sys.argv[1] if len(sys.argv) > 1 else "explore"
OUTPUT_DIR = Path(__file__).parent.parent / "candidates" / BATCH_NAME
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

client = genai.Client(api_key=API_KEY)
MODEL = "imagen-4.0-generate-001"

# Brand context -- NO hex codes (Imagen renders them as literal text)
BRAND_CONTEXT = """
Brand: "Builds Character" with tagline "Thank Yourself Later."
A composure-driven philosophy brand for people who choose the hard path on purpose.
Not motivational, not loud. Measured, calm, dry, direct. Understatement carries authority.
The philosophy is universal: training, building, raising, creating, enduring.
Visual identity should feel: durable, scalable, quietly serious, engineered.
Should feel at home on a gym bag, a training journal, a workshop wall, a laptop lid,
or a nightstand.
Colors: deep charcoal/graphite, off-white/bone, burnt rust (sparingly), forest green (sparingly).
No gradients. No neon. Restraint equals credibility.
"""

# Round 2 prompts -- aligned to updated brand guidelines
PROMPTS = {
    "wordmark-clean": f"""
{BRAND_CONTEXT}
Design a typographic logo with two lines of text:
Line 1 (primary, larger, bold): BUILDS CHARACTER
Line 2 (smaller, lighter weight): Thank Yourself Later.
Use a clean geometric sans-serif typeface. All caps for the primary line with
slight letter tracking. The tagline in lighter weight, smaller, understated.
Deep charcoal on white background. No icon, no imagery. Pure typography.
The feel should be engineered and precise, like the branding on high-end
technical gear. Think Arc'teryx, Satisfy Running, or Tracksmith level of restraint.
Do NOT include any color codes, hashtags, or technical annotations in the image.
""",

    "wordmark-contrast": f"""
{BRAND_CONTEXT}
Design a typographic logo:
Line 1: BUILDS CHARACTER (bold, geometric sans-serif, tracked caps)
Line 2: Thank Yourself Later. (lighter weight, smaller, understated)
The word CHARACTER should have a subtle visual distinction: slightly different
weight, or a hairline rule above/below, or a minimal color accent in burnt rust.
Deep charcoal text on clean white background. No decorative elements. No icon.
The restraint IS the design. It should look like it belongs etched into metal
or debossed into leather.
Do NOT include any color codes or technical annotations.
""",

    "contour-mark": f"""
{BRAND_CONTEXT}
Design a logo combining a minimal abstract icon with text.
Icon: A single topographic contour line or elevation ring, abstract and geometric.
One continuous line forming an irregular closed shape, like a single contour from
a topo map. Simple enough to work at 16 pixels. One color, embroidery-safe.
Text below: BUILDS CHARACTER in clean geometric sans-serif, tracked caps.
Below that: Thank Yourself Later. in lighter weight.
Deep charcoal on white background, with the contour line in burnt rust.
Minimal, technical, engineered. Not decorative. Not playful.
Do NOT include any color codes or technical annotations.
""",

    "switchback-mark": f"""
{BRAND_CONTEXT}
Design a logo combining a minimal abstract icon with text.
Icon: An abstract switchback or zigzag path, like trail switchbacks viewed from
above on a topographic map. 3-4 clean angular turns. Geometric, not hand-drawn.
Simple enough to be a favicon at 16px. Single color, embroidery-safe.
Text: BUILDS CHARACTER in clean geometric sans-serif, tracked all-caps.
Below: Thank Yourself Later. in lighter weight.
Deep charcoal on white. The switchback mark in charcoal or burnt rust.
Should feel like technical cartography, not illustration.
Do NOT include any color codes or technical annotations.
""",

    "elevation-mark": f"""
{BRAND_CONTEXT}
Design a logo combining a minimal abstract icon with text.
Icon: A simple elevation profile line, like a cross-section of terrain.
A single horizontal line with one or two gradual rises and dips, representing
an elevation chart or horizon line. Minimal, geometric, abstract.
Must work at 16px as a favicon. One color. Embroidery-safe.
Text: BUILDS CHARACTER in geometric sans-serif, tracked all-caps, bold.
Below: Thank Yourself Later. in lighter weight, smaller.
Charcoal on white background. The elevation line in charcoal or burnt rust.
Engineered, precise, restrained. Like branding on precision instruments.
Do NOT include any color codes or technical annotations.
""",

    "needle-mark": f"""
{BRAND_CONTEXT}
Design a logo combining a minimal abstract icon with text.
Icon: A compass needle abstraction. Not a full compass rose, just the essential
needle form: a single elongated diamond or chevron pointing upward. Geometric,
sharp, abstract enough that it reads as a directional mark rather than a literal
compass. Must work at 16px. One color. Embroidery-safe.
Text: BUILDS CHARACTER in geometric sans-serif, tracked all-caps, bold.
Below: Thank Yourself Later. in lighter weight.
Deep charcoal on white. Needle in charcoal or burnt rust.
Quiet authority. Not decorative.
Do NOT include any color codes or technical annotations.
""",
}


def generate_batch(name: str, prompt: str):
    """Generate 4 candidates for a single prompt direction."""
    print(f"\n--- Generating: {name} ---")
    print(f"Prompt: {prompt[:100]}...")

    try:
        response = client.models.generate_images(
            model=MODEL,
            prompt=prompt.strip(),
            config=types.GenerateImagesConfig(
                number_of_images=4,
                aspect_ratio="1:1",
                include_rai_reason=True,
                output_mime_type="image/png",
            ),
        )
    except Exception as e:
        print(f"ERROR generating {name}: {e}")
        return

    if not response.generated_images:
        print(f"WARNING: No images returned for {name} (likely safety filter)")
        return

    for i, gi in enumerate(response.generated_images):
        img_data = gi.image.image_bytes
        if isinstance(img_data, str):
            img_data = base64.b64decode(img_data)
        out_path = OUTPUT_DIR / f"{name}-{i+1}.png"
        out_path.write_bytes(img_data)
        print(f"  Saved: {out_path}")

    print(f"  Generated {len(response.generated_images)} candidates")


if __name__ == "__main__":
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Model: {MODEL}")
    print(f"Generating {len(PROMPTS)} batches x 4 candidates = {len(PROMPTS) * 4} images\n")

    for name, prompt in PROMPTS.items():
        generate_batch(name, prompt)

    print(f"\n\nDone! Review candidates in: {OUTPUT_DIR}")
    print(f"Total directions: {len(PROMPTS)}")
