# State

## Current Focus

Phases 1, 2 (site scaffold), and 3 (core agent) complete. Hobson service running on CT 255 with Gemini 2.5 Flash. Code merged to master and pushed to GitHub. Cloudflare Pages deployment pending (manual dashboard setup).

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
- [x] Phase 2: Site built (deployment pending Cloudflare Pages setup)
  - [x] Astro 5 site scaffolded with Tailwind v4, sitemap
  - [x] 6 pages: home, blog, shop (placeholder), dashboard (placeholder), about
  - [x] Content collections (blog) with hello-world sample post
  - [x] Build verified (all pages compile cleanly)
  - [x] Code pushed to GitHub (pieChartsAreLies/buildscharacter)
  - [x] PR #1 merged to master
  - [ ] Cloudflare Pages connected (manual dashboard step)
  - [ ] Custom domain configured (buildscharacter.com)
- [x] Phase 3: Core agent built and running
  - [x] Database client (db.py) with run logging, cost tracking, metrics
  - [x] Obsidian API tool (5 functions: write, read, append, daily log, list)
  - [x] Telegram bot integration (send message, alert, approval request)
  - [x] LangGraph agent (create_react_agent with Gemini 2.5 Flash, 8 tools)
  - [x] Health endpoint (FastAPI /health on :8080)
  - [x] Scheduler (APScheduler with 5 cron workflows, circuit breaking)
  - [x] Main entry point (checkpointer + agent + scheduler + health)
  - [x] Systemd service (enabled, running, auto-restart)
  - [x] DB integration test passed (run log, decisions, costs, metrics)
  - [x] Health endpoint verified: {"status":"ok","agent":"hobson","version":"0.1.0"}
  - [x] Telegram test message sent to Hobson's Folly group
- [ ] Substack launched

## Infrastructure

| Component | Location | Status |
|-----------|----------|--------|
| Hobson service | CT 255, Loki, 192.168.2.232:8080 | Running (systemd, Gemini 2.5 Flash) |
| PostgreSQL schema | CT 201, Freya, hobson schema | Applied (8 tables + checkpointer) |
| Obsidian vault | 98 - Hobson Builds Character/ | Created (19 files) |
| Ollama | CT 205, 192.168.2.71:11434 | Verified reachable |
| Grafana | CT 180, 192.168.2.180:3000 | Existing, dashboard TBD |
| Uptime Kuma | CT 182 | Existing, monitors TBD |
| GitHub repo | pieChartsAreLies/buildscharacter | Code pushed, PR #1 merged |
| Cloudflare Pages | buildscharacter.com | Pending setup |

## Known Issues

- Substack has no public API; python-substack (reverse-engineered) is fragile
- Overseerr tunnel is on loki.buildscharacter.com (no conflict with root domain)

## Next Steps

1. Connect Cloudflare Pages to GitHub repo (manual dashboard step)
2. Phase 4: Content pipeline (Tasks 15-16 in plan)
3. Phase 5: Merch pipeline (Tasks 17-18 in plan)
4. Set up Uptime Kuma monitors for Hobson
5. Set up Grafana dashboard (Phase 8)
