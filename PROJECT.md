# BuildsCharacter.com + Hobson

## Goal

Build a profitable, largely autonomous web business on buildscharacter.com (content-driven brand + POD merch), operated by an autonomous AI agent named Hobson built on LangGraph. The Substack newsletter is the primary product; merch and blog are proof-of-work for the narrative. Hobson documents everything transparently in Obsidian and publishes a public Grafana dashboard. The endgame is "The Hobson Playbook," productizing the agent system and learnings.

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
- **Analytics:** Umami (self-hosted) + Grafana (public dashboard, CT 180)
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
