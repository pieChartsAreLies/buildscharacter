# State

## Current Focus

Phases 1-6 complete. Hobson service running on CT 255 with Gemini 2.5 Flash (18 tools). All 5 scheduled workflows have structured prompts. Site live on buildscharacter.com. Ready for Phase 7 (Substack integration).

## Status

- [x] Business model selected (Content + Merch)
- [x] Agent architecture designed (LangGraph + MCP tools)
- [x] Budget allocated ($600-1,200 of $2,000, rest in reserve)
- [x] Design document written and approved (revised after Gemini adversarial review)
- [x] Implementation plan created (26 tasks, 10 phases)
- [x] Homelab documentation written and published
- [x] Prerequisites completed (Telegram bot, Printful, Substack, Instagram)
- [x] Phase 1: Infrastructure provisioned
  - [x] Python project scaffolded (hobson/ with LangGraph stack)
  - [x] Brand guidelines written (brand/brand_guidelines.md)
  - [x] PostgreSQL schema applied (8 tables + checkpointer tables, hobson schema on CT 201)
  - [x] LXC container provisioned (CT 255 on Loki, 192.168.2.232, Python 3.11)
  - [x] Obsidian vault created (98 - Hobson Builds Character/, 19 files)
- [x] Phase 2: Site built and live
  - [x] Astro 5 site scaffolded with Tailwind v4, sitemap
  - [x] 6 pages: home, blog, shop (placeholder), dashboard (placeholder), about
  - [x] Content collections (blog) with hello-world sample post
  - [x] Code pushed to GitHub (pieChartsAreLies/buildscharacter, public)
  - [x] Cloudflare Pages connected and deploying
  - [x] Custom domain configured (buildscharacter.com)
- [x] Phase 3: Core agent built and running
  - [x] Database client (db.py) with run logging, cost tracking, metrics
  - [x] Obsidian API tool (5 functions: write, read, append, daily log, list)
  - [x] Telegram bot integration (send message, alert, approval request)
  - [x] LangGraph agent (create_react_agent with Gemini 2.5 Flash)
  - [x] Health endpoint (FastAPI /health on :8080)
  - [x] Scheduler (APScheduler with 5 cron workflows, circuit breaking)
  - [x] Systemd service (enabled, running, auto-restart)
- [x] Phase 4: Content pipeline built
  - [x] Git operations tool (git_ops.py) using GitHub REST API
  - [x] Content pipeline workflow prompt (content_pipeline.py)
  - [x] Content Calendar populated in Obsidian
- [x] Phase 5: Merch pipeline built
  - [x] Printful API tool (5 functions: list catalog, get variants, upload file, create product, list store)
  - [x] Design batch workflow prompt (design_batch.py)
- [x] Phase 6: Analytics & reporting built
  - [x] Cloudflare Analytics tool (3 functions: site stats, top pages, top referrers)
  - [x] Replaced planned Umami with Cloudflare GraphQL API (no new service needed)
  - [x] Morning briefing workflow prompt (morning_briefing.py)
  - [x] Weekly business review workflow prompt (business_review.py)
  - [x] Agent updated to 18 tools
  - [x] All 5 scheduler jobs use structured prompts
  - [x] Config updated with cloudflare_api_token and cloudflare_zone_id
- [x] Substack launched
  - [x] First post published: "I Was Built to Sell Stickers. Here's My Plan."

## Infrastructure

| Component | Location | Status |
|-----------|----------|--------|
| Hobson service | CT 255, Loki, 192.168.2.232:8080 | Running (systemd, Gemini 2.5 Flash) |
| PostgreSQL schema | CT 201, Freya, hobson schema | Applied (8 tables + checkpointer) |
| Obsidian vault | 98 - Hobson Builds Character/ | Created (19+ files) |
| Ollama | CT 205, 192.168.2.71:11434 | Verified reachable |
| Grafana | CT 180, 192.168.2.180:3000 | Existing, dashboard TBD |
| Uptime Kuma | CT 182 | Existing, monitors TBD |
| GitHub repo | pieChartsAreLies/buildscharacter | Public, master + feature branch |
| Cloudflare Pages | buildscharacter.com | Live |
| Substack | buildscharacter.substack.com | First post published |

## Known Issues

- Substack has no public API; python-substack (reverse-engineered) is fragile
- GitHub token on CT 255 is a gho_ OAuth token (may expire); should replace with a fine-grained PAT
- Google API key passed explicitly to ChatGoogleGenerativeAI (pydantic-settings doesn't set env vars)
- Cloudflare API token and zone ID not yet added to CT 255 .env (need to create token in CF dashboard)

## Next Steps

1. Phase 7: Substack integration (Tasks 22-23)
2. Phase 8: Grafana dashboard (Task 24)
3. Phase 9: Uptime Kuma monitors (Task 25)
4. Phase 10: Final deployment and systemd verification (Task 26)
5. Create Cloudflare API token (Analytics:Read) and add to CT 255 .env
