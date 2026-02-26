# Build Character Logo Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create the ironbound shield logo as hand-coded SVGs and deploy across all brand touchpoints (favicon, site header, social avatars, Printful merch, monochrome variants).

**Architecture:** Hand-coded SVG files with a vision feedback loop for quality assurance. All variants derive from a "golden master" full-mark SVG. Text is converted to paths before generating variants. Brand colors only (charcoal #1a1a1a, rust #c45d3e, offwhite #f5f0eb). PNG rasterization via sharp (Node.js). Visual verification via Playwright screenshots evaluated with Claude Vision.

**Tech Stack:** SVG (hand-coded), Node.js (sharp for rasterization, text-to-svg for font conversion, svgo for optimization), Playwright (screenshots for vision feedback), Astro (site integration)

**Environment:** Node v22.17.1, Playwright 1.58.2 available. No ImageMagick/rsvg-convert/Inkscape. Space Grotesk loaded from Google Fonts (no local .ttf).

---

### Task 0: Set up tooling

**Files:**
- Create: `brand/tools/package.json`
- Create: `brand/tools/screenshot.mjs`
- Create: `brand/tools/rasterize.mjs`

**Step 1: Initialize Node tooling in brand/tools/**

```bash
mkdir -p /Users/llama/Development/builds-character/brand/tools
cd /Users/llama/Development/builds-character/brand/tools
npm init -y
npm install sharp svgo text-to-svg
```

**Step 2: Create screenshot utility**

Create `brand/tools/screenshot.mjs` -- a Playwright script that renders an SVG file to a PNG screenshot at a given size. This is the core of the vision feedback loop.

```javascript
// Usage: node screenshot.mjs <svg-path> <width> <output-png>
import { chromium } from 'playwright';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const [svgPath, width, outputPath] = process.argv.slice(2);
const svgContent = readFileSync(resolve(svgPath), 'utf-8');
const w = parseInt(width) || 512;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: w, height: w } });
await page.setContent(`
  <html>
    <head>
      <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
      <style>
        body { margin: 0; display: flex; justify-content: center; align-items: center;
               min-height: 100vh; background: white; }
        img { max-width: 90%; max-height: 90%; }
      </style>
    </head>
    <body>
      <img src="data:image/svg+xml;base64,${Buffer.from(svgContent).toString('base64')}" />
    </body>
  </html>
`);
await page.waitForTimeout(1000); // wait for font load
await page.screenshot({ path: resolve(outputPath || 'screenshot.png') });
await browser.close();
```

**Step 3: Create rasterize utility**

Create `brand/tools/rasterize.mjs` -- uses sharp to convert SVG to high-res PNG (for Printful and social).

```javascript
// Usage: node rasterize.mjs <svg-path> <width> <height> <output-png>
import sharp from 'sharp';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const [svgPath, w, h, outputPath] = process.argv.slice(2);
const svgBuffer = readFileSync(resolve(svgPath));
await sharp(svgBuffer)
  .resize(parseInt(w), parseInt(h), { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
  .png()
  .toFile(resolve(outputPath));
console.log(`Rasterized ${svgPath} -> ${outputPath} (${w}x${h})`);
```

**Step 4: Verify tools work**

```bash
cd /Users/llama/Development/builds-character/brand/tools
node -e "import('sharp').then(s => console.log('sharp OK'))"
node -e "import('svgo').then(s => console.log('svgo OK'))"
```

**Step 5: Commit**

```bash
git add brand/tools/
git commit -m "chore: add Node tooling for logo rasterization and screenshots"
```

---

### Task 1: Create the full-mark logo SVG (golden master)

**Files:**
- Create: `brand/logo-full-color.svg`

**Step 1: Create initial SVG with all elements**

Create `brand/logo-full-color.svg` with viewBox `0 0 200 240`. This is the "golden master" from which all other variants are derived. All text starts as `<text>` elements for rapid iteration; Task 3 converts to paths.

Build these elements:
- **Shield outline:** Heater shield, flat top, pointed bottom. Path nodes offset 1-2px from mathematical perfection for hand-cut feel. ~5:6 width-to-height ratio.
- **Plank lines:** 3 vertical lines inside the shield with slight wave (cubic bezier, 2-3px deviation).
- **Crack:** Short path (~15-20px) branching off middle plank at ~45 degrees. Same stroke weight as plank lines.
- **Upper iron band:** Solid filled rectangle, rust color.
- **Lower iron band:** Path with a bend/kink at one point (single node offset ~3px downward). Rust color.
- **Rivets:** 6 filled circles (~3px radius) at band-plank intersections. Rust fill, charcoal stroke.
- **Text:** "BUILD" centered above upper band, "CHARACTER" centered below lower band. Space Grotesk Bold, slight letter-spacing.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 240" fill="none">
  <path d="M10 8 L190 10 L192 140 L102 232 L8 138 Z"
        stroke="#1a1a1a" stroke-width="4" fill="none" stroke-linejoin="round"/>
  <path d="M58 10 C59 50, 57 100, 58 138" stroke="#1a1a1a" stroke-width="1.5"/>
  <path d="M102 10 C101 60, 103 110, 102 170" stroke="#1a1a1a" stroke-width="1.5"/>
  <path d="M144 10 C143 50, 145 100, 144 138" stroke="#1a1a1a" stroke-width="1.5"/>
  <path d="M102 95 L115 82" stroke="#1a1a1a" stroke-width="1.2" stroke-linecap="round"/>
  <rect x="14" y="60" width="172" height="12" rx="1" fill="#c45d3e"/>
  <path d="M14 150 L80 150 L85 153 L90 150 L172 150 L172 162 L90 162 L85 165 L80 162 L14 162 Z" fill="#c45d3e"/>
  <circle cx="58" cy="66" r="3" fill="#c45d3e" stroke="#1a1a1a" stroke-width="1"/>
  <circle cx="102" cy="66" r="3" fill="#c45d3e" stroke="#1a1a1a" stroke-width="1"/>
  <circle cx="144" cy="66" r="3" fill="#c45d3e" stroke="#1a1a1a" stroke-width="1"/>
  <circle cx="58" cy="156" r="3" fill="#c45d3e" stroke="#1a1a1a" stroke-width="1"/>
  <circle cx="102" cy="156" r="3" fill="#c45d3e" stroke="#1a1a1a" stroke-width="1"/>
  <circle cx="144" cy="156" r="3" fill="#c45d3e" stroke="#1a1a1a" stroke-width="1"/>
  <text x="100" y="52" text-anchor="middle" font-family="Space Grotesk" font-weight="700"
        font-size="22" fill="#1a1a1a" letter-spacing="3">BUILD</text>
  <text x="100" y="190" text-anchor="middle" font-family="Space Grotesk" font-weight="700"
        font-size="18" fill="#1a1a1a" letter-spacing="2">CHARACTER</text>
</svg>
```

**Step 2: Vision feedback loop (max 3 iterations)**

Screenshot the SVG at 512px:

```bash
cd /Users/llama/Development/builds-character
node brand/tools/screenshot.mjs brand/logo-full-color.svg 512 brand/tools/review-full.png
```

Read the screenshot with the Read tool and evaluate against these criteria:
1. Shield shape is clearly a shield (flat top, pointed bottom)
2. Iron bands are visually distinct horizontal bars
3. Lower band has a visible but not cartoonish kink
4. Rivets are visible at intersections
5. Plank lines create subtle vertical divisions
6. Crack is visible but subtle
7. "BUILD" and "CHARACTER" text is readable and properly centered
8. Overall: looks brutalist and functional, not corporate

If any criterion fails, adjust SVG coordinates and re-screenshot. **Maximum 3 iterations.** After 3 cycles, accept the current state and note any remaining issues for manual follow-up.

**Exit criteria:** All 8 points above are "good enough" (clearly recognizable even if not perfect), OR 3 iterations exhausted.

**Step 3: Commit**

```bash
git add brand/logo-full-color.svg
git commit -m "feat: add full-mark color logo (ironbound shield)"
```

---

### Task 2: Create icon and favicon SVGs

**Files:**
- Create: `brand/logo-icon-color.svg`
- Create: `brand/logo-avatar-color.svg`
- Create: `brand/favicon.svg`
- Modify: `site/public/favicon.svg`

**Step 1: Create icon (small mark)**

Copy shield structure from golden master. **Remove:** text, plank division lines. **Keep:** shield outline, both iron bands (with kink), rivets.

**Step 2: Create avatar (BC monogram)**

Start from icon mark. Add "BC" text centered between the two iron bands. Try side-by-side layout first (more readable than stacked). Space Grotesk Bold, font-size ~40, letter-spacing 1.

```svg
<text x="100" y="110" text-anchor="middle" dominant-baseline="central"
      font-family="Space Grotesk" font-weight="700" font-size="40"
      fill="#1a1a1a" letter-spacing="1">BC</text>
```

**Step 3: Create favicon**

Maximum simplification for 16-128px. Filled charcoal shield shape + two horizontal rust bars. Include dark-mode variant:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">
  <style>
    .shield { fill: #1a1a1a; }
    .band { fill: #c45d3e; }
    @media (prefers-color-scheme: dark) {
      .shield { fill: #f5f0eb; }
    }
  </style>
  <path class="shield" d="M8 6 L120 8 L122 88 L66 122 L6 86 Z"/>
  <rect class="band" x="18" y="32" width="92" height="8"/>
  <rect class="band" x="18" y="64" width="82" height="8"/>
</svg>
```

Copy to `site/public/favicon.svg`.

**Step 4: Vision feedback (max 2 iterations per variant)**

Screenshot each at its target size and evaluate:
- Icon at 256px: bands and rivets distinct, shield recognizable
- Avatar at 512px: "BC" readable, integrated with shield
- Favicon at 64px: shield shape + bars distinguishable

```bash
node brand/tools/screenshot.mjs brand/logo-icon-color.svg 256 brand/tools/review-icon.png
node brand/tools/screenshot.mjs brand/logo-avatar-color.svg 512 brand/tools/review-avatar.png
node brand/tools/screenshot.mjs brand/favicon.svg 64 brand/tools/review-favicon.png
```

**Step 5: Commit**

```bash
git add brand/logo-icon-color.svg brand/logo-avatar-color.svg brand/favicon.svg site/public/favicon.svg
git commit -m "feat: add icon, avatar, and favicon logo variants"
```

---

### Task 3: Convert text to paths in golden master

**Files:**
- Modify: `brand/logo-full-color.svg`
- Modify: `brand/logo-avatar-color.svg`
- Create: `brand/tools/text-to-path.mjs`

**Step 1: Download Space Grotesk Bold font**

```bash
cd /Users/llama/Development/builds-character/brand/tools
curl -L "https://fonts.google.com/download?family=Space+Grotesk" -o space-grotesk.zip
unzip -o space-grotesk.zip -d fonts/
ls fonts/  # Find the Bold .ttf file
```

**Step 2: Create text-to-path conversion script**

Create `brand/tools/text-to-path.mjs`:

```javascript
// Usage: node text-to-path.mjs <font.ttf> <text> <font-size> <x> <y>
import TextToSVG from 'text-to-svg';

const [fontPath, text, fontSize, x, y] = process.argv.slice(2);
const textToSVG = TextToSVG.loadSync(fontPath);
const d = textToSVG.getD(text, {
  x: parseFloat(x), y: parseFloat(y),
  fontSize: parseFloat(fontSize),
  anchor: 'center middle',
  letterSpacing: 0.15  // em units
});
console.log(d);
```

**Step 3: Generate path data for "BUILD" and "CHARACTER"**

```bash
node brand/tools/text-to-path.mjs brand/tools/fonts/SpaceGrotesk-Bold.ttf "BUILD" 22 100 52
node brand/tools/text-to-path.mjs brand/tools/fonts/SpaceGrotesk-Bold.ttf "CHARACTER" 18 100 190
node brand/tools/text-to-path.mjs brand/tools/fonts/SpaceGrotesk-Bold.ttf "BC" 40 100 110
```

**Step 4: Apply roughening**

For each generated path, apply controlled distortion: shift outer control points by max +/- 1.5 units on X/Y axes. This can be done by a small script or manual edit of the path `d` attribute. Do NOT randomize; apply consistent directional shifts that create a "stamped" feel.

**Step 5: Replace `<text>` elements in golden master and avatar**

In `brand/logo-full-color.svg`, replace the two `<text>` elements with `<path>` elements using the generated (and roughened) `d` attributes.

In `brand/logo-avatar-color.svg`, replace the `<text>` element with the "BC" path.

**Step 6: Vision verify (max 2 iterations)**

```bash
node brand/tools/screenshot.mjs brand/logo-full-color.svg 512 brand/tools/review-paths.png
```

Read screenshot. Text should be readable and look like it was stamped/branded into the surface. If letters are illegible or self-intersecting, reduce distortion magnitude and retry.

**Step 7: Commit**

```bash
git add brand/logo-full-color.svg brand/logo-avatar-color.svg brand/tools/
git commit -m "feat: convert logo text to vector paths with roughening"
```

---

### Task 4: Generate all monochrome variants

**Files:**
- Create: `brand/logo-full-mono-charcoal.svg`
- Create: `brand/logo-full-mono-offwhite.svg`
- Create: `brand/logo-icon-mono-charcoal.svg`
- Create: `brand/logo-icon-mono-offwhite.svg`
- Create: `brand/logo-avatar-mono-charcoal.svg`
- Create: `brand/logo-avatar-mono-offwhite.svg`

**Step 1: Create mono variants via color replacement**

For each source SVG (full, icon, avatar):
- **Charcoal mono:** Replace all `fill="#c45d3e"` with `fill="#1a1a1a"`, all `stroke="#c45d3e"` with `stroke="#1a1a1a"`. Single-color charcoal on transparent.
- **Offwhite mono:** Replace all color values with `#f5f0eb`. Single-color offwhite on transparent.

This is straightforward string replacement since text is already converted to paths (Task 3).

**Step 2: Verify one representative variant**

```bash
node brand/tools/screenshot.mjs brand/logo-full-mono-charcoal.svg 512 brand/tools/review-mono.png
```

Confirm: single color, bands distinguished by fill vs. stroke, text readable.

**Step 3: Commit**

```bash
git add brand/logo-*-mono-*.svg
git commit -m "feat: add monochrome logo variants (charcoal + offwhite)"
```

---

### Task 5: Integrate logo into site header

**Files:**
- Create: `site/src/components/BrandIcon.astro`
- Modify: `site/src/layouts/Base.astro:64-66`
- Copy: `brand/logo-icon-color.svg` to `site/public/logo-icon-color.svg`

**Step 1: Create BrandIcon Astro component**

Create `site/src/components/BrandIcon.astro` that inlines the icon SVG for CSS control:

```astro
---
const { class: className = '' } = Astro.props;
---
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 240" fill="none"
     class:list={[className]} aria-hidden="true">
  <!-- Paste icon SVG contents here (shield + bands + rivets, no text) -->
  <!-- Use currentColor for charcoal elements so CSS can control them -->
</svg>
```

Use `currentColor` for the shield outline/structure so it responds to text color changes (hover, dark mode).

**Step 2: Update site header**

In `site/src/layouts/Base.astro`, replace lines 64-66:

```astro
<!-- FROM -->
<a href="/" class="font-display font-bold text-xl tracking-tight hover:text-rust transition-colors">
  BuildsCharacter
</a>

<!-- TO -->
<a href="/" class="flex items-center gap-2 hover:text-rust transition-colors group">
  <BrandIcon class="h-8 w-auto" />
  <span class="font-display font-bold text-xl tracking-tight">Build Character</span>
</a>
```

Add import at top of frontmatter:
```astro
import BrandIcon from '../components/BrandIcon.astro';
```

Note: This intentionally changes "BuildsCharacter" to "Build Character" (the rebranded name, per decision on 2026-02-25).

**Step 3: Add accessibility**

Ensure the `<a>` has proper accessible text. The `<span>` text "Build Character" serves as the accessible name. The SVG has `aria-hidden="true"` to avoid duplicate announcements.

**Step 4: Also copy static icon SVG to public/ for non-Astro uses**

```bash
cp brand/logo-icon-color.svg site/public/logo-icon-color.svg
```

**Step 5: Commit**

```bash
git add site/src/components/BrandIcon.astro site/src/layouts/Base.astro site/public/logo-icon-color.svg
git commit -m "feat: add logo icon to site header with accessible markup"
```

---

### Task 6: Generate PNG exports (social + Printful)

**Files:**
- Create: `brand/exports/logo-avatar-512.png`
- Create: `brand/exports/logo-avatar-256.png`
- Create: `brand/exports/logo-full-1024.png`
- Create: `brand/exports/logo-full-4500.png` (Printful)
- Create: `brand/exports/logo-icon-mono-charcoal-4500.png` (Printful merch tag)
- Create: `brand/exports/logo-icon-mono-offwhite-4500.png` (Printful merch tag, dark garments)

**Step 1: Create exports directory**

```bash
mkdir -p /Users/llama/Development/builds-character/brand/exports
```

**Step 2: Rasterize social sizes**

```bash
cd /Users/llama/Development/builds-character
node brand/tools/rasterize.mjs brand/logo-avatar-color.svg 512 512 brand/exports/logo-avatar-512.png
node brand/tools/rasterize.mjs brand/logo-avatar-color.svg 256 256 brand/exports/logo-avatar-256.png
node brand/tools/rasterize.mjs brand/logo-full-color.svg 1024 1228 brand/exports/logo-full-1024.png
```

Note: Full mark height is 1228 to maintain 200:240 aspect ratio at 1024px width.

**Step 3: Rasterize Printful sizes**

Printful requires 4500x5400px minimum for apparel at 300 DPI. Generate high-res versions:

```bash
node brand/tools/rasterize.mjs brand/logo-full-color.svg 4500 5400 brand/exports/logo-full-4500.png
node brand/tools/rasterize.mjs brand/logo-icon-mono-charcoal.svg 4500 5400 brand/exports/logo-icon-mono-charcoal-4500.png
node brand/tools/rasterize.mjs brand/logo-icon-mono-offwhite.svg 4500 5400 brand/exports/logo-icon-mono-offwhite-4500.png
```

**Step 4: Verify PNG quality**

Read one export with the Read tool to verify: correct colors, transparent background, no artifacts, correct dimensions.

```bash
node -e "import('sharp').then(async s => { const m = await s.default('brand/exports/logo-full-4500.png').metadata(); console.log(m.width, m.height, m.format, m.hasAlpha); })"
```

Expected: `4500 5400 png true`

**Step 5: Add exports to .gitignore or commit**

Large PNGs (4500px) should be committed since they're brand assets needed for Printful. However, if the repo prefers to regenerate them, add a `brand/exports/Makefile` or npm script instead.

```bash
git add brand/exports/
git commit -m "feat: add PNG exports for social platforms and Printful merch"
```

---

### Task 7: SVGO optimization

**Files:**
- Modify: all `brand/*.svg` files

**Step 1: Run SVGO on all SVG files**

```bash
cd /Users/llama/Development/builds-character
npx svgo brand/logo-*.svg brand/favicon.svg --config='{"plugins":[{"name":"preset-default","params":{"overrides":{"removeViewBox":false,"cleanupIds":false}}}]}'
```

This cleans up: excessive decimal precision, unnecessary groups, redundant attributes. Preserves viewBox and IDs.

**Step 2: Verify SVGs still render correctly**

```bash
node brand/tools/screenshot.mjs brand/logo-full-color.svg 512 brand/tools/review-optimized.png
```

Read screenshot and verify nothing broke.

**Step 3: Commit**

```bash
git add brand/*.svg
git commit -m "chore: optimize SVG files with SVGO"
```

---

### Task 8: Final visual review

**Files:**
- Review: all `brand/*.svg` and `brand/exports/*.png`
- Modify: any files needing final adjustments

**Step 1: Generate review screenshots of all variants**

```bash
cd /Users/llama/Development/builds-character
node brand/tools/screenshot.mjs brand/logo-full-color.svg 512 brand/tools/review-final-full.png
node brand/tools/screenshot.mjs brand/logo-icon-color.svg 256 brand/tools/review-final-icon.png
node brand/tools/screenshot.mjs brand/logo-avatar-color.svg 512 brand/tools/review-final-avatar.png
node brand/tools/screenshot.mjs brand/favicon.svg 64 brand/tools/review-final-favicon.png
node brand/tools/screenshot.mjs brand/logo-full-mono-charcoal.svg 512 brand/tools/review-final-mono.png
```

**Step 2: Visual audit checklist**

Read each screenshot and verify against the design doc (`docs/plans/2026-02-26-logo-design.md`):

- [ ] Shield shape: irregular edges, not mathematically perfect
- [ ] Iron bands: rust colored, lower band has visible kink
- [ ] Rivets: 6 total, at band-plank intersections
- [ ] Crack: branches off middle plank, subtle
- [ ] Text (full mark): "BUILD" above upper band, "CHARACTER" below lower band
- [ ] Monogram (avatar): "BC" centered between bands, readable
- [ ] Favicon: recognizable at 64px (shield + bars distinguishable)
- [ ] Monochrome: single color, bands distinguished by fill vs. stroke
- [ ] Colors: only charcoal #1a1a1a, rust #c45d3e, offwhite #f5f0eb used

**Step 3: Fix any issues**

Address each failed check. Max 2 additional iterations. Re-screenshot and re-verify.

**Step 4: Clean up review screenshots**

```bash
rm brand/tools/review-*.png
```

**Step 5: Final commit**

```bash
git add brand/ site/
git commit -m "chore: final logo review and adjustments"
```

---

## Task Dependency Order

```
Task 0 (tooling) -> Task 1 (golden master) -> Task 3 (text to paths)
                    Task 2 (icon/avatar/favicon) -> Task 3 (avatar text to paths)
Task 3 -> Task 4 (mono variants)
Task 2 -> Task 5 (site header)
Task 3 + Task 4 -> Task 6 (PNG exports)
Task 6 -> Task 7 (SVGO)
Task 7 -> Task 8 (final review)
```

## File Summary

| File | Task | Description |
|------|------|-------------|
| `brand/tools/package.json` | 0 | Node tooling dependencies |
| `brand/tools/screenshot.mjs` | 0 | Playwright SVG screenshot utility |
| `brand/tools/rasterize.mjs` | 0 | sharp SVG-to-PNG rasterizer |
| `brand/tools/text-to-path.mjs` | 3 | Font text to SVG path converter |
| `brand/logo-full-color.svg` | 1 | Golden master, full mark with text paths |
| `brand/logo-icon-color.svg` | 2 | Icon mark (no text), color |
| `brand/logo-avatar-color.svg` | 2 | Avatar with BC monogram paths, color |
| `brand/favicon.svg` | 2 | Minimal favicon shield + dark mode |
| `site/public/favicon.svg` | 2 | Deployed favicon (copy) |
| `brand/logo-full-mono-charcoal.svg` | 4 | Full mark, charcoal mono |
| `brand/logo-full-mono-offwhite.svg` | 4 | Full mark, offwhite mono |
| `brand/logo-icon-mono-charcoal.svg` | 4 | Icon, charcoal mono |
| `brand/logo-icon-mono-offwhite.svg` | 4 | Icon, offwhite mono |
| `brand/logo-avatar-mono-charcoal.svg` | 4 | Avatar, charcoal mono |
| `brand/logo-avatar-mono-offwhite.svg` | 4 | Avatar, offwhite mono |
| `site/src/components/BrandIcon.astro` | 5 | Inline SVG component for header |
| `site/src/layouts/Base.astro` | 5 | Header updated with logo + a11y |
| `site/public/logo-icon-color.svg` | 5 | Static icon copy for non-Astro use |
| `brand/exports/logo-avatar-512.png` | 6 | Social avatar PNG |
| `brand/exports/logo-avatar-256.png` | 6 | Social avatar PNG (small) |
| `brand/exports/logo-full-1024.png` | 6 | Full mark PNG |
| `brand/exports/logo-full-4500.png` | 6 | Printful-ready full mark (4500x5400) |
| `brand/exports/logo-icon-mono-charcoal-4500.png` | 6 | Printful merch tag (light garments) |
| `brand/exports/logo-icon-mono-offwhite-4500.png` | 6 | Printful merch tag (dark garments) |
