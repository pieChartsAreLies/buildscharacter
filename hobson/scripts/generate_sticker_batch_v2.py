"""One-off script: generate 20 sticker designs v2 - clean typography, no terrain.

Run on CT 255:
    cd /root/builds-character/hobson
    .venv/bin/python scripts/generate_sticker_batch_v2.py
"""

import asyncio
import json
import sys
import time

sys.path.insert(0, "src")

from hobson.tools.image_gen import generate_design_image

CONCEPTS = [
    {"name": "Thank Yourself Later", "text": "THANK YOURSELF LATER\nBuilds Character"},
    {"name": "Hard Work", "text": "HARD WORK\nBuilds Character"},
    {"name": "Parenting", "text": "PARENTING\nBuilds Character"},
    {"name": "The High Road", "text": "THE HIGH ROAD\nBuilds Character"},
    {"name": "Make the Hard Choice", "text": "MAKE THE HARD CHOICE\nBuilds Character"},
    {"name": "Early Mornings", "text": "EARLY MORNINGS\nBuilds Character"},
    {"name": "Patience", "text": "PATIENCE\nBuilds Character"},
    {"name": "Starting Over", "text": "STARTING OVER\nBuilds Character"},
    {"name": "Saying No", "text": "SAYING NO\nBuilds Character"},
    {"name": "The Long Way", "text": "THE LONG WAY\nBuilds Character"},
    {"name": "Doing It Again", "text": "DOING IT AGAIN\nBuilds Character"},
    {"name": "Showing Up", "text": "SHOWING UP\nBuilds Character"},
    {"name": "Honest Work", "text": "HONEST WORK\nBuilds Character"},
    {"name": "Discomfort", "text": "DISCOMFORT\nBuilds Character"},
    {"name": "Effort Compounds", "text": "EFFORT COMPOUNDS\nBuilds Character"},
    {"name": "The Boring Parts", "text": "THE BORING PARTS\nBuilds Character"},
    {"name": "Raising the Bar", "text": "RAISING THE BAR\nBuilds Character"},
    {"name": "Staying Late", "text": "STAYING LATE\nBuilds Character"},
    {"name": "One More Rep", "text": "ONE MORE REP\nBuilds Character"},
    {"name": "Losing Gracefully", "text": "LOSING GRACEFULLY\nBuilds Character"},
]

PROMPT_TEMPLATE = """Design a premium die-cut sticker with ONLY text, no imagery whatsoever.

The sticker has two lines of text:
Line 1 (large, bold): "{line1}"
Line 2 (smaller, underneath): "Builds Character"

Layout: The main phrase is large, bold, uppercase sans-serif (like Helvetica Bold or similar clean grotesque). "Builds Character" sits directly underneath in smaller, lighter weight text. Centered alignment. Clean white or transparent background.

CRITICAL REQUIREMENTS:
- ONLY typography. No icons. No illustrations. No mountains. No contour lines. No terrain. No decorative elements of any kind.
- No borders, no frames, no shapes behind the text.
- No watermarks, no drop shadows, no gradients.
- Charcoal/dark gray text (#1a1a1a) only.
- Clean, professional, minimal. Think Supreme box logo level of simplicity but without the box.
- The text must be perfectly spelled and legible.
- Die-cut sticker shape that follows the text outline.
- Would look at home on a water bottle, laptop, car bumper, or journal.
"""


async def main():
    results = []
    total = len(CONCEPTS)

    print(f"Generating {total} sticker designs (v2 - clean typography)...")
    print("=" * 60)

    for i, concept in enumerate(CONCEPTS, 1):
        name = concept["name"]
        # Extract line 1 from the text (everything before \n)
        line1 = concept["text"].split("\n")[0]
        prompt = PROMPT_TEMPLATE.format(line1=line1)

        print(f"\n[{i}/{total}] Generating: {name}")
        start = time.time()

        try:
            result_json = await generate_design_image.ainvoke({
                "prompt": prompt,
                "concept_name": f"v2-{name.lower().replace(' ', '-')}",
                "product_type": "sticker",
                "aspect_ratio": "1:1",
            })
            result = json.loads(result_json)
            elapsed = time.time() - start

            if result.get("status") == "success":
                print(f"  OK: {result['image_url']} [{elapsed:.1f}s]")
                results.append({
                    "index": i,
                    "name": name,
                    "text": concept["text"],
                    "url": result["image_url"],
                })
            else:
                print(f"  FAILED: {result.get('message', 'unknown')} [{elapsed:.1f}s]")
                results.append({"index": i, "name": name, "url": None, "error": result.get("message")})
        except Exception as e:
            elapsed = time.time() - start
            print(f"  ERROR: {e} [{elapsed:.1f}s]")
            results.append({"index": i, "name": name, "url": None, "error": str(e)})

        if i < total:
            time.sleep(2)

    print("\n" + "=" * 60)
    successful = [r for r in results if r.get("url")]
    failed = [r for r in results if not r.get("url")]
    print(f"Successful: {len(successful)}/{total}")

    for r in successful:
        print(f"{r['index']:2d}. {r['name']:30s} {r['url']}")

    with open("scripts/sticker_batch_v2_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to scripts/sticker_batch_v2_results.json")


if __name__ == "__main__":
    asyncio.run(main())
