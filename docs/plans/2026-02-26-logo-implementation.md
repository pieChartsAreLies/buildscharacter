# Build Character Logo Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create the ironbound shield logo as hand-coded SVGs and deploy across all brand touchpoints (favicon, site header, social avatar, merch-ready monochrome variants).

**Architecture:** Hand-coded SVG files using only path manipulation for the brutalist aesthetic. All variants share the same base paths, with progressive detail removal for smaller sizes. Brand colors only (charcoal #1a1a1a, rust #c45d3e, offwhite #f5f0eb). No build tooling needed; SVGs are static assets.

**Tech Stack:** SVG (hand-coded), Astro (site integration), ImageMagick or librsvg (PNG rasterization for social avatars)

---

### Task 1: Create the full-mark logo SVG

**Files:**
- Create: `brand/logo-full-color.svg`

**Step 1: Create the SVG file with shield outline**

Create `brand/logo-full-color.svg` with viewBox `0 0 200 240`. Build the shield path as a heater shield silhouette (flat top, pointed bottom) with intentionally slightly irregular edges (nodes offset 1-2px from mathematical perfection).

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 240" fill="none">
  <!-- Shield outline - slightly irregular edges for hand-cut feel -->
  <path d="M10 8 L190 10 L192 140 L102 232 L8 138 Z"
        stroke="#1a1a1a" stroke-width="4" fill="none" stroke-linejoin="round"/>

  <!-- 3 vertical plank division lines with subtle wave -->
  <path d="M58 10 C59 50, 57 100, 58 138" stroke="#1a1a1a" stroke-width="1.5"/>
  <path d="M102 10 C101 60, 103 110, 102 170" stroke="#1a1a1a" stroke-width="1.5"/>
  <path d="M144 10 C143 50, 145 100, 144 138" stroke="#1a1a1a" stroke-width="1.5"/>

  <!-- Crack branching off middle plank at ~45 degrees -->
  <path d="M102 95 L115 82" stroke="#1a1a1a" stroke-width="1.2" stroke-linecap="round"/>

  <!-- Upper iron band - solid rectangle -->
  <rect x="14" y="60" width="172" height="12" rx="1" fill="#c45d3e"/>

  <!-- Lower iron band - with bent kink showing impact -->
  <path d="M14 150 L80 150 L85 153 L90 150 L172 150 L172 162 L90 162 L85 165 L80 162 L14 162 Z"
        fill="#c45d3e"/>

  <!-- Rivets - 6 filled circles at band-plank intersections -->
  <!-- Upper band rivets -->
  <circle cx="58" cy="66" r="3" fill="#c45d3e" stroke="#1a1a1a" stroke-width="1"/>
  <circle cx="102" cy="66" r="3" fill="#c45d3e" stroke="#1a1a1a" stroke-width="1"/>
  <circle cx="144" cy="66" r="3" fill="#c45d3e" stroke="#1a1a1a" stroke-width="1"/>
  <!-- Lower band rivets -->
  <circle cx="58" cy="156" r="3" fill="#c45d3e" stroke="#1a1a1a" stroke-width="1"/>
  <circle cx="102" cy="156" r="3" fill="#c45d3e" stroke="#1a1a1a" stroke-width="1"/>
  <circle cx="144" cy="156" r="3" fill="#c45d3e" stroke="#1a1a1a" stroke-width="1"/>

  <!-- "BUILD" text above upper band, slight arc -->
  <!-- Convert Space Grotesk Bold to paths. These are placeholder paths;
       actual letter paths must be traced from the font at implementation time. -->
  <text x="100" y="52" text-anchor="middle"
        font-family="Space Grotesk" font-weight="700" font-size="22"
        fill="#1a1a1a" letter-spacing="3">BUILD</text>

  <!-- "CHARACTER" text below lower band -->
  <text x="100" y="190" text-anchor="middle"
        font-family="Space Grotesk" font-weight="700" font-size="18"
        fill="#1a1a1a" letter-spacing="2">CHARACTER</text>
</svg>
```

Note: The text elements use live `<text>` initially for rapid iteration. Task 7 converts all text to `<path>` elements with manual roughening for the final production version.

**Step 2: Open in browser to visually verify**

Run: `open brand/logo-full-color.svg`

Verify: Shield shape is visible, planks divide it into sections, iron bands cross horizontally (lower one has visible kink), rivets sit at intersections, crack branches off middle plank, text reads "BUILD" and "CHARACTER". Overall impression should be brutalist and functional, not polished.

**Step 3: Iterate on proportions**

Adjust node positions, band widths, plank spacing, text size/position until the mark looks balanced and intentional. The shield edges should feel hand-drawn but deliberate. Key things to check:
- Shield outline isn't mathematically perfect (nodes slightly offset)
- Iron bands feel like solid bars, not decorative stripes
- Lower band kink is noticeable but not cartoonish (~3px offset)
- Crack is subtle, not dramatic (~15-20px long)
- Text is readable and properly centered
- Overall: looks like something stenciled on gear, not a corporate crest

**Step 4: Commit**

```bash
git add brand/logo-full-color.svg
git commit -m "feat: add full-mark color logo (ironbound shield)"
```

---

### Task 2: Create the icon (small mark) SVG

**Files:**
- Create: `brand/logo-icon-color.svg`

**Step 1: Create simplified version**

Copy the shield structure from Task 1 but remove: text, plank division lines. Keep: shield outline, both iron bands (with kink), rivets, crack (optional, include if readable at 256px).

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 240" fill="none">
  <!-- Shield outline -->
  <path d="M10 8 L190 10 L192 140 L102 232 L8 138 Z"
        stroke="#1a1a1a" stroke-width="4" fill="none" stroke-linejoin="round"/>

  <!-- Upper iron band -->
  <rect x="14" y="60" width="172" height="12" rx="1" fill="#c45d3e"/>

  <!-- Lower iron band with kink -->
  <path d="M14 150 L80 150 L85 153 L90 150 L172 150 L172 162 L90 162 L85 165 L80 162 L14 162 Z"
        fill="#c45d3e"/>

  <!-- Rivets -->
  <circle cx="58" cy="66" r="3" fill="#c45d3e" stroke="#1a1a1a" stroke-width="1"/>
  <circle cx="102" cy="66" r="3" fill="#c45d3e" stroke="#1a1a1a" stroke-width="1"/>
  <circle cx="144" cy="66" r="3" fill="#c45d3e" stroke="#1a1a1a" stroke-width="1"/>
  <circle cx="58" cy="156" r="3" fill="#c45d3e" stroke="#1a1a1a" stroke-width="1"/>
  <circle cx="102" cy="156" r="3" fill="#c45d3e" stroke="#1a1a1a" stroke-width="1"/>
  <circle cx="144" cy="156" r="3" fill="#c45d3e" stroke="#1a1a1a" stroke-width="1"/>
</svg>
```

**Step 2: Verify at target sizes**

Open in browser and resize window to check readability at ~128px, ~256px, ~400px. The bands and rivets should remain distinct. Shield shape should be immediately recognizable.

**Step 3: Commit**

```bash
git add brand/logo-icon-color.svg
git commit -m "feat: add icon-mark color logo (no text)"
```

---

### Task 3: Create the avatar (BC monogram) SVG

**Files:**
- Create: `brand/logo-avatar-color.svg`

**Step 1: Create avatar version**

Start from the icon mark (Task 2). Add a "BC" monogram centered between the two iron bands. Letters are stacked vertically: "B" above "C", Space Grotesk Bold. Fill ~60% of the vertical space between bands.

```svg
<!-- Add between the iron bands, centered -->
<text x="100" y="100" text-anchor="middle" dominant-baseline="central"
      font-family="Space Grotesk" font-weight="700" font-size="40"
      fill="#1a1a1a" letter-spacing="1">BC</text>
```

Note: The monogram may work better as side-by-side "BC" rather than stacked, depending on the vertical space between bands. Try both layouts and pick whichever reads cleaner. The design doc specified stacked, but side-by-side may be more readable in practice.

**Step 2: Verify at 256px and 512px**

Run: `open brand/logo-avatar-color.svg`

The "BC" should be immediately readable. The monogram should feel integrated with the shield, not floating on top. Rivets and plank details (if included) shouldn't compete with the letters.

**Step 3: Commit**

```bash
git add brand/logo-avatar-color.svg
git commit -m "feat: add avatar-mark color logo (BC monogram)"
```

---

### Task 4: Create the favicon SVG

**Files:**
- Create: `brand/favicon.svg`
- Modify: `site/public/favicon.svg` (replace contents)

**Step 1: Create minimal favicon**

Maximum simplification: shield outline filled with charcoal, two horizontal bars inset from edges in rust (or offwhite). No rivets, no text, no plank lines, no crack. Must be recognizable at 16px.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" fill="none">
  <!-- Filled shield shape -->
  <path d="M8 6 L120 8 L122 88 L66 122 L6 86 Z" fill="#1a1a1a"/>

  <!-- Two horizontal bars (iron bands, simplified) -->
  <rect x="18" y="32" width="92" height="8" fill="#c45d3e"/>
  <rect x="18" y="64" width="82" height="8" fill="#c45d3e"/>
</svg>
```

Also include a dark-mode variant using `prefers-color-scheme`:

```svg
<style>
  .shield { fill: #1a1a1a; }
  .band { fill: #c45d3e; }
  @media (prefers-color-scheme: dark) {
    .shield { fill: #f5f0eb; }
  }
</style>
```

**Step 2: Test at actual favicon size**

Copy to `site/public/favicon.svg` and run the Astro dev server to check the browser tab. The shield shape and two bars should be distinguishable.

Run: `cd /Users/llama/Development/builds-character/site && npx astro dev`

Check: Browser tab shows the shield favicon, not the old Astro rocket.

**Step 3: Commit**

```bash
git add brand/favicon.svg site/public/favicon.svg
git commit -m "feat: replace default favicon with brand shield"
```

---

### Task 5: Create monochrome variants

**Files:**
- Create: `brand/logo-full-mono-charcoal.svg`
- Create: `brand/logo-full-mono-offwhite.svg`
- Create: `brand/logo-icon-mono-charcoal.svg`
- Create: `brand/logo-icon-mono-offwhite.svg`
- Create: `brand/logo-avatar-mono-charcoal.svg`
- Create: `brand/logo-avatar-mono-offwhite.svg`

**Step 1: Create charcoal monochrome full mark**

Copy `logo-full-color.svg`. Replace all `fill="#c45d3e"` with `fill="#1a1a1a"`. Replace all `stroke="#c45d3e"` similarly. The iron bands are now distinguished from the outline by being filled shapes vs. stroked paths.

**Step 2: Create offwhite monochrome full mark**

Same as above but all colors become `#f5f0eb`. This is for use on dark backgrounds.

**Step 3: Repeat for icon and avatar variants**

Same color-swap process for the icon and avatar SVGs.

**Step 4: Commit**

```bash
git add brand/logo-*-mono-*.svg
git commit -m "feat: add monochrome logo variants (charcoal + offwhite)"
```

---

### Task 6: Integrate logo into site header

**Files:**
- Modify: `site/src/layouts/Base.astro:64-66` (replace text logo with SVG)

**Step 1: Replace text-only header with logo + text**

In `site/src/layouts/Base.astro`, replace the current text-only brand link (line 64-66):

```astro
<!-- Current -->
<a href="/" class="font-display font-bold text-xl tracking-tight hover:text-rust transition-colors">
  BuildsCharacter
</a>
```

With an inline SVG icon + text combination:

```astro
<a href="/" class="flex items-center gap-2 hover:text-rust transition-colors group">
  <img src="/logo-icon-color.svg" alt="" class="h-8 w-auto" />
  <span class="font-display font-bold text-xl tracking-tight">Build Character</span>
</a>
```

This requires copying `brand/logo-icon-color.svg` to `site/public/logo-icon-color.svg`.

**Step 2: Test the site header**

Run: `cd /Users/llama/Development/builds-character/site && npx astro dev`

Verify: Logo icon appears to the left of "Build Character" text in the nav bar. Hover transitions work. Logo is ~32px tall and crisp.

**Step 3: Commit**

```bash
git add site/public/logo-icon-color.svg site/src/layouts/Base.astro
git commit -m "feat: add logo icon to site header navigation"
```

---

### Task 7: Convert text to paths (production hardening)

**Files:**
- Modify: `brand/logo-full-color.svg`
- Modify: `brand/logo-avatar-color.svg`
- Modify: all mono variants that contain text

**Step 1: Convert `<text>` elements to `<path>` elements**

Use a font-to-SVG-path tool or manually trace the Space Grotesk Bold letterforms. For each character, convert to path data and then manually offset 4-5 nodes by 0.5-1px to create the stamped/branded look.

This can be done by:
1. Opening each SVG in a vector editor (Inkscape, or programmatically)
2. Converting text to paths (`Object > Object to Path` in Inkscape)
3. Manually shifting a few nodes per letter for the rough feel
4. Replacing the `<text>` elements with the resulting `<path>` elements

If no vector editor is available, the `<text>` elements with `font-family="Space Grotesk"` are acceptable for web use (font is loaded by the site). The path conversion is primarily needed for standalone/merch use where the font may not be available.

**Step 2: Verify text renders identically**

Open each modified SVG in browser. Text should look the same as before but with a subtle hand-stamped quality (slightly irregular edges visible at zoom).

**Step 3: Update monochrome variants**

Copy the path-converted text elements into each monochrome variant, adjusting fill colors.

**Step 4: Commit**

```bash
git add brand/*.svg
git commit -m "feat: convert logo text to paths for production use"
```

---

### Task 8: Generate PNG rasterizations for social platforms

**Files:**
- Create: `brand/exports/logo-avatar-512.png`
- Create: `brand/exports/logo-avatar-256.png`
- Create: `brand/exports/logo-full-1024.png`

**Step 1: Create exports directory**

```bash
mkdir -p /Users/llama/Development/builds-character/brand/exports
```

**Step 2: Rasterize SVGs to PNG**

Using `rsvg-convert` (from librsvg) or ImageMagick:

```bash
# Install if needed: brew install librsvg
rsvg-convert -w 512 -h 512 brand/logo-avatar-color.svg > brand/exports/logo-avatar-512.png
rsvg-convert -w 256 -h 256 brand/logo-avatar-color.svg > brand/exports/logo-avatar-256.png
rsvg-convert -w 1024 brand/logo-full-color.svg > brand/exports/logo-full-1024.png
```

If `rsvg-convert` isn't available, use ImageMagick:

```bash
convert -background none -density 300 brand/logo-avatar-color.svg -resize 512x512 brand/exports/logo-avatar-512.png
```

**Step 3: Verify PNG quality**

Open each PNG and check for: crisp edges, correct colors, no artifacts, transparent background.

```bash
open brand/exports/logo-avatar-512.png
```

**Step 4: Commit**

```bash
git add brand/exports/
git commit -m "feat: add PNG exports for social platform avatars"
```

---

### Task 9: Final visual review and cleanup

**Files:**
- Review: all `brand/*.svg` and `brand/exports/*.png`
- Modify: any files needing final adjustments

**Step 1: Visual audit checklist**

Open each file and verify against the design doc (`docs/plans/2026-02-26-logo-design.md`):

- [ ] Shield shape: irregular edges, not mathematically perfect
- [ ] Iron bands: rust colored, lower band has visible kink
- [ ] Rivets: 6 total, at band-plank intersections
- [ ] Crack: branches off middle plank, subtle
- [ ] Text (full mark): "BUILD" above upper band, "CHARACTER" below lower band
- [ ] Monogram (avatar): "BC" centered between bands
- [ ] Favicon: recognizable at 16px in browser tab
- [ ] Monochrome variants: all single-color, distinguish bands by fill vs. stroke
- [ ] Site header: icon + text combination, hover works
- [ ] Colors: only charcoal, rust, offwhite used (no off-palette colors)

**Step 2: Fix any issues found**

Address each failed check. Re-verify after changes.

**Step 3: Final commit**

```bash
git add -A brand/ site/
git commit -m "chore: logo visual review and final adjustments"
```

---

## File Summary

| File | Task | Description |
|------|------|-------------|
| `brand/logo-full-color.svg` | 1 | Full mark with text, color |
| `brand/logo-icon-color.svg` | 2 | Icon mark (no text), color |
| `brand/logo-avatar-color.svg` | 3 | Avatar with BC monogram, color |
| `brand/favicon.svg` | 4 | Minimal favicon shield |
| `site/public/favicon.svg` | 4 | Deployed favicon (copy) |
| `brand/logo-full-mono-charcoal.svg` | 5 | Full mark, charcoal mono |
| `brand/logo-full-mono-offwhite.svg` | 5 | Full mark, offwhite mono |
| `brand/logo-icon-mono-charcoal.svg` | 5 | Icon, charcoal mono |
| `brand/logo-icon-mono-offwhite.svg` | 5 | Icon, offwhite mono |
| `brand/logo-avatar-mono-charcoal.svg` | 5 | Avatar, charcoal mono |
| `brand/logo-avatar-mono-offwhite.svg` | 5 | Avatar, offwhite mono |
| `site/public/logo-icon-color.svg` | 6 | Icon copy for site header |
| `site/src/layouts/Base.astro` | 6 | Header updated with logo |
| `brand/exports/logo-avatar-512.png` | 8 | Social avatar PNG |
| `brand/exports/logo-avatar-256.png` | 8 | Social avatar PNG (small) |
| `brand/exports/logo-full-1024.png` | 8 | Full mark PNG |
