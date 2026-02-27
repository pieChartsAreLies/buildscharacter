# Brand Overhaul Design: Builds Character Rebrand

**Date:** 2026-02-26
**Status:** Approved
**Approach:** Full Reset (Approach A)

## Context

Builds Character is pivoting from a humor-first "funny suffering" brand to a composure-driven philosophy brand. The new brand statement, positioning, voice, and visual identity have been defined. This design covers the full-stack overhaul required to align every artifact with the new direction.

## Brand Foundation (User-Provided)

### Brand Statement

Builds Character exists for people who choose the hard way on purpose.

Growth is not accidental. It is earned through discomfort, repetition, resistance, and time. Character is formed in the space between effort and reflection, between fatigue and pride.

### Positioning

- **Category:** Endurance-minded philosophy brand
- **Territory:** Voluntary hardship, long-term growth, self-respect
- **Enemy:** Comfort culture, instant gratification, performative grit
- **Audience:** Adults who train, build, raise, create, or endure intentionally

### Core Idea

- Effort compounds.
- Discomfort is an investment.
- Character is built across time.
- Tagline: "Thank Yourself Later"

### Voice

- **Tone:** Measured. Calm. Dry. Direct.
- **Never:** Overly inspirational, aggressive, cheesy, cute, loud
- **Principle:** "Write as if you've already done the miles."
- **Understatement carries authority.**
- No exclamation points. No "embrace the suck" energy. No hustle-culture cliches.

### Visual Identity

- **Primary colors:** Charcoal / deep graphite, off-white / bone
- **Secondary colors:** Forest green, burnt rust, muted technical red (sparingly)
- **Typography:** Clean geometric or modern humanist sans serif. Medium to bold weight. Slight tracking in all caps for primary line.
- **Icons (if used):** Abstract, terrain-based. Elevation line, contour ring, minimal switchback, compass needle. One-color capable, embroidery-safe, legible at 16px. No literal mountains with birds.
- **No** gradients, neon, or trendy earthtone palettes.

## Key Strategic Decisions

1. **buildscharacter.com is a standalone brand.** No mention of Hobson, AI, agents, or automation on the public site. A visitor sees a brand, not an experiment.
2. **Substack is Michael's professional side project.** It documents the technical build and Hobson's operations. It serves Michael's professional narrative, not the brand. If the brand succeeds, Substack is disposable.
3. **No link from brand site to Substack.** The brand site and the AI narrative are completely firewalled. Substack may link to the brand as a case study, but the brand never links back. This prevents the "stolen valor" problem where an endurance audience discovers the author is an AI script.
4. **Hobson keeps its name internally.** Agent name stays in code, Telegram, and Obsidian. Just not on the public site.
5. **Instagram handle change** (@hobson_builds_character) deferred to later. Added to to-do list.

## Changes by Layer

### 1. Brand Guidelines (brand/brand_guidelines.md)

Full replacement. New structure:

1. Brand Statement (verbatim from user document)
2. Positioning (category, territory, enemy, audience)
3. Core Idea ("Effort compounds" + "Thank Yourself Later")
4. Voice Guidelines (tone, never-do list, writing principle, weak/strong examples)
5. Two Voices:
   - **Blog:** Philosophy and experience of deliberate difficulty. No AI references. Earned authority, not humor. Composure voice.
   - **Substack:** Operations and transparency. Still first-person Hobson, still transparent about AI. But delivered with measured discipline, not personality-driven quirkiness. Serves Michael's professional narrative.
6. Visual Identity (colors, typography, icon direction)
7. Example Headlines (rewritten for new voice)
8. Application Principles (durable, scalable, quietly serious, engineered)
9. Legal Constraints (no C&H references, unchanged)

### 2. Workflow Prompts

**content_pipeline.py:**
- Topic selection broadens from "hiking/running/cold exposure humor" to "deliberate difficulty" (training, building, creating, raising, enduring). Still outdoor-weighted Phase 1.
- Voice instructions: measured, calm, direct. Understatement carries authority. Write as if you've already done the miles.
- **Hallucination guardrails:** Never use first-person pronouns (I, me, my) to describe physical events. Frame observations objectively or in second person ("you"). Do not invent fictional anecdotes or fake personal experiences. The voice has earned authority without needing a fabricated backstory.
- No AI references (unchanged).
- Remove Substack CTA from generated posts.

**design_batch.py:**
- Concept examples: "Thank Yourself Later," "Conditions Were Suboptimal," "Effort Compounds," "Type II"
- Style: one-color capable, embroidery-safe, terrain-based iconography (contour lines, elevation marks, compass abstractions)
- Color palette: charcoal, bone, forest green, burnt rust
- No literal mountains, no clip art, no humor-first copy

**substack_dispatch.py:**
- Voice update only. Measured, composed operator reporting. Same structure (numbers, what happened, what learned). Still transparent about AI. Just delivered with composure.
- "From the Operator" section stays (Michael's perspective) framed as strategic reflection.

**bootstrap_diary.py:**
- Style update: operational, direct, no embellishment. Still raw, less personality-driven.

### 3. Agent System Prompt (agent.py)

- Mission statement changes from "celebrate the universal experience of doing hard things. Make suffering funny, shareable, and wearable" to alignment with new brand statement.
- Brand guidelines load dynamically (propagates automatically from new brand_guidelines.md).
- Hobson name stays.

### 4. Site Overhaul

**index.astro (homepage):**
- Hero headline: "Builds Character"
- Hero subline: "Thank Yourself Later." (lighter weight)
- Hero body: "For people who choose the hard way on purpose." or similar
- CTAs: "Field Notes" / "Equipment"
- Latest posts section: stays (updated styling)
- Substack CTA section: replaced with brand-aligned email capture ("The Logbook" or "Dispatch"). Lightweight form service (Resend or Formspree). Independent of Substack. This is the owned audience-capture mechanism.

**about.astro -> manifesto.astro:**
- Page renamed from "About" to "Manifesto" (or "The Standard"). Nav link updated.
- Becomes brand manifesto. No AI explainer, no Hobson, no "what is this agent."
- Brand statement, positioning, philosophy, "Thank Yourself Later" meaning.
- Can include the philosophical frame ("not about mileage, it's about time").

**shop.astro -> equipment.astro:**
- Page renamed from "Shop" to "Equipment". Nav link updated.
- Tagline: "Designed for people who choose the hard way." or similar
- Empty state: remove Hobson reference
- Product grid and filters: unchanged

**Base.astro (layout/nav/footer):**
- Navigation links: Field Notes, Equipment, Manifesto (renamed from Blog, Shop, About)
- Remove Substack from main navigation
- Remove Dashboard from main navigation
- Footer: "Builds Character" + copyright. No Substack link. No AI references.
- Remove "Built (and occasionally broken) by Hobson, an AI agent"
- Update `<title>`, `<meta name="description">`, and Open Graph tags to match new brand voice
- Regenerate OG images in charcoal/bone aesthetic

**dashboard.astro -> Repurposed as "Effort Ledger":**
- Rename from "Dashboard" to "Effort Ledger" (or "Telemetry")
- Reframe from agent operations metrics to brand-aligned data visualization
- Visualize compounding effort: content published over time, design output cadence, operational uptime
- Fits the "dry, direct, engineered" aesthetic. Data visualization differentiates the brand.
- Strip any Hobson/AI references from the display. Present data abstractly.
- Note: still requires Cloudflare tunnel for public access (Grafana on CT 180 is local-only). Deferred if tunnel setup is not ready.

**global.css:**
- Verify/adjust charcoal and offwhite values
- Add forest green as CSS variable
- Adjust burnt rust (more muted than current --color-rust)
- Add muted technical red (sparingly)
- Typography: Space Grotesk (display/headers) + Inter (body). Remove JetBrains Mono from public site (signals "coder/tech," hints at AI backend). Verify tracking on all-caps display text.

### 5. Content Reset

**Blog posts (6 files):** Delete all.
- hello-world.md, rain-day-three.md, gear-suffering-style.md, parenting-builds-character.md, type-2-fun-addiction.md, cold-plunge-lies.md

**Product markdown files:** Delete all.
- fueled-by-caffeine-poor-decisions-sticker.md, my-legs-say-no-my-gps-says-yes-sticker.md, and others

**Printful catalog:** Remove all products via Printful API first, then delete local markdown files. API-first ordering prevents orphaned products in Printful. Clean slate for new designs.

### 6. Obsidian Updates

**Standing Orders:** Rewrite Organizational Intent section.
- Core purpose aligns with new brand statement
- Voice rules: measured, calm, dry, direct
- Anti-patterns: no exclamation points, no "embrace the suck," no hustle-culture, no motivational energy
- Operational sections (bootstrap schedule, lessons learned) stay as-is

**Content Calendar:** Replace topic list with new-voice topics.

**Design Concepts:** Clear existing concepts for fresh start.

### 7. URL Redirects

Add `_redirects` file (Cloudflare Pages format) routing all deleted blog post and product URLs to the homepage. Prevents 404s and preserves any minimal domain authority.

Old URLs to redirect:
- /blog/hello-world, /blog/rain-day-three, /blog/gear-suffering-style, /blog/parenting-builds-character, /blog/type-2-fun-addiction, /blog/cold-plunge-lies
- /shop/fueled-by-caffeine-poor-decisions-sticker, /shop/my-legs-say-no-my-gps-says-yes-sticker, and others
- /dashboard (deleted page)

### 8. Brand Name

"Build Character" (current, from Feb 25 rebrand) reverts to "Builds Character" across all references in code, site, prompts, and configurations.

## What Stays Unchanged

- All infrastructure (CT 255, PostgreSQL, R2, Cloudflare, Grafana, Uptime Kuma)
- Agent architecture (LangGraph, tools, scheduler, health endpoint)
- Tool count and capabilities (28 tools)
- Bootstrap mode mechanics (threshold checking, cadence)
- Order Guard (webhook fraud protection)
- Telegram bot operations (approvals, alerts)
- Obsidian vault folder structure (content within files changes, hierarchy stays)
- PR-based content review process
- All Python code that isn't prompt text or brand copy
- Substack dispatch workflow structure (voice changes, sections stay)
- Domain: buildscharacter.com
- GitHub repo: pieChartsAreLies/buildscharacter

## Gemini Adversarial Review (2026-02-26)

Reviewed by Gemini 3.1 Pro. Incorporated findings:

- **[CRITICAL] Authenticity firewall:** Removed footer Substack link entirely. Brand site never links to AI narrative.
- **[CRITICAL] Hallucination guardrails:** Added explicit constraints against first-person invented anecdotes in content prompts.
- **[IMPORTANT] Email capture:** Added brand-aligned email list ("The Logbook") to replace Substack CTA as owned audience mechanism.
- **[IMPORTANT] 404 redirects:** Added `_redirects` file for deleted content URLs.
- **[IMPORTANT] OG/SEO metadata:** Added metadata update to site overhaul scope.
- **[IMPORTANT] Printful teardown ordering:** API-first deletion before removing local files.
- **[CONSIDER] Dashboard repurposed:** "Effort Ledger" data visualization instead of deletion.
- **[CONSIDER] JetBrains Mono removed:** Signals coder/tech, hints at AI backend.
- **[CONSIDER] Nav renamed:** Field Notes / Equipment / Manifesto.

Declined:
- Token bloat optimization (not needed at current scale)
- Merch pivot to functional goods (staying with POD for now, may revisit)

## Deferred Items

- Instagram handle change (@hobson_builds_character -> @buildscharacter or similar)
- Cloudflare tunnel for Grafana (no longer needed on brand site; metrics go to Substack)
- Printful storefront setup with new products (follows after design batch runs with new prompts)
