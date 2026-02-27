# BuildsCharacter.com + Hobson

## Goal

Build and operate an endurance-minded philosophy brand on buildscharacter.com for people who choose the hard way on purpose. Composure-driven voice (measured, calm, dry, direct). Operated by an autonomous AI agent (Hobson) built on LangGraph. The brand site is a standalone business; the Substack is a separate technical build log serving Michael's professional narrative. Revenue through POD merch, content, and eventual digital products.

## Tech Stack

- **Site:** Astro or Next.js on Cloudflare Pages
- **Merch:** Printful API (zero inventory, auto-fulfilled)
- **Agent:** Python + LangGraph (monolithic first, extract sub-agents after stability) on LXC container (Loki)
- **LLMs:** Claude Max (high-judgment), Gemini (low-stakes), Ollama CT 205 (trivial tasks)
- **MCP Tools:** Printful, social media, Obsidian REST API, Git, Umami, image generation, Substack
- **State:** PostgreSQL (CT 201) with execution trace logging
- **Human interface:** Telegram bot (approvals, alerts) + PR-based review (content editing)
- **Documentation:** Obsidian vault (`98 - Hobson Builds Character/`)
- **Newsletter:** Substack (hobsonbuildscharacter.substack.com)
- **Email Capture:** Formspree ("The Logbook")
- **Analytics:** Cloudflare Analytics + Grafana (CT 180)
- **Monitoring:** Uptime Kuma (self-hosted)
- **DNS/CDN:** Cloudflare
- **Secrets:** Bitwarden

## Architecture

Hobson starts as a monolithic LangGraph agent that adds capabilities incrementally (blog drafting -> design generation -> analytics -> Substack). Sub-agents extracted only after complexity demands it. APScheduler triggers workflows on cron. MCP tools provide external service access. PostgreSQL stores state, metrics, decisions, and immutable execution traces. Telegram for approvals and alerts. PR-based workflow for content review. Uptime Kuma for health monitoring. Grafana for public transparency dashboard.

## Constraints

- $2,000 total budget for year one (~$600-1,200 expected spend, rest in reserve)
- No Calvin and Hobbes imagery, characters, or direct references in any commercial context
- No Shopify until revenue exceeds $2K/mo
- No ad spend until organic channels validate what resonates
- All spending requires human approval via Telegram + programmatic cost controls
- Blog content requires human experience layer (not pure AI) for Google E-E-A-T, but pipeline designed for graceful degradation without human input
- Single audience focus (outdoor/endurance) in Phase 1. Expand from data, not assumptions.

## Decisions Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-02-23 | Content + Merch model over SaaS or pure affiliate | Best budget fit, automation potential, diversified revenue, exit value |
| 2026-02-23 | Cloudflare Pages + Printful over Shopify | Saves $468/year. Shopify at scale, not at launch |
| 2026-02-23 | AI design generation over Fiverr | Saves $400-500. Modern AI tools are sufficient |
| 2026-02-23 | Agent name: Hobson | Independent name, avoids C&H IP proximity, own cultural reference |
| 2026-02-23 | LangGraph over n8n | Code-first agent framework, not visual workflow editor |
| 2026-02-23 | Obsidian vault for transparency | Full audit trail of every decision and action |
| 2026-02-23 | Substack as primary product | Narrative IS the product. Merch/blog are proof-of-work. |
| 2026-02-23 | Incremental agent build | Monolithic first. Extract sub-agents after stability. |
| 2026-02-23 | PR-based content review | Telegram for approvals, PRs for editing. Async, inline comments. |
| 2026-02-23 | Claude Max + Gemini + Ollama | Tiered LLM strategy. Eliminates API costs. |
| 2026-02-23 | Uptime Kuma + Grafana | Homelab-first monitoring and public transparency dashboard |
| 2026-02-23 | Single audience first | Outdoor/endurance. Expand from data, not assumptions. |
| 2026-02-23 | Reader voting in Substack | Community-driven priorities. Subscribers as co-conspirators. |
| 2026-02-23 | The Hobson Playbook | Endgame product. Capture meta-learnings from day one. |
| 2026-02-23 | Execution trace logging | Immutable run_log for debugging autonomous operations |
| 2026-02-23 | Programmatic cost controls | Per-action logging, daily caps, single-action thresholds |
| 2026-02-26 | Brand pivot: humor to composure | Full reset from "funny suffering" to composure-driven philosophy brand. Voice: measured, calm, dry, direct. Tagline: "Thank Yourself Later." |
| 2026-02-26 | Decouple Substack from brand site | Brand site never links to Substack. Complete firewall between brand and AI narrative. Substack is Michael's professional project, disposable if brand succeeds. |
| 2026-02-26 | Nav renamed: Field Notes / Equipment / Manifesto | Blog -> Field Notes, Shop -> Equipment, About -> Manifesto. Dashboard removed. |
| 2026-02-26 | Email capture via Formspree ("The Logbook") | Owned audience mechanism. Independent of Substack. AJAX form on homepage. |
| 2026-02-26 | All old content deleted | 6 blog posts + 2 product files removed. Clean slate for composure brand. Git tag v1.0-humor-legacy preserves old state. |
| 2026-02-27 | Routes renamed: Journal / Shop / Manifesto | "Field Notes" and "Equipment" were outdoor-coded language. Universal alternatives for broader audience. |
| 2026-02-27 | Site visual redesign via Lovable prototype | A24/Kinfolk aesthetic: noise + topo textures, alternating dark/light sections, typography-driven, full-bleed hero. Ported from React/Tailwind v3 prototype to Astro/Tailwind v4. |
| 2026-02-27 | Hobson repositioned: autonomous operator with human oversight | Genuine operational autonomy (picks topics, generates designs, makes tactical decisions). Michael holds strategic direction, editorial veto, brand authority. Governance boundary IS the experiment. |
| 2026-02-27 | Substack dual-voice structure | Michael 60-70% (strategic frame), Hobson 30-40% (operational report), plus "The Numbers" and "The Cutting Room Floor" sections. 48-hour fallback: Hobson publishes solo if Michael doesn't complete his frame. |
| 2026-02-27 | Brand/audience widened | No longer outdoor/endurance-only. Targeting anyone who embraces deliberate difficulty: training, parenting, entrepreneurship, creative work, recovery. |
