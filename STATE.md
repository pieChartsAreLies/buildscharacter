# State

## Current Focus

Phase 1 and Phase 3 (core agent) complete. Hobson service running on CT 255. Ready for Phase 2 (website) and Phase 4+ (content/merch/analytics workflows).

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
- [ ] Phase 2: Site built and deployed
- [x] Phase 3: Core agent built and running
  - [x] Database client (db.py) with run logging, cost tracking, metrics
  - [x] Obsidian API tool (5 functions: write, read, append, daily log, list)
  - [x] Telegram bot integration (send message, alert, approval request)
  - [x] LangGraph agent (create_react_agent with Claude Sonnet, 8 tools)
  - [x] Health endpoint (FastAPI /health on :8080)
  - [x] Scheduler (APScheduler with 5 cron workflows, circuit breaking)
  - [x] Main entry point (checkpointer + agent + scheduler + health)
  - [x] Systemd service (enabled, running, auto-restart)
  - [x] DB integration test passed (run log, decisions, costs, metrics)
  - [x] Health endpoint verified: {"status":"ok","agent":"hobson","version":"0.1.0"}
- [ ] Substack launched

## Infrastructure

| Component | Location | Status |
|-----------|----------|--------|
| Hobson service | CT 255, Loki, 192.168.2.232:8080 | Running (systemd) |
| PostgreSQL schema | CT 201, Freya, hobson schema | Applied (8 tables + checkpointer) |
| Obsidian vault | 98 - Hobson Builds Character/ | Created |
| Ollama | CT 205, 192.168.2.71:11434 | Verified reachable |
| Grafana | CT 180, 192.168.2.180:3000 | Existing, dashboard TBD |
| Uptime Kuma | CT 182 | Existing, monitors TBD |

## Known Issues

- Overseerr Cloudflare tunnel currently on buildscharacter.com; needs to move to subdomain before site goes live
- Claude Max quota shared with Bob and Tim; monitor for rate limiting
- Substack has no public API; python-substack (reverse-engineered) is fragile
- Telegram chat ID not yet configured (need to create group and get ID)
- No ANTHROPIC_API_KEY in .env yet; agent will fail on Claude calls until configured
- Obsidian API key not yet in .env; Obsidian tools will fail until configured

## Next Steps

1. Phase 2: Build the Astro website (Tasks 6-7 in plan)
2. Phase 4: Content pipeline (Tasks 15-16 in plan)
3. Phase 5: Merch pipeline (Tasks 17-18 in plan)
4. Configure remaining API keys in .env (Anthropic, Obsidian, Telegram chat ID)
5. Set up Uptime Kuma monitors for Hobson
