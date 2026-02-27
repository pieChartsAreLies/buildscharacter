"""One-off script: generate 20 sticker designs for manual selection.

Run on CT 255:
    cd /root/builds-character/hobson
    .venv/bin/python scripts/generate_sticker_batch.py

Outputs a summary with R2 URLs for each design.
"""

import asyncio
import json
import sys
import time

# Add src to path so we can import hobson modules
sys.path.insert(0, "src")

from hobson.tools.image_gen import generate_design_image

CONCEPTS = [
    {
        "name": "Thank Yourself Later",
        "text": "Thank Yourself Later.",
        "style": "Bold typographic sticker. Large sans-serif uppercase text, tight tracking. Charcoal text on transparent background. Clean edges, no decorative elements. The text is the entire design.",
    },
    {
        "name": "Effort Compounds",
        "text": "Effort Compounds.",
        "style": "Minimal typographic sticker. Clean uppercase sans-serif, medium weight. Single color charcoal on transparent background. Slightly condensed letterforms. No icons, no borders.",
    },
    {
        "name": "The Present Does the Work",
        "text": "The Present Does the Work.",
        "style": "Two-line typographic layout. 'The Present' on line one, 'Does the Work.' on line two. Bold uppercase sans-serif. Charcoal on transparent. Generous line spacing. Clean and architectural.",
    },
    {
        "name": "What You Carry Gets Lighter Eventually",
        "text": "What You Carry Gets Lighter. Eventually.",
        "style": "Typographic sticker with intentional line break. Main text in bold uppercase, 'Eventually.' smaller and offset below. Charcoal on transparent. The pause between lines is the design.",
    },
    {
        "name": "Nobody Asked You to Be Here",
        "text": "Nobody Asked You to Be Here.",
        "style": "Direct typographic sticker. Bold uppercase sans-serif, single line or tight two-line stack. Charcoal on transparent background. No softening, no decoration. Statement as design.",
    },
    {
        "name": "The Part You Dont Post About",
        "text": "The Part You Don't Post About",
        "style": "Understated typographic sticker. Medium weight uppercase sans-serif. Charcoal on transparent. Slightly smaller scale than other designs. Quiet confidence in the restraint.",
    },
    {
        "name": "Growth Is Not Accidental",
        "text": "Growth Is Not Accidental.",
        "style": "Typographic sticker with subtle contour line element. Bold text with a single thin topographic contour line curving behind it. Charcoal text, muted warm gray line. Transparent background.",
    },
    {
        "name": "Comfort Is a Direction",
        "text": "Comfort Is a Direction, Not a Destination.",
        "style": "Two-line typographic layout. Longer statement broken across two lines. Clean uppercase sans-serif, medium weight. Charcoal on transparent. The length of the statement is deliberate.",
    },
    {
        "name": "Earn the View",
        "text": "Earn the View.",
        "style": "Typographic sticker with minimal landscape element. Bold uppercase text with abstract elevation contour lines below, suggesting terrain. Charcoal text, thin line work. Transparent background.",
    },
    {
        "name": "Not Yet",
        "text": "Not Yet.",
        "style": "Extremely minimal typographic sticker. Two words, period. Large bold uppercase sans-serif centered. Charcoal on transparent. The brevity is the statement. Maximum whitespace ratio.",
    },
    {
        "name": "One More",
        "text": "One More.",
        "style": "Minimal typographic sticker. Two words, large scale, bold uppercase. Charcoal on transparent background. No context needed. Clean, architectural letterforms.",
    },
    {
        "name": "The Work Is the Point",
        "text": "The Work Is the Point.",
        "style": "Typographic sticker. Clean uppercase sans-serif, bold weight. Single line or tight two-line stack. Charcoal on transparent. No ornamentation.",
    },
    {
        "name": "You Already Know",
        "text": "You Already Know.",
        "style": "Typographic sticker with quiet authority. Medium-bold uppercase sans-serif. Charcoal on transparent. Slightly wider tracking than other designs. Feels like an acknowledgment, not a command.",
    },
    {
        "name": "Built Slowly",
        "text": "Built Slowly.",
        "style": "Minimal typographic sticker. Two words in bold uppercase with extra-wide letter spacing. Charcoal on transparent. The spacing itself communicates patience. Clean and deliberate.",
    },
    {
        "name": "Rest Is Earned",
        "text": "Rest Is Earned.",
        "style": "Typographic sticker. Bold uppercase sans-serif. Charcoal on transparent background. Three words, direct statement. No softening elements.",
    },
    {
        "name": "Show Up Anyway",
        "text": "Show Up Anyway.",
        "style": "Typographic sticker. Bold uppercase sans-serif, tight tracking. Charcoal on transparent. Reads as resolve, not motivation. The period is essential.",
    },
    {
        "name": "Quiet Work",
        "text": "Quiet Work.",
        "style": "Minimal typographic sticker. Two words in lighter weight uppercase sans-serif. Charcoal on transparent. The lighter weight matches the meaning. Understated presence.",
    },
    {
        "name": "Choose Your Difficult",
        "text": "Choose Your Difficult.",
        "style": "Typographic sticker. Bold uppercase sans-serif. Charcoal on transparent background. 'Difficult' used as a noun. Clean, architectural layout.",
    },
    {
        "name": "Character Takes Time",
        "text": "Character Takes Time.",
        "style": "Typographic sticker with subtle abstract element. Bold text with faint concentric contour rings behind, suggesting growth rings or topographic elevation. Charcoal text, very faint warm gray rings. Transparent background.",
    },
    {
        "name": "Contour Lines Badge",
        "text": "BUILDS CHARACTER",
        "style": "Badge-style sticker. 'BUILDS CHARACTER' in bold uppercase sans-serif arced across the top, with abstract topographic contour lines forming the central design element. Single color charcoal. Circular or rounded shape. No mountains, no birds. The contour lines suggest terrain without depicting it literally. Transparent background.",
    },
]

PROMPT_TEMPLATE = """Design a premium die-cut sticker for the brand "Builds Character."

Text on sticker: "{text}"

Style direction: {style}

Technical requirements:
- Die-cut sticker format, transparent/clean background
- Must be legible at 3-4 inch sticker scale
- One-color capable (charcoal #1a1a1a primary)
- No borders, no watermarks, no drop shadows
- No cartoon style, no clip art, no playful elements
- No photorealistic elements, no faces
- Typography-forward: the text IS the design
- If using any iconography, keep it abstract and terrain-based (contour lines, elevation marks)
- Professional, durable, quietly serious aesthetic
- Would feel at home on a water bottle, laptop, or journal cover
"""


async def main():
    results = []
    total = len(CONCEPTS)

    print(f"Generating {total} sticker designs...")
    print("=" * 60)

    for i, concept in enumerate(CONCEPTS, 1):
        name = concept["name"]
        prompt = PROMPT_TEMPLATE.format(text=concept["text"], style=concept["style"])

        print(f"\n[{i}/{total}] Generating: {name}")
        start = time.time()

        try:
            result_json = await generate_design_image.ainvoke({
                "prompt": prompt,
                "concept_name": name,
                "product_type": "sticker",
                "aspect_ratio": "1:1",
            })
            result = json.loads(result_json)
            elapsed = time.time() - start

            if result.get("status") == "success":
                print(f"  OK: {result['image_url']} ({result['width']}x{result['height']}) [{elapsed:.1f}s]")
                results.append({
                    "index": i,
                    "name": name,
                    "text": concept["text"],
                    "url": result["image_url"],
                    "width": result["width"],
                    "height": result["height"],
                    "generation_id": result.get("generation_id"),
                })
            else:
                print(f"  FAILED: {result.get('message', 'unknown error')} [{elapsed:.1f}s]")
                results.append({
                    "index": i,
                    "name": name,
                    "text": concept["text"],
                    "url": None,
                    "error": result.get("message"),
                })
        except Exception as e:
            elapsed = time.time() - start
            print(f"  ERROR: {e} [{elapsed:.1f}s]")
            results.append({
                "index": i,
                "name": name,
                "text": concept["text"],
                "url": None,
                "error": str(e),
            })

        # Brief pause to avoid rate limiting
        if i < total:
            time.sleep(2)

    # Print summary
    print("\n" + "=" * 60)
    print("GENERATION SUMMARY")
    print("=" * 60)

    successful = [r for r in results if r.get("url")]
    failed = [r for r in results if not r.get("url")]

    print(f"\nSuccessful: {len(successful)}/{total}")
    if failed:
        print(f"Failed: {len(failed)}/{total}")

    print("\n--- DESIGNS FOR REVIEW ---\n")
    for r in successful:
        print(f"{r['index']:2d}. {r['name']}")
        print(f"    Text: \"{r['text']}\"")
        print(f"    URL:  {r['url']}")
        print(f"    Size: {r['width']}x{r['height']}")
        print()

    if failed:
        print("\n--- FAILED ---\n")
        for r in failed:
            print(f"{r['index']:2d}. {r['name']}: {r.get('error', 'unknown')}")

    # Save results to JSON for easy reference
    with open("scripts/sticker_batch_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nFull results saved to scripts/sticker_batch_results.json")


if __name__ == "__main__":
    asyncio.run(main())
