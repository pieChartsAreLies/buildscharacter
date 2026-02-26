# Build Character Logo Design

**Date:** 2026-02-26
**Status:** Approved

## Concept: The Ironbound Shield

A shield made of rough-hewn wooden planks, bound together by iron bands. Functional, not decorative. The kind of thing built to take hits and hold together. "BUILD CHARACTER" is stamped/branded into the wood.

**What it communicates:** This held together. It was built to take hits. Character is forged through resistance, not polish. Iron and wood, not chrome and glass.

**Brand alignment:** Dry, earned, unpretentious. Evokes endurance and hard materials without being preachy or motivational. The shield is a badge you've earned, not a trophy you've bought.

## Visual Specification

### Shape & Structure

- **Shield silhouette:** Pointed bottom, flat/slightly curved top. Traditional heater shield proportions (~5:6 width-to-height ratio).
- **Planks:** 3-4 vertical wooden planks with subtle wood grain lines running vertically.
- **Iron bands:** Two horizontal bands crossing the planks, one at upper third, one at lower third. Slight dimensional depth (hint of shadow/bevel, not flat).
- **Rivets:** Small circles at each band-plank intersection. 6-8 total.

### Typography

- "BUILD" above the upper iron band, "CHARACTER" below the lower iron band. Both curved slightly to follow the shield contour.
- **Typeface:** Space Grotesk Bold with subtle roughened/distressed treatment to look branded/stamped into wood.
- Text color: charcoal (#1a1a1a) or rust (#c45d3e) depending on background.

### Color Palette

| Element | Color | Hex |
|---------|-------|-----|
| Wood planks | Warm brown | #8B6F47 |
| Wood grain/shadow | Dark brown | #6B5234 |
| Iron bands | Dark charcoal | #1a1a1a to #2d2d2d |
| Iron highlights | Metallic edge | Upper-edge highlight |
| Rivets | Iron with highlight dot | Same as bands |
| Text (light bg) | Charcoal | #1a1a1a |
| Text (dark bg) | Offwhite | #f5f0eb |

### Responsive Versions

| Context | Size | Content |
|---------|------|---------|
| Favicon | 16-128px | Shield outline + two crossing horizontal bands only. No text, no grain, no rivets. Single color. |
| Social avatar | 256-512px | Full shield with bands and rivets, "BC" monogram between bands. |
| Full mark | 512px+ | Complete version with all detail and full "BUILD CHARACTER" text. |

### Monochrome/Single-color

For embroidery, stamps, dark merch: all-charcoal or all-offwhite. Wood grain becomes simple vertical lines. Iron bands become solid bars.

## Deliverables

1. **`logo-full.svg`** -- Complete ironbound shield with "BUILD CHARACTER" text
2. **`logo-icon.svg`** -- Shield with bands only, no text (favicon/small contexts)
3. **`logo-avatar.png`** -- 512x512, shield with "BC" monogram (social/messaging)
4. **`favicon.svg`** -- Simplified shield, replaces current site favicon
5. **Monochrome variants** -- Charcoal-on-transparent and offwhite-on-transparent for both full and icon

## Placement

- **Site header:** Full logo SVG
- **Favicon:** Icon SVG (replaces `/site/public/favicon.svg`)
- **Printful store:** Full logo as store header
- **Instagram avatar:** Social avatar PNG
- **Telegram bot avatar:** Social avatar PNG
- **Merch brand tag:** Monochrome icon
- **Sticker designs:** Full or icon mark as brand element

## Generation Method

SVG hand-coded (not AI image generation). Geometric enough to build directly in SVG for crisp, scalable vectors at every size without upscaling artifacts.

## Brand Constraints

- No Calvin and Hobbes references
- No motivational/inspirational imagery
- No hustle-culture aesthetics
- Tone: earned, unpretentious, functional
