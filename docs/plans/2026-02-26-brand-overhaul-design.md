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
3. **Subtle footer link only** connects the site to Substack. No CTA, no explanation. Just a quiet text link for the curious.
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
- CTAs: "Read" / "Shop"
- Latest posts section: stays (updated styling)
- Substack CTA section: removed entirely

**about.astro:**
- Becomes brand manifesto. No AI explainer, no Hobson, no "what is this agent."
- Brand statement, positioning, philosophy, "Thank Yourself Later" meaning.
- Can include the philosophical frame ("not about mileage, it's about time").

**shop.astro:**
- Tagline: "Designed for people who choose the hard way." or similar
- Empty state: remove Hobson reference
- Product grid and filters: unchanged

**Base.astro (layout/nav/footer):**
- Remove Substack from main navigation
- Remove Dashboard from main navigation
- Footer: "Builds Character" + copyright + subtle "How this was built" text link to Substack
- Remove "Built (and occasionally broken) by Hobson, an AI agent"

**dashboard.astro:**
- Delete page entirely. Metrics published on Substack instead.

**global.css:**
- Verify/adjust charcoal and offwhite values
- Add forest green as CSS variable
- Adjust burnt rust (more muted than current --color-rust)
- Add muted technical red (sparingly)
- Typography: Inter/Space Grotesk/JetBrains Mono likely work as-is (clean geometric sans serif). Verify tracking on all-caps display text.

### 5. Content Reset

**Blog posts (6 files):** Delete all.
- hello-world.md, rain-day-three.md, gear-suffering-style.md, parenting-builds-character.md, type-2-fun-addiction.md, cold-plunge-lies.md

**Product markdown files:** Delete all.
- fueled-by-caffeine-poor-decisions-sticker.md, my-legs-say-no-my-gps-says-yes-sticker.md, and others

**Printful catalog:** Remove all products (4 currently). Clean slate for new designs.

### 6. Obsidian Updates

**Standing Orders:** Rewrite Organizational Intent section.
- Core purpose aligns with new brand statement
- Voice rules: measured, calm, dry, direct
- Anti-patterns: no exclamation points, no "embrace the suck," no hustle-culture, no motivational energy
- Operational sections (bootstrap schedule, lessons learned) stay as-is

**Content Calendar:** Replace topic list with new-voice topics.

**Design Concepts:** Clear existing concepts for fresh start.

### 7. Brand Name

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

## Deferred Items

- Instagram handle change (@hobson_builds_character -> @buildscharacter or similar)
- Cloudflare tunnel for Grafana (no longer needed on brand site; metrics go to Substack)
- Printful storefront setup with new products (follows after design batch runs with new prompts)
