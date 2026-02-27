# Astro Site Redesign Port - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Port the Lovable visual design (character-forge) into the existing Astro site, with naming corrections (Journal/Shop) and manifesto content fix.

**Architecture:** Direct CSS/template port. The Lovable prototype uses React + Tailwind v3 (config file + HSL variables). The Astro site uses Tailwind v4 (@theme directive). Design tokens translate to @theme, React components become Astro templates, ScrollReveal becomes a vanilla JS IntersectionObserver script.

**Tech Stack:** Astro 5, Tailwind v4, vanilla JS (no React in Astro), Cloudflare Pages

**Source reference:** `/Users/llama/Development/character-forge/` (Lovable prototype)
**Target:** `/Users/llama/Development/builds-character/site/`

---

### Task 1: Update global.css with new design tokens

**Files:**
- Modify: `site/src/styles/global.css`

**Step 1: Rewrite global.css**

Add warm-gray color, noise overlay, topo pattern, reading utilities, letter-spacing utilities. Port from character-forge's `index.css` + `tailwind.config.ts`.

```css
@import "tailwindcss";

@theme {
  /* Brand colors - primary */
  --color-charcoal: #1a1a1a;
  --color-bone: #f5f0eb;

  /* Brand colors - secondary */
  --color-rust: #8b4513;
  --color-forest: #2d5016;

  /* Depth and utility */
  --color-warm-gray: #c4bbb2;
  --color-muted: #6b7280;

  /* Fonts */
  --font-sans: 'Inter', ui-sans-serif, system-ui, sans-serif;
  --font-display: 'Space Grotesk', ui-sans-serif, system-ui, sans-serif;

  /* Letter spacing */
  --tracking-ultra-wide: 0.25em;
  --tracking-mega-wide: 0.4em;

  /* Line height */
  --leading-reading: 1.75;
}

/* Noise overlay texture */
.noise-overlay {
  position: relative;
}
.noise-overlay::before {
  content: "";
  position: absolute;
  inset: 0;
  opacity: 0.06;
  pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  background-repeat: repeat;
  background-size: 256px 256px;
  z-index: 1;
}
.noise-overlay > * {
  position: relative;
  z-index: 2;
}

/* Topo pattern texture */
.topo-pattern {
  position: relative;
}
.topo-pattern::after {
  content: "";
  position: absolute;
  inset: 0;
  opacity: 0.04;
  pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg width='200' height='200' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M100 20c44 0 80 36 80 80s-36 80-80 80S20 144 20 100 56 20 100 20z' fill='none' stroke='%23f5f0eb' stroke-width='0.5'/%3E%3Cpath d='M100 40c33 0 60 27 60 60s-27 60-60 60-60-27-60-60 27-60 60-60z' fill='none' stroke='%23f5f0eb' stroke-width='0.5'/%3E%3Cpath d='M100 60c22 0 40 18 40 40s-18 40-40 40-40-18-40-40 18-40 40-40z' fill='none' stroke='%23f5f0eb' stroke-width='0.5'/%3E%3C/svg%3E");
  background-repeat: repeat;
  background-size: 200px 200px;
  z-index: 1;
}
.topo-pattern > * {
  position: relative;
  z-index: 2;
}

/* Scroll reveal */
.scroll-reveal {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.8s ease-out, transform 0.8s ease-out;
}
.scroll-reveal.revealed {
  opacity: 1;
  transform: translateY(0);
}

/* Reading width */
.reading-width {
  max-width: 65ch;
}
```

**Step 2: Verify build**

Run: `cd /Users/llama/Development/builds-character/site && npx astro build`
Expected: Clean build, no errors

**Step 3: Commit**

```bash
git add site/src/styles/global.css
git commit -m "feat: update design tokens with noise, topo, scroll reveal, reading utilities"
```

---

### Task 2: Update Google Fonts import for additional weights

**Files:**
- Modify: `site/src/layouts/Base.astro`

**Step 1: Update font link to include light weight for pull quotes**

Change the Google Fonts import to include Space Grotesk 300 (light) weight:
```html
<link
  href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@300;500;700&display=swap"
  rel="stylesheet"
/>
```

**Step 2: Commit**

```bash
git add site/src/layouts/Base.astro
git commit -m "feat: add Space Grotesk light weight for pull quotes"
```

---

### Task 3: Rewrite Base.astro layout

**Files:**
- Modify: `site/src/layouts/Base.astro`

**Step 1: Rewrite the layout**

Port from character-forge's Navbar.tsx and Footer.tsx. Key changes:
- Fixed nav with backdrop blur (from Lovable Navbar)
- Nav items: Journal, Shop, Manifesto (no Home link - logo is home)
- Nav uses tracking-ultra-wide uppercase style
- Footer: minimal, noise overlay, ultra-wide tracking
- Remove `max-w-5xl` constraint from main (pages control their own width)
- Remove `py-12` from main (pages control their own spacing)
- Change html class from `bg-offwhite` to `bg-bone`
- Add scroll-reveal JS script to body

Reference: `character-forge/src/components/Navbar.tsx` and `Footer.tsx`

The `<main>` tag should have no padding or max-width since each page controls its own full-bleed sections (dark hero, bone content, dark email capture).

Add inline script at end of body for scroll reveal:
```html
<script>
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const delay = parseInt(el.dataset.delay || '0');
        setTimeout(() => el.classList.add('revealed'), delay);
        observer.unobserve(el);
      }
    });
  }, { threshold: 0.15 });
  document.querySelectorAll('.scroll-reveal').forEach(el => observer.observe(el));
</script>
```

**Step 2: Verify build**

Run: `cd /Users/llama/Development/builds-character/site && npx astro build`

**Step 3: Commit**

```bash
git add site/src/layouts/Base.astro
git commit -m "feat: rewrite layout with fixed nav, Journal/Shop/Manifesto, scroll reveal"
```

---

### Task 4: Rewrite index.astro (homepage)

**Files:**
- Modify: `site/src/pages/index.astro`

**Step 1: Rewrite homepage**

Port from character-forge's `pages/Index.tsx`. Key sections:
1. Full-viewport dark hero with massive "BUILDS CHARACTER", rust tagline, noise + topo overlays
2. Transition strip ("Effort compounds.")
3. Recent articles section (editorial cards with rust/forest left borders) - header says "Recent" not "Recent Field Notes"
4. Email capture ("The Logbook") in dark section with noise overlay

Article links point to `/journal` (not `/field-notes`).
Keep the Formspree form with PLACEHOLDER ID (existing known issue).

Reference: `character-forge/src/pages/Index.tsx`

**Step 2: Verify build and visual check**

Run: `cd /Users/llama/Development/builds-character/site && npx astro dev`
Check localhost in browser.

**Step 3: Commit**

```bash
git add site/src/pages/index.astro
git commit -m "feat: rewrite homepage with full-bleed hero, editorial cards, email capture"
```

---

### Task 5: Move field-notes/ to journal/ and rewrite listing

**Files:**
- Delete: `site/src/pages/field-notes/index.astro`
- Delete: `site/src/pages/field-notes/[...slug].astro`
- Create: `site/src/pages/journal/index.astro`
- Create: `site/src/pages/journal/[...slug].astro`

**Step 1: Create journal/index.astro**

Port from character-forge's `pages/FieldNotes.tsx` but using Astro content collections. Key changes:
- Page header: dark section with noise overlay, "JOURNAL" in massive type
- Subtitle: "Observations on effort, discipline, and the long game."
- Featured article: full-width card with rust left border, large title, excerpt
- Grid: 2-column with warm-gray left borders, hover transitions
- Tags in forest green
- All scroll-reveal enabled

Reference: `character-forge/src/pages/FieldNotes.tsx`

**Step 2: Create journal/[...slug].astro**

Copy existing `field-notes/[...slug].astro` logic (content collection rendering) but update the prose styling to match the new design:
- Dark header section with noise overlay (title, date, tags)
- Bone body section with generous reading width
- Keep the existing Tailwind prose selectors but adjust colors for bone/charcoal palette

**Step 3: Delete old field-notes directory**

```bash
rm -r site/src/pages/field-notes/
```

**Step 4: Verify build**

Run: `cd /Users/llama/Development/builds-character/site && npx astro build`

**Step 5: Commit**

```bash
git add site/src/pages/journal/ site/src/pages/field-notes/
git commit -m "feat: rename field-notes to journal with editorial listing design"
```

---

### Task 6: Rename equipment.astro to shop.astro and rewrite

**Files:**
- Delete: `site/src/pages/equipment.astro`
- Create: `site/src/pages/shop.astro`

**Step 1: Create shop.astro**

Port from character-forge's `pages/Equipment.tsx`. Key changes:
- Page header: dark section with noise overlay, "SHOP" in massive type
- Subtitle: "Carry the ethos."
- Product grid: 3-column, warm-gray card backgrounds, phrase prominently displayed
- Rust CTA buttons, hover lift animations
- Scroll reveal on cards

Uses Astro content collections for product data (same `getCollection('products')` approach).
Keep the existing product filtering JS for product types.

Reference: `character-forge/src/pages/Equipment.tsx`

**Step 2: Delete old equipment.astro**

```bash
rm site/src/pages/equipment.astro
```

**Step 3: Verify build**

Run: `cd /Users/llama/Development/builds-character/site && npx astro build`

**Step 4: Commit**

```bash
git add site/src/pages/shop.astro site/src/pages/equipment.astro
git commit -m "feat: rename equipment to shop with new product grid design"
```

---

### Task 7: Rewrite manifesto.astro

**Files:**
- Modify: `site/src/pages/manifesto.astro`

**Step 1: Rewrite manifesto page**

Port from character-forge's `pages/Manifesto.tsx`. Key changes:
- Dark header with noise + topo, "MANIFESTO" in massive type
- Alternating dark/light sections with pull quotes
- **FIX:** Remove "This is not a motivational brand. It is a composure brand." Replace with a statement that embodies the philosophy without explaining positioning.
- Each section: pull quote at 3xl-6xl scale + body text at reading width
- Final section: "Thank yourself later." standalone at largest scale
- Closing mark: "Builds Character" in muted bone

Manifesto sections (corrected):
1. (dark) "Growth is not accidental." + body
2. (light) "The present does the work. The future collects." + body
3. (dark) "Comfort is a direction, not a destination." + body
4. (light) "We choose the hard path knowing the payoff is worth it." + body
5. (dark) "Thank yourself later." (no body, largest scale)

Reference: `character-forge/src/pages/Manifesto.tsx` (but with corrected content)

**Step 2: Verify build and visual check**

**Step 3: Commit**

```bash
git add site/src/pages/manifesto.astro
git commit -m "feat: rewrite manifesto with alternating sections and corrected content"
```

---

### Task 8: Update _redirects for new routes

**Files:**
- Modify: `site/public/_redirects`

**Step 1: Add redirects for renamed routes**

Keep existing redirects and add:
```
# Field notes -> journal
/field-notes /journal 301
/field-notes/ /journal 301
/field-notes/* /journal/:splat 301

# Equipment -> shop
/equipment /shop 301
/equipment/ /shop 301
```

Also update existing blog/shop redirects to point to new routes:
```
/blog /journal 301
/blog/ /journal 301
/blog/* /journal 301
/shop /shop 301
/shop/ /shop 301
/shop/* /shop 301
```

**Step 2: Commit**

```bash
git add site/public/_redirects
git commit -m "feat: update redirects for journal and shop route renames"
```

---

### Task 9: Update content collection author default

**Files:**
- Modify: `site/src/content.config.ts`

**Step 1: Change blog author default**

Change `author: z.string().default('Hobson')` to `author: z.string().default('Builds Character')` to match the brand overhaul.

**Step 2: Commit**

```bash
git add site/src/content.config.ts
git commit -m "feat: update blog author default to Builds Character"
```

---

### Task 10: Update Hobson's git_ops.py for new route

**Files:**
- Modify: `hobson/src/hobson/tools/git_ops.py`

**Step 1: Check and update blog publishing path references**

Search git_ops.py for any hardcoded `/field-notes/` or `field-notes` path references and update to `/journal/`. The content data path (`src/data/blog/`) does NOT change - only URL references in any notification messages or PR descriptions.

Similarly check for `/equipment/` references and update to `/shop/`.

**Step 2: Check and update other workflow files**

Search all Python files for hardcoded route references:
```bash
grep -r "field-notes\|equipment" hobson/src/hobson/
```

Update any matches.

**Step 3: Run tests**

Run: `cd /Users/llama/Development/builds-character/hobson && python -m pytest tests/ -v`
Expected: All 38 tests pass

**Step 4: Commit**

```bash
git add hobson/
git commit -m "feat: update Hobson route references from field-notes/equipment to journal/shop"
```

---

### Task 11: Final verification and state update

**Files:**
- Modify: `STATE.md`
- Modify: `PROJECT.md`

**Step 1: Build and verify**

Run: `cd /Users/llama/Development/builds-character/site && npx astro build`
Expected: Clean build

Run: `cd /Users/llama/Development/builds-character/site && npx astro dev`
Visual check: all pages render correctly

**Step 2: Update STATE.md**

Add "Site Redesign Port" section to status. Update next steps.

**Step 3: Update PROJECT.md decisions log**

Add entry for route rename and site redesign.

**Step 4: Commit**

```bash
git add STATE.md PROJECT.md
git commit -m "docs: update project state for site redesign port"
```

---

## Dependency Order

Tasks 1-3 must be sequential (CSS -> fonts -> layout).
Task 4 (homepage) depends on Task 3.
Tasks 5-7 (journal, shop, manifesto) can run after Task 3 and are independent of each other.
Task 8 (redirects) runs after Tasks 5-6.
Task 9 (content config) is independent.
Task 10 (Hobson tools) is independent.
Task 11 (verification) runs last.

## Notes for Implementer

- The Astro site uses **Tailwind v4** with `@theme` syntax, NOT Tailwind v3 with a config file. Do not create a `tailwind.config.ts`.
- Color references: the old site used `offwhite` and `slate`. The new design uses `bone` and `muted`. Update all class references.
- The Lovable prototype has ~50 shadcn UI component files. **Ignore all of them.** Only port the 4 page components, Navbar, Footer, and ScrollReveal.
- Astro pages use `---` frontmatter for server-side logic, not React hooks. Forms need vanilla JS, not useState.
- The scroll-reveal in Astro is a CSS class + inline script, not a React component.
