# BuildsCharacter.com + Hobson

## Goal

Build a profitable, largely autonomous web business on buildscharacter.com (content-driven brand + POD merch), operated by an AI agent named Hobson who documents his work transparently in Obsidian and publishes a public Substack newsletter narrating the journey. The business is the product. The agent architecture is the engineering project. The Substack is the differentiator.

## Tech Stack

- **Site:** Astro or Next.js on Cloudflare Pages
- **Merch:** Printful API (zero inventory, auto-fulfilled)
- **Agent:** Python + LangGraph (supervisor + sub-agents) on LXC container
- **MCP Tools:** Printful, social media, Obsidian REST API, Excalidraw, Git, Umami, image generation, Substack
- **State:** PostgreSQL (CT 201)
- **Human interface:** Telegram bot (approvals, status updates)
- **Documentation:** Obsidian vault (`98 - Hobson Builds Character/`)
- **Newsletter:** Substack (hobsonbuildscharacter.substack.com)
- **Analytics:** Umami (self-hosted on homelab)
- **DNS/CDN:** Cloudflare

## Architecture

Hobson is a LangGraph supervisor agent with four sub-agents (Content, Design, Analytics, Operations). APScheduler triggers workflows on cron schedules. MCP tool servers provide access to external services. PostgreSQL stores state, metrics, and decisions. Telegram provides human-in-the-loop for spending and strategic decisions. Obsidian is the transparency layer. Substack is the public-facing journal.

## Constraints

- $2,000 total budget for year one
- No Calvin and Hobbes imagery, characters, or direct references in any commercial context
- No Shopify until revenue exceeds $2K/mo
- No ad spend until organic channels validate what resonates
- All spending requires human approval via Telegram
- Blog content requires human experience layer (not pure AI) for Google E-E-A-T compliance

## Decisions Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-02-23 | Content + Merch model over SaaS or pure affiliate | Best budget fit, automation potential, diversified revenue, exit value |
| 2026-02-23 | Cloudflare Pages + Printful over Shopify | Saves $468/year. Shopify at scale, not at launch |
| 2026-02-23 | AI design generation over Fiverr | Saves $400-500. Modern AI tools are sufficient |
| 2026-02-23 | Agent name: Hobson | Independent name, avoids C&H IP proximity |
| 2026-02-23 | LangGraph over n8n | Code-first agent framework, not visual workflow editor |
| 2026-02-23 | Obsidian vault for transparency | Full audit trail of every decision and action |
| 2026-02-23 | Substack as public journal | Content flywheel, revenue stream, meta-narrative differentiator |
