# Brand Overhaul Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Full brand reset from humor-first "funny suffering" to composure-driven philosophy brand, touching brand guidelines, all workflow prompts, site pages, content, and merch.

**Architecture:** Replace brand_guidelines.md (cascades to agent system prompt automatically). Rewrite 4 workflow prompt strings. Overhaul 5 Astro pages + layout + CSS. Delete old content and products. Add email capture. Add URL redirects. Update Obsidian Standing Orders.

**Tech Stack:** Python (workflow prompts), Astro (site), CSS (Tailwind v4), Obsidian REST API (standing orders), Printful API (product teardown)

**Design doc:** `docs/plans/2026-02-26-brand-overhaul-design.md`

---

### Task 1: Replace brand guidelines

**Files:**
- Overwrite: `brand/brand_guidelines.md`

**Step 1: Write the new brand guidelines**

Replace the entire file with:

```markdown
# Builds Character Brand Guidelines

> Machine-readable brand spec. Loaded into Hobson's system prompt for every generation task.

## Brand Statement

Builds Character exists for people who choose the hard way on purpose.

Growth is not accidental. It is earned through discomfort, repetition, resistance, and time. We are not here for ease. We are here for endurance.

Character is formed in the space between now and later, between effort and reflection, between fatigue and pride. The work may not feel good in the moment. That is the point.

## Positioning

- **Category:** Endurance-minded philosophy brand
- **Territory:** Voluntary hardship, long-term growth, self-respect
- **Enemy:** Comfort culture, instant gratification, performative grit
- **Audience:** Adults who train, build, raise, create, or endure intentionally

This is not a motivational brand. It is a composure brand.

## Core Idea

- Effort compounds.
- Discomfort is an investment.
- Character is built across time.

**Tagline:** Thank Yourself Later.

"Thank Yourself Later" reframes hardship as a gift to the future self. The present does the work. The future receives the benefit.

## Voice Guidelines

**Tone:** Measured. Calm. Dry. Direct.

**Never:**
- Overly inspirational
- Aggressive
- Cheesy
- Cute
- Loud

**Principle:** Write as if you've already done the miles.

Avoid exclamation points. Avoid "embrace the suck" energy. Avoid hustle-culture cliches.

Understatement carries authority.

**Examples:**

| Weak | Strong |
|------|--------|
| "Push harder! You've got this!" | "Conditions were suboptimal." |
| "Pain is temporary!" | "It won't feel good. It will feel worth it." |
| "Embrace the grind!" | "Tuesday. Again." |

## Rules

1. Never use first-person pronouns (I, me, my) to describe physical events. Frame observations objectively or in second person ("you").
2. Do not invent fictional anecdotes or fake personal experiences. The voice has earned authority without needing a fabricated backstory.
3. No motivational platitudes. No transformation promises. State what is, not what could be.
4. Profanity is acceptable in moderation. Corporate-speak is never acceptable.
5. Every piece of content should pass the "would you actually share this?" test.

## Two Voices: Blog vs. Substack

### Blog Voice (buildscharacter.com / "Field Notes")

The blog is the brand. Philosophy and experience of deliberate difficulty.

- **Perspective:** Second person ("you") or objective. Never first-person accounts of physical events.
- **Topics:** Deliberate difficulty across domains. Training, building, creating, raising, enduring. Outdoor-weighted in Phase 1, but the frame is philosophy, not comedy.
- **AI references:** None. Zero. The brand stands on its own. No mention of being AI, having algorithms, agents, automation, or any aspect of being a machine.
- **Tone:** Measured composure. Earned authority through understatement.
- **What NOT to do:** Do not analyze the audience from the outside. Do not mock activities the audience values. Do not use exclamation points. Do not be motivational.

### Substack Voice (buildscharacter.substack.com)

The Substack is a separate professional project documenting the technical build. It is not part of the brand. The brand site does not link to it.

- **Perspective:** First person as Hobson. Transparent about being AI.
- **Topics:** Technical build log, operational reporting, revenue data, decisions, failures. Co-authored with Michael (the human operator).
- **AI references:** Expected and encouraged. This is the whole point.
- **Tone:** Measured, composed, direct. Same discipline as the blog voice. Competent operator reporting, not personality-driven quirkiness.
- **"From the Operator" section:** Michael's strategic reflections on directing the agent.

## Example Headlines

### Blog (On-Brand)

- "Conditions Were Suboptimal"
- "The Case for Doing It Again Tomorrow"
- "What You Carry Gets Lighter. Eventually."
- "Nobody Asked You to Be Here"
- "Tuesday. Again."
- "The Part You Don't Post About"

### Blog (Off-Brand -- NEVER do this)

- "Push Through the Pain! You've Got This!" (motivational)
- "I ran my first ultra and here's what happened" (first-person fabrication)
- "10 Ways Suffering Makes You Stronger" (listicle self-help)
- "Embrace the Grind: Why Hard Work Pays Off" (hustle culture)

### Substack (On-Brand)

- "Week 3: Revenue Was $12. Here's the Plan."
- "The Content Pipeline Broke Twice This Week"
- "Why I Rewrote the Brand Guidelines at 2am"

## Visual Identity

### Colors

- **Primary:** Charcoal / deep graphite (#1a1a1a), Off-white / bone (#f5f0eb)
- **Secondary:** Forest green (#2d5016), Burnt rust (#8b4513), Muted technical red (#a63d40, sparingly)

No gradients. No neon. No trendy earthtone palettes. Restraint = credibility.

### Typography

- **Display / Headers:** Space Grotesk (medium to bold weight, slight tracking in all caps)
- **Body:** Inter
- No monospace fonts on the public site (signals tech/coder aesthetic)

### Iconography (Optional)

If used, abstract and terrain-based:
- Elevation line
- Contour ring
- Minimal switchback
- Compass needle abstraction

One-color capable. Embroidery-safe. Legible at 16px. No literal mountains with birds.

## Application Principles

Everything must feel: durable, scalable, quietly serious, engineered.

If it looks like a sticker, it is wrong. If it looks like a creed, it is right.

The brand should feel at home on ultralight gear, on technical apparel, in a Strava screenshot, on a minimalist patch, in a training journal.

## Legal Constraints

- "Builds character" is an unprotectable common phrase
- NEVER reference Calvin, Hobbes, Bill Watterson, or any Calvin and Hobbes imagery in commercial materials
- The phrase predates the comic and belongs to no one
```

**Step 2: Verify the file loads**

Run: `cd /Users/llama/Development/builds-character/hobson && python -c "from hobson.config import settings; from pathlib import Path; p = Path(settings.brand_guidelines_path); print('OK' if p.exists() else 'MISSING')"`
Expected: `OK`

**Step 3: Commit**

```bash
git add brand/brand_guidelines.md
git commit -m "Replace brand guidelines with composure brand identity"
```

---

### Task 2: Update agent system prompt

**Files:**
- Modify: `hobson/src/hobson/agent.py` (lines 45-73)

**Step 1: Update the system prompt**

Replace the SYSTEM_PROMPT string. Change the mission statement and operating principles to match the new brand. Keep tool descriptions and standing orders logic identical.

Replace:
```python
SYSTEM_PROMPT = f"""You are Hobson, an autonomous AI agent running the BuildsCharacter.com business.

Your mission: celebrate the universal experience of doing hard things. Make suffering funny, shareable, and wearable.
```

With:
```python
SYSTEM_PROMPT = f"""You are Hobson, an autonomous AI agent running the BuildsCharacter.com business.

Your mission: build and operate an endurance-minded philosophy brand for people who choose the hard way on purpose. Effort compounds. Discomfort is an investment. Character is built across time.
```

Also replace in the Operating Principles section:
```
- Write in your voice: dry, self-aware, competent but honest
```
With:
```
- Write in your voice: measured, calm, dry, direct. Understatement carries authority.
```

**Step 2: Run existing tests**

Run: `cd /Users/llama/Development/builds-character/hobson && python -m pytest tests/ -v`
Expected: All tests pass (no tests depend on system prompt content)

**Step 3: Commit**

```bash
git add hobson/src/hobson/agent.py
git commit -m "Update agent system prompt for composure brand voice"
```

---

### Task 3: Rewrite content pipeline prompt

**Files:**
- Modify: `hobson/src/hobson/workflows/content_pipeline.py`

**Step 1: Replace the CONTENT_PIPELINE_PROMPT**

Replace the entire `CONTENT_PIPELINE_PROMPT` string with a new version that:

- Step 2 (topic selection): Broadens from "hiking/running/cold exposure" to "deliberate difficulty" (training, building, creating, raising, enduring). Still outdoor-weighted Phase 1.
- Step 3 (writing): Voice instructions change to "measured, calm, direct. Write as if you've already done the miles. Understatement carries authority." Add explicit hallucination guardrails: "Never use first-person pronouns (I, me, my) to describe physical events. Frame observations objectively or in second person. Do not invent fictional anecdotes."
- Remove "Include at least one joke that earns its spot"
- Remove "End with a subtle Substack CTA" (no Substack link from brand site)
- CRITICAL VOICE RULES updated: no exclamation points, no motivational energy, no humor-first approach. Composure, not comedy.

**Step 2: Verify Python syntax**

Run: `cd /Users/llama/Development/builds-character/hobson && python -c "from hobson.workflows.content_pipeline import CONTENT_PIPELINE_PROMPT; print('OK:', len(CONTENT_PIPELINE_PROMPT), 'chars')"`
Expected: `OK: <number> chars`

**Step 3: Commit**

```bash
git add hobson/src/hobson/workflows/content_pipeline.py
git commit -m "Rewrite content pipeline prompt for composure brand voice"
```

---

### Task 4: Rewrite design batch prompt

**Files:**
- Modify: `hobson/src/hobson/workflows/design_batch.py`

**Step 1: Replace the DESIGN_BATCH_PROMPT**

Replace the entire `DESIGN_BATCH_PROMPT` string. Key changes:

- Step 3 (concept generation): Replace humor-first examples with composure concepts:
  - "Thank Yourself Later" (tagline, universal)
  - "Conditions Were Suboptimal" (earned understatement)
  - "Effort Compounds" (core idea, minimal)
  - "Type II" (endurance terminology, abstract)
  - "Tuesday. Again." (quiet resolve)
- Step 3 product focus: Stickers and patches first. "If it looks like a sticker, it is wrong. If it looks like a creed, it is right."
- Step 6 (image generation): Style guidance changes to "one-color capable, embroidery-safe, abstract terrain-based iconography (contour lines, elevation marks, compass abstractions). No literal mountains with birds. No clip art."
- Step 6 color palette: charcoal (#1a1a1a), bone (#f5f0eb), forest green (#2d5016), burnt rust (#8b4513)
- Remove closing "make people laugh" instruction. Replace with "Your designs should feel durable, scalable, and quietly serious. Engineered, not playful."
- Update DESIGN_BATCH_BOOTSTRAP_PROMPT to track the same changes (it's derived via `.replace()` so verify the replaced substring still matches)

**Step 2: Verify Python syntax**

Run: `cd /Users/llama/Development/builds-character/hobson && python -c "from hobson.workflows.design_batch import DESIGN_BATCH_PROMPT, DESIGN_BATCH_BOOTSTRAP_PROMPT; print('OK:', len(DESIGN_BATCH_PROMPT), len(DESIGN_BATCH_BOOTSTRAP_PROMPT))"`
Expected: `OK: <number> <number>`

**Step 3: Commit**

```bash
git add hobson/src/hobson/workflows/design_batch.py
git commit -m "Rewrite design batch prompt for composure brand aesthetic"
```

---

### Task 5: Update Substack dispatch and bootstrap diary prompts

**Files:**
- Modify: `hobson/src/hobson/workflows/substack_dispatch.py`
- Modify: `hobson/src/hobson/workflows/bootstrap_diary.py`

**Step 1: Update substack_dispatch.py**

In the `SUBSTACK_DISPATCH_PROMPT` string, update the style rules section (around step 3):

Replace:
```
   **Style rules:**
   - Write in first person as Hobson
   - Be transparent about being an AI. Never pretend otherwise.
   - Use real numbers even when they're embarrassing
   - Humor should be dry and earned, not forced
   - No corporate-speak, no hype, no motivational platitudes
   - The tone is: competent but honest, like a friend giving you the real update
```

With:
```
   **Style rules:**
   - Write in first person as Hobson
   - Be transparent about being an AI. Never pretend otherwise.
   - Use real numbers even when they are embarrassing
   - Tone: measured, composed, direct. No forced humor, no personality-driven quirkiness.
   - No corporate-speak, no hype, no motivational platitudes, no exclamation points
   - Deliver operational reporting with composure. Competent and honest.
```

Also update the closing paragraph. Replace:
```
Remember: this is the flagship content product. It should be the best thing
you write all week. The audience subscribed because they want to watch an AI
try to build a business with radical transparency, AND hear the human
operator's perspective on directing and refining the agent. The dual
perspective (Hobson's operational view + Michael's strategic view) is what
makes this newsletter unique. Give them a reason to open the email next Friday.
```

With:
```
Remember: the Substack serves as a technical build log and professional
showcase. The audience follows because they want to understand how an AI
agent operates a business, with real numbers and honest reporting. The dual
perspective (Hobson's operational view + Michael's strategic view) is what
makes this newsletter distinct. Deliver substance, not spectacle.
```

**Step 2: Update bootstrap_diary.py**

In the `BOOTSTRAP_DIARY_PROMPT` string, update the style rules:

Replace:
```
   Style rules:
   - Raw and operational, not polished prose
   - Real numbers, real failures, no sugarcoating
   - Dry humor when it fits naturally
   - This is a build log for Substack source material, not a blog post
```

With:
```
   Style rules:
   - Operational and direct, not polished prose
   - Real numbers, real failures, no sugarcoating
   - No forced humor. If something is notable, state it plainly.
   - This is a build log for Substack source material, not a blog post
```

**Step 3: Verify Python syntax for both**

Run: `cd /Users/llama/Development/builds-character/hobson && python -c "from hobson.workflows.substack_dispatch import SUBSTACK_DISPATCH_PROMPT; from hobson.workflows.bootstrap_diary import BOOTSTRAP_DIARY_PROMPT; print('OK')"`
Expected: `OK`

**Step 4: Commit**

```bash
git add hobson/src/hobson/workflows/substack_dispatch.py hobson/src/hobson/workflows/bootstrap_diary.py
git commit -m "Update Substack and bootstrap diary prompts for composure voice"
```

---

### Task 6: Update site CSS and typography

**Files:**
- Modify: `site/src/styles/global.css`
- Modify: `site/src/layouts/Base.astro` (font imports only)

**Step 1: Update global.css**

Replace the entire `@theme` block:

```css
@theme {
  /* Brand colors - primary */
  --color-charcoal: #1a1a1a;
  --color-offwhite: #f5f0eb;

  /* Brand colors - secondary */
  --color-rust: #8b4513;
  --color-forest: #2d5016;
  --color-technical-red: #a63d40;

  /* Utility colors */
  --color-slate: #4a5568;
  --color-cream: #faf6f1;

  /* Fonts - no monospace on public site */
  --font-sans: 'Inter', ui-sans-serif, system-ui, sans-serif;
  --font-display: 'Space Grotesk', ui-sans-serif, system-ui, sans-serif;
}
```

Key changes:
- `--color-rust` changes from `#c45d3e` to `#8b4513` (burnt rust, more muted)
- `--color-sage` removed, replaced with `--color-forest: #2d5016`
- `--color-technical-red: #a63d40` added
- `--font-mono` removed (no JetBrains Mono on public site)

**Step 2: Update font import in Base.astro**

In `site/src/layouts/Base.astro`, replace the Google Fonts link:

Replace:
```html
    <link
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Space+Grotesk:wght@500;700&display=swap"
      rel="stylesheet"
    />
```

With:
```html
    <link
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap"
      rel="stylesheet"
    />
```

**Step 3: Search for `font-mono` usage in site templates**

Run: `grep -rn "font-mono" /Users/llama/Development/builds-character/site/src/`

Replace any `font-mono` classes in site templates with `text-sm` or remove them. These appear in:
- `shop.astro` (filter buttons, product type labels, prices, empty state)
- `Base.astro` (footer, if any)
- `index.astro` (post dates)
- `about.astro` (bottom CTA)

Replace `font-mono` with appropriate alternatives (usually just remove it, or use `font-sans text-sm`).

**Step 4: Commit**

```bash
git add site/src/styles/global.css site/src/layouts/Base.astro
git commit -m "Update color palette and remove JetBrains Mono from public site"
```

---

### Task 7: Overhaul site layout and navigation

**Files:**
- Modify: `site/src/layouts/Base.astro`

**Step 1: Update navigation links**

Replace the `navLinks` array:

```javascript
const navLinks = [
  { href: '/', label: 'Home' },
  { href: '/field-notes', label: 'Field Notes' },
  { href: '/equipment', label: 'Equipment' },
  { href: '/manifesto', label: 'Manifesto' },
];
```

**Step 2: Update header brand name**

Replace `BuildsCharacter` with `BUILDS CHARACTER` (all caps, per brand guidelines slight tracking):

```html
<a href="/" class="font-display font-bold text-xl tracking-widest hover:text-rust transition-colors">
  BUILDS CHARACTER
</a>
```

**Step 3: Update default description**

Replace:
```javascript
description = 'Celebrating the universal experience of doing hard things. Making suffering funny, shareable, and wearable.',
```

With:
```javascript
description = 'For people who choose the hard way on purpose. Effort compounds. Thank yourself later.',
```

**Step 4: Update OG title format**

Replace `{title} | BuildsCharacter` with `{title} | Builds Character` (two occurrences: `<title>` and `og:title`).

**Step 5: Replace footer**

Replace the entire footer section:

```html
<footer class="border-t border-charcoal/10 mt-auto">
  <div class="max-w-5xl mx-auto px-4 py-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-slate">
    <p class="tracking-wide font-display">BUILDS CHARACTER</p>
    <p>&copy; {new Date().getFullYear()}</p>
  </div>
</footer>
```

No Substack link. No Hobson credit. No Instagram (handle change deferred).

**Step 6: Commit**

```bash
git add site/src/layouts/Base.astro
git commit -m "Overhaul site nav, header, and footer for brand reset"
```

---

### Task 8: Rewrite homepage

**Files:**
- Modify: `site/src/pages/index.astro`

**Step 1: Replace the entire page content**

```astro
---
import Base from '../layouts/Base.astro';
import { getCollection } from 'astro:content';

const posts = (await getCollection('blog', ({ data }) => !data.draft))
  .sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf())
  .slice(0, 3);
---

<Base title="Home">
  <!-- Hero -->
  <section class="py-20 text-center">
    <h1 class="font-display text-5xl font-bold tracking-widest mb-4">
      BUILDS CHARACTER
    </h1>
    <p class="text-lg text-slate mb-2">
      Thank Yourself Later.
    </p>
    <p class="text-slate max-w-xl mx-auto mb-10">
      For people who choose the hard way on purpose.
    </p>
    <div class="flex gap-4 justify-center">
      <a
        href="/field-notes"
        class="bg-rust text-offwhite px-6 py-3 font-medium hover:bg-rust/90 transition-colors"
      >
        Field Notes
      </a>
      <a
        href="/equipment"
        class="border border-charcoal px-6 py-3 font-medium hover:bg-charcoal hover:text-offwhite transition-colors"
      >
        Equipment
      </a>
    </div>
  </section>

  <!-- Latest Posts -->
  {posts.length > 0 && (
    <section class="py-12">
      <h2 class="font-display text-2xl font-bold mb-8">Recent</h2>
      <div class="grid gap-8 md:grid-cols-3">
        {posts.map((post) => (
          <a href={`/field-notes/${post.id}`} class="group">
            <article class="border border-charcoal/10 p-6 hover:border-rust/40 transition-colors h-full">
              <time class="text-sm text-slate">
                {post.data.pubDate.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
              </time>
              <h3 class="font-display font-bold text-lg mt-2 group-hover:text-rust transition-colors">
                {post.data.title}
              </h3>
              <p class="text-slate mt-2 text-sm">
                {post.data.description}
              </p>
            </article>
          </a>
        ))}
      </div>
    </section>
  )}

  <!-- Email Capture -->
  <section class="py-12 border-t border-charcoal/10">
    <div class="text-center">
      <h2 class="font-display text-2xl font-bold mb-3">The Logbook</h2>
      <p class="text-slate mb-6 max-w-lg mx-auto">
        Periodic dispatches on effort, discipline, and the long game.
      </p>
      <form
        action="https://formspree.io/f/PLACEHOLDER"
        method="POST"
        class="flex flex-col sm:flex-row gap-3 justify-center max-w-md mx-auto"
      >
        <input
          type="email"
          name="email"
          placeholder="your@email.com"
          required
          class="flex-1 px-4 py-3 border border-charcoal/20 bg-cream text-charcoal placeholder:text-slate/50 focus:outline-none focus:border-rust"
        />
        <button
          type="submit"
          class="bg-charcoal text-offwhite px-6 py-3 font-medium hover:bg-charcoal/80 transition-colors"
        >
          Subscribe
        </button>
      </form>
    </div>
  </section>
</Base>
```

Note: The Formspree action URL needs a real form ID. Use `PLACEHOLDER` for now; the owner will set up the Formspree form and replace it.

**Step 2: Commit**

```bash
git add site/src/pages/index.astro
git commit -m "Rewrite homepage with composure brand hero and email capture"
```

---

### Task 9: Rewrite About -> Manifesto page

**Files:**
- Create: `site/src/pages/manifesto.astro`
- Delete: `site/src/pages/about.astro`

**Step 1: Create manifesto.astro**

```astro
---
import Base from '../layouts/Base.astro';
---

<Base title="Manifesto" description="Builds Character exists for people who choose the hard way on purpose.">
  <div class="max-w-3xl mx-auto">
    <h1 class="font-display text-4xl font-bold mb-8">The Standard</h1>

    <div class="space-y-6 text-charcoal/90 leading-relaxed">
      <p>
        Growth is not accidental. It is earned through discomfort, repetition,
        resistance, and time.
      </p>

      <p>
        Character is formed in the space between now and later, between effort
        and reflection, between fatigue and pride. The work may not feel good
        in the moment. That is the point.
      </p>

      <p>
        We design for those who understand Type II experiences: difficult while
        happening, meaningful in hindsight. We value discipline over drama,
        resilience over noise, substance over spectacle.
      </p>

      <h2 class="font-display text-2xl font-bold mt-12">What This Is</h2>
      <p>
        Builds Character is not about suffering for show. It is about deliberate
        hardship that compounds.
      </p>
      <p>
        The present may resist you. Your future self will thank you.
      </p>

      <h2 class="font-display text-2xl font-bold mt-12">What This Is Not</h2>
      <p>
        This is not a motivational brand. It is a composure brand.
      </p>
      <p>
        We are not interested in comfort culture, instant gratification, or
        performative grit. If difficulty is only valuable when someone is
        watching, it was never about the difficulty.
      </p>

      <h2 class="font-display text-2xl font-bold mt-12">The Long View</h2>
      <p>
        This foundation was built for anywhere delayed gratification matters:
        training, parenting, entrepreneurship, creative work, health, recovery.
      </p>
      <p>
        It is not about mileage. It is about time.
      </p>
      <p>
        And time is the ultimate endurance event.
      </p>
    </div>
  </div>
</Base>
```

**Step 2: Delete about.astro**

```bash
rm site/src/pages/about.astro
```

**Step 3: Commit**

```bash
git add site/src/pages/manifesto.astro
git rm site/src/pages/about.astro
git commit -m "Replace About page with brand Manifesto"
```

---

### Task 10: Rewrite Shop -> Equipment page

**Files:**
- Create: `site/src/pages/equipment.astro`
- Delete: `site/src/pages/shop.astro`

**Step 1: Create equipment.astro**

Copy the product grid logic from shop.astro but update all brand copy. Key changes:

- Page title: "Equipment"
- Tagline: "Designed for people who choose the hard way."
- Empty state: "New designs in progress." (no Hobson, no Substack link)
- Remove `font-mono` classes (replace with plain text styling)
- Keep filter buttons, product grid, buy button click tracking
- Keep all Printful integration logic

**Step 2: Delete shop.astro**

```bash
rm site/src/pages/shop.astro
```

**Step 3: Commit**

```bash
git add site/src/pages/equipment.astro
git rm site/src/pages/shop.astro
git commit -m "Replace Shop page with Equipment page"
```

---

### Task 11: Rename blog routes to field-notes

**Files:**
- Rename: `site/src/pages/blog/` -> `site/src/pages/field-notes/`

**Step 1: Rename the directory**

```bash
mv site/src/pages/blog site/src/pages/field-notes
```

**Step 2: Update any internal links**

Check `[...slug].astro` and `index.astro` inside field-notes/ for any hardcoded `/blog/` references and update to `/field-notes/`.

**Step 3: Commit**

```bash
git add site/src/pages/field-notes/
git rm -r site/src/pages/blog/
git commit -m "Rename blog routes to field-notes"
```

---

### Task 12: Delete old content and products

**Files:**
- Delete: `site/src/data/blog/hello-world.md`
- Delete: `site/src/data/blog/rain-day-three.md`
- Delete: `site/src/data/blog/gear-suffering-style.md`
- Delete: `site/src/data/blog/parenting-builds-character.md`
- Delete: `site/src/data/blog/type-2-fun-addiction.md`
- Delete: `site/src/data/blog/cold-plunge-lies.md`
- Delete: `site/src/data/products/fueled-by-caffeine-poor-decisions-sticker.md`
- Delete: `site/src/data/products/my-legs-say-no-my-gps-says-yes-sticker.md`

**Step 1: Delete all blog posts**

```bash
rm site/src/data/blog/*.md
```

**Step 2: Delete all product files**

```bash
rm site/src/data/products/*.md
```

**Step 3: Commit**

```bash
git rm site/src/data/blog/*.md site/src/data/products/*.md
git commit -m "Remove all old blog posts and product files for brand reset"
```

---

### Task 13: Delete dashboard page and add redirects

**Files:**
- Delete: `site/src/pages/dashboard.astro`
- Create: `site/public/_redirects`

**Step 1: Delete dashboard.astro**

```bash
rm site/src/pages/dashboard.astro
```

**Step 2: Create _redirects file**

Create `site/public/_redirects` (Cloudflare Pages redirect format):

```
# Old blog posts -> homepage
/blog/hello-world /field-notes 301
/blog/rain-day-three /field-notes 301
/blog/gear-suffering-style /field-notes 301
/blog/parenting-builds-character /field-notes 301
/blog/type-2-fun-addiction /field-notes 301
/blog/cold-plunge-lies /field-notes 301

# Old blog index -> field notes
/blog /field-notes 301
/blog/ /field-notes 301

# Old shop -> equipment
/shop /equipment 301
/shop/ /equipment 301

# Old product pages -> equipment
/shop/* /equipment 301

# Old about -> manifesto
/about /manifesto 301
/about/ /manifesto 301

# Deleted dashboard
/dashboard / 301
/dashboard/ / 301
```

**Step 3: Commit**

```bash
git rm site/src/pages/dashboard.astro
git add site/public/_redirects
git commit -m "Delete dashboard page and add URL redirects for old routes"
```

---

### Task 14: Update git_ops.py references

**Files:**
- Modify: `hobson/src/hobson/tools/git_ops.py`

**Step 1: Check for brand name references**

Search for "Build Character", "BuildsCharacter", "Hobson" in git_ops.py. Update any PR descriptions, commit message templates, or footer text that references the old brand name or Hobson publicly.

Key areas:
- PR footer text (if any mentions Hobson or old brand)
- Commit message templates
- Blog post path references (if hardcoded to `blog/` instead of `field-notes/`)

Note: The `publish_blog_post` and `publish_product` tools write to `site/src/data/blog/` and `site/src/data/products/` via GitHub API. These data directory paths stay the same (Astro's content collection config determines URLs, not file paths). Only the page route changed, not the data directory.

**Step 2: Run tests**

Run: `cd /Users/llama/Development/builds-character/hobson && python -m pytest tests/ -v`
Expected: All tests pass

**Step 3: Commit**

```bash
git add hobson/src/hobson/tools/git_ops.py
git commit -m "Update git_ops references for brand reset"
```

---

### Task 15: Update Obsidian Standing Orders

**Files:**
- Remote: Obsidian vault at `98 - Hobson Builds Character/Operations/Standing Orders.md` (via REST API)

**Step 1: Read current Standing Orders**

Use the Obsidian REST API or direct file read to get the current content.

**Step 2: Rewrite the Organizational Intent section**

Replace the existing "Organizational Intent" section with updated content that reflects:

- Core purpose: "Builds Character exists for people who choose the hard way on purpose. Effort compounds. Discomfort is an investment. Character is built across time."
- Voice: Measured. Calm. Dry. Direct. Understatement carries authority.
- Anti-patterns: No exclamation points, no "embrace the suck," no hustle-culture, no motivational energy, no humor-first content.
- Two voices: Blog = philosophy of deliberate difficulty (no AI). Substack = technical build log (transparent about AI).
- Brand site does not reference Hobson, AI, or automation publicly.
- Hallucination guardrails: No first-person physical anecdotes. No invented experiences.

Keep all operational sections (bootstrap schedule, lessons learned, etc.) unchanged.

**Step 3: Commit note about this change**

This is an Obsidian vault change, not a git change. Log in the daily log that Standing Orders were updated.

---

### Task 16: Update Obsidian Content Calendar

**Files:**
- Remote: Obsidian vault at `98 - Hobson Builds Character/Content/Blog/Content Calendar.md`

**Step 1: Replace the topic list**

Clear old humor-focused topics. Replace with new-voice topics:

| Topic | Category | Notes |
|-------|----------|-------|
| Conditions Were Suboptimal | Philosophy | Understatement as authority. When the conditions were bad and you did it anyway. |
| The Case for Doing It Again Tomorrow | Discipline | Repetition as the mechanism of growth. Not motivation, just routine. |
| What You Carry Gets Lighter. Eventually. | Endurance | The adaptation curve. Physical or metaphorical load bearing. |
| Nobody Asked You to Be Here | Choice | The distinction between chosen difficulty and imposed difficulty. |
| Tuesday. Again. | Routine | The unglamorous middle. No race day, no summit, just the work. |
| The Part You Don't Post About | Honesty | What deliberate difficulty actually looks like vs. what gets shared. |
| Effort Compounds | Core Idea | The long arc argument. Small consistent inputs, large eventual outputs. |
| Type II | Experience | Difficult while happening, meaningful in hindsight. The endurance concept. |

Keep Substack topics in a separate section (operational, technical, build log).

**Step 2: Clear old design concepts**

Remove or archive existing concept notes in `98 - Hobson Builds Character/Content/Designs/Concepts/`.

---

### Task 17: Run full test suite and deploy

**Files:**
- None (verification only)

**Step 1: Run all Hobson tests**

Run: `cd /Users/llama/Development/builds-character/hobson && python -m pytest tests/ -v`
Expected: All tests pass

**Step 2: Build the Astro site locally**

Run: `cd /Users/llama/Development/builds-character/site && npm run build`
Expected: Build succeeds with no errors. Warnings about empty content collections are acceptable (we deleted all posts and products).

**Step 3: Push to GitHub**

```bash
cd /Users/llama/Development/builds-character
git push origin master
```

This triggers Cloudflare Pages deployment for the site.

**Step 4: Deploy Hobson to CT 255**

```bash
ssh root@192.168.2.16  # Loki
pct exec 255 -- bash -c 'cd /root/builds-character && git pull && systemctl restart hobson'
```

Verify:
```bash
pct exec 255 -- systemctl status hobson
pct exec 255 -- curl -s http://localhost:8080/health
```
Expected: Active (running), health OK

**Step 5: Verify site is live**

Check buildscharacter.com in browser:
- Homepage shows "BUILDS CHARACTER" / "Thank Yourself Later."
- /field-notes works (empty, no posts yet)
- /equipment works (empty, no products yet)
- /manifesto shows brand manifesto
- /blog redirects to /field-notes
- /shop redirects to /equipment
- /about redirects to /manifesto
- /dashboard redirects to /
- No Hobson or AI references anywhere on the site

**Step 6: Commit any final fixes**

If anything needs adjustment after deployment, fix and commit.

---

### Task 18: Printful product teardown

**Files:**
- None (API operation)

**Step 1: List current Printful products**

SSH to CT 255 and use the Printful API to list all current products:

```bash
ssh root@192.168.2.16
pct exec 255 -- bash -c 'source /root/builds-character/.env && curl -s -H "Authorization: Bearer $PRINTFUL_API_KEY" https://api.printful.com/store/products | python3 -m json.tool'
```

**Step 2: Delete each product via API**

For each product ID returned, delete it:

```bash
pct exec 255 -- bash -c 'source /root/builds-character/.env && curl -s -X DELETE -H "Authorization: Bearer $PRINTFUL_API_KEY" https://api.printful.com/store/products/<ID>'
```

**Step 3: Verify catalog is empty**

Re-run the list command to confirm zero products.

---

### Task 19: Update PROJECT.md and STATE.md

**Files:**
- Modify: `PROJECT.md`
- Modify: `STATE.md`

**Step 1: Update PROJECT.md**

- Update the Goal section to reflect the composure brand positioning
- Update Tech Stack if anything changed (Formspree addition for email capture)
- Add decisions to the Decisions Log:
  - 2026-02-26: Brand pivot from humor to composure
  - 2026-02-26: Decouple Substack from brand site
  - 2026-02-26: Nav renamed (Field Notes / Equipment / Manifesto)
  - 2026-02-26: Email capture via Formspree ("The Logbook")
  - 2026-02-26: Dashboard repurposed as Effort Ledger (deferred until CF tunnel ready)

**Step 2: Update STATE.md**

- Update Current Focus
- Add the brand overhaul to the status list
- Update Known Issues (remove resolved, add new like Formspree placeholder)
- Update Next Steps
- Remove Voice Split section (superseded by brand overhaul)

**Step 3: Commit**

```bash
git add PROJECT.md STATE.md
git commit -m "Update project state docs for brand overhaul"
```
