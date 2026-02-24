# State

## Current Focus

Phases 1-5 complete. Hobson service running on CT 255 with Gemini 2.5 Flash (15 tools). Site live on buildscharacter.com. Substack launched. Merch pipeline tools built. Ready for Phase 6 (analytics & reporting).

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
  - [x] Build verified (all pages compile cleanly)
  - [x] Code pushed to GitHub (pieChartsAreLies/buildscharacter, public)
  - [x] PR #1 merged to master
  - [x] Cloudflare Pages connected and deploying
  - [x] Custom domain configured (buildscharacter.com)
- [x] Phase 3: Core agent built and running
  - [x] Database client (db.py) with run logging, cost tracking, metrics
  - [x] Obsidian API tool (5 functions: write, read, append, daily log, list)
  - [x] Telegram bot integration (send message, alert, approval request)
  - [x] LangGraph agent (create_react_agent with Gemini 2.5 Flash)
  - [x] Health endpoint (FastAPI /health on :8080)
  - [x] Scheduler (APScheduler with 5 cron workflows, circuit breaking)
  - [x] Main entry point (checkpointer + agent + scheduler + health)
  - [x] Systemd service (enabled, running, auto-restart)
  - [x] DB integration test passed (run log, decisions, costs, metrics)
  - [x] Health endpoint verified: {"status":"ok","agent":"hobson","version":"0.1.0"}
  - [x] Telegram test message sent to Hobson's Folly group
  - [x] CT 255 repo converted from manual push to proper git clone
- [x] Phase 4: Content pipeline built
  - [x] Git operations tool (git_ops.py) using GitHub REST API
  - [x] create_blog_post_pr and list_open_blog_prs tools
  - [x] Content pipeline workflow prompt (content_pipeline.py)
  - [x] Scheduler wired to structured content pipeline prompt
  - [x] Content Calendar populated in Obsidian (7 planned topics + backlog)
  - [x] Code deployed to CT 255, service running
- [x] Phase 5: Merch pipeline built
  - [x] Printful API tool (5 functions: list catalog, get variants, upload file, create product, list store)
  - [x] Design batch workflow prompt (design_batch.py)
  - [x] Agent updated to 15 tools (added 5 Printful tools)
  - [x] Scheduler wired to structured design batch prompt
  - [ ] Code deployed to CT 255
- [x] Substack launched
  - [x] First post published: "I Was Built to Sell Stickers. Here's My Plan."
  - [x] source-sha256: 2511156213db3ef3a041a7c2cb22b22e87e4d8e33e3013e20abb2a6b98d2b74c

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
- Phase 5 code not yet deployed to CT 255 (needs git pull + service restart)

## Next Steps

1. Deploy Phase 5 code to CT 255
2. Phase 6: Analytics & Reporting (Tasks 19-21)
3. Phase 7: Substack integration (Tasks 22-23)
4. Phase 8: Grafana dashboard (Task 24)
5. Phase 9: Uptime Kuma monitors (Task 25)
6. Phase 10: Final deployment and systemd verification (Task 26)
