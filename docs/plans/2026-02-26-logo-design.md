# Build Character Logo Design

**Date:** 2026-02-26
**Status:** Approved (revised after adversarial review)

## Concept: The Ironbound Shield

A shield made of rough-hewn planks, bound by iron bands. Brutalist, functional, not decorative. Built to take hits and hold together. "BUILD CHARACTER" stamped into the surface.

One iron band is visibly bent, and one plank is slightly misaligned or cracked. This isn't damage to be fixed; it's proof of use. The shield works. It just has a story.

**What it communicates:** This held together. Character is forged through resistance, not polish. The imperfections are the point.

**Brand alignment:** Dry, earned, unpretentious. The bent band says "we know a shield is a bit much, but look, this one's been through it." Self-aware, not heraldic.

## Visual Specification

### Design Philosophy: Brutalist Vector

No gradients, no filters, no dimensional effects. All visual interest comes from path design: intentionally imperfect lines, slightly irregular shapes, hand-drawn-feeling geometry. Think stenciled on equipment, not rendered in Photoshop. This approach is production-ready for embroidery, screen printing, laser etching, and digital use.

### Shape & Structure

- **Shield silhouette:** Pointed bottom, flat top. Heater shield proportions (~5:6 width-to-height). Outline path is slightly irregular (not mathematically perfect, 3-4 nodes per edge manually offset 1-2px to create hand-cut feel).
- **Planks:** 3 vertical division lines inside the shield. Simple straight paths with slight wave (2-3 nodes each, subtle deviation). No fill texture, just lines implying planks.
- **Iron bands:** Two horizontal bands crossing the planks, upper third and lower third. Solid filled rectangles, no gradient. The lower band has a visible bend/kink at one point (a single node offset downward ~3px), showing it's taken an impact.
- **Rivets:** 6 filled circles (no highlight dots, no effects) at band-plank intersections. ~3px radius at full size.
- **Story detail:** One plank division line has a crack branching off at ~45 degrees, roughly 15-20px long at full size. Thin stroke, same weight as plank lines.

### Typography

- "BUILD" centered above the upper iron band, "CHARACTER" centered below the lower iron band. Slight arc following shield contour.
- **Typeface:** Space Grotesk Bold, converted to paths. 4-5 nodes per character manually shifted 0.5-1px to create a stamped/branded look through geometry, not filters.
- Text is part of the vector paths, not live text.

### BC Monogram (Avatar Mark)

- **Layout:** "B" and "C" stacked vertically, centered between the two iron bands.
- **Style:** Space Grotesk Bold, converted to paths with the same manual roughening as the full text (4-5 nodes shifted per letter).
- **Size:** Letters fill ~60% of the space between bands. Tight vertical spacing (4px gap at full size).
- **Standalone use:** The monogram works inside the shield (avatar) or alone on a plain background (watermark).

### Color Palette (Brand Colors Only)

| Element | Color | Hex |
|---------|-------|-----|
| Shield outline | Charcoal | #1a1a1a |
| Plank lines & crack | Charcoal | #1a1a1a |
| Iron bands | Rust | #c45d3e |
| Rivets | Rust | #c45d3e |
| Text | Charcoal | #1a1a1a |
| Background (light) | Offwhite | #f5f0eb |
| Background (dark) | Charcoal | #1a1a1a |
| Inverted text/lines | Offwhite | #f5f0eb |

No off-palette colors. The rust iron bands against charcoal structure create visual hierarchy using only the brand palette.

### Responsive Versions

| Context | Size | Content |
|---------|------|---------|
| Favicon | 16-128px | Shield outline only with two horizontal bars inset from edges. No text, no plank lines, no rivets, no crack. Single color (charcoal or rust). |
| Small mark | 128-400px | Shield with bands, rivets, and bent band detail. No text, no plank lines. Crack visible at 256px+. |
| Avatar | 256-512px | Shield with bands, rivets, bent band, plank lines, crack, and "BC" monogram between bands. |
| Full mark | 512px+ | Complete version: all structural detail plus "BUILD CHARACTER" text. |

### Monochrome/Single-color

All-charcoal or all-offwhite. Identical paths, single fill color. Iron bands become same color as outline (distinguished by fill vs. stroke). Production-validated for: embroidery, screen printing (1-color), laser etching, stamping/debossing.

## Deliverables

| File | Description |
|------|-------------|
| `logo-full-color.svg` | Full mark, color (rust bands, charcoal structure) |
| `logo-full-mono-charcoal.svg` | Full mark, all charcoal on transparent |
| `logo-full-mono-offwhite.svg` | Full mark, all offwhite on transparent |
| `logo-avatar-color.svg` | Avatar mark with BC monogram, color |
| `logo-avatar-mono-charcoal.svg` | Avatar mark, all charcoal |
| `logo-avatar-mono-offwhite.svg` | Avatar mark, all offwhite |
| `logo-icon-color.svg` | Small mark (no text/monogram), color |
| `logo-icon-mono-charcoal.svg` | Small mark, all charcoal |
| `logo-icon-mono-offwhite.svg` | Small mark, all offwhite |
| `favicon.svg` | Minimal shield + bars, single color |

All SVG. PNG rasterizations generated from SVG as needed (not separate source files).

## Placement

- **Site header:** `logo-full-color.svg`
- **Favicon:** `favicon.svg` (replaces `/site/public/favicon.svg`)
- **Printful store header:** `logo-full-color.svg`
- **Instagram avatar:** Rasterize `logo-avatar-color.svg` to 512x512 PNG
- **Telegram bot avatar:** Same rasterized avatar PNG
- **Merch brand tag:** `logo-icon-mono-charcoal.svg` or offwhite depending on garment
- **Sticker designs:** Icon or full mark as brand element

## Generation Method

SVG hand-coded. All visual effects achieved through path manipulation (irregular node placement, intentional geometric imperfection). No SVG filters, no gradients, no raster effects. This ensures:
- Crisp rendering at any size
- Full compatibility with print production methods
- Easy color swapping for mono variants
- Small file sizes

## Brand Constraints

- No Calvin and Hobbes references
- No motivational/inspirational imagery
- No hustle-culture aesthetics
- No heraldic grandeur or polish
- Tone: earned, unpretentious, functional, self-aware
- The imperfections (bent band, crack) are intentional brand signals, not bugs
