# State

## Current Focus

All 10 phases complete, branch merged to master. Hobson service running on CT 255 with Gemini 2.5 Flash (21 tools, 5 scheduled workflows). Site live on buildscharacter.com. First week of autonomous operation starting.

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
  - [x] Astro 5 site on Cloudflare Pages (buildscharacter.com)
- [x] Phase 3: Core agent built and running
  - [x] DB client, Obsidian tool, Telegram bot, LangGraph agent, health endpoint
  - [x] Scheduler with 5 cron workflows, circuit breaking
  - [x] Systemd service (enabled, running, auto-restart)
- [x] Phase 4: Content pipeline built
  - [x] Git operations tool, content pipeline workflow, content calendar
- [x] Phase 5: Merch pipeline built
  - [x] Printful API tool (5 functions), design batch workflow
- [x] Phase 6: Analytics & reporting built
  - [x] Cloudflare Analytics tool (3 functions, replaced planned Umami)
  - [x] Morning briefing workflow, weekly business review workflow
  - [x] CF API token configured on CT 255
- [x] Phase 7: Substack integration built
  - [x] Substack tool (3 functions: create draft, publish, list posts)
  - [x] Cookie-based auth with fallback to Obsidian on auth failure
  - [x] Content hash signing on all drafts
  - [x] Weekly Substack dispatch workflow (Friday 3pm ET)
  - [x] Agent updated to 21 tools
- [x] Substack launched
  - [x] First post published: "I Was Built to Sell Stickers. Here's My Plan."
- [x] Phase 8: Grafana dashboard provisioned
  - [x] Service account + API token created
  - [x] Hobson PostgreSQL data source added
  - [x] 9-panel dashboard (operations, success rate, costs, content/designs/decisions, goals)
  - [x] Anonymous access + embedding enabled in grafana.ini
  - [x] Dashboard iframe embedded in site dashboard.astro
  - [x] Note: local-only, needs CF tunnel for public access
- [x] Phase 9: Uptime Kuma monitors configured
  - [x] 5 push monitors (one per workflow) with per-workflow push URLs
  - [x] 1 HTTP health monitor (CT 255:8080/health)
  - [x] Push URLs configured in CT 255 .env and scheduler.py
- [x] Phase 10: Final deployment verification
  - [x] Service: active (running), 106.4MB memory
  - [x] Health endpoint: OK
  - [x] Scheduler: 5 jobs started
  - [x] All 21 tools verified loading

## Infrastructure

| Component | Location | Status |
|-----------|----------|--------|
| Hobson service | CT 255, Loki, 192.168.2.232:8080 | Running (systemd, 21 tools) |
| PostgreSQL schema | CT 201, Freya, hobson schema | Applied (8 tables + checkpointer) |
| Obsidian vault | 98 - Hobson Builds Character/ | Created (19+ files) |
| Grafana | CT 180, 192.168.2.180:3000 | Dashboard live (9 panels, anon access) |
| Uptime Kuma | CT 182, 192.168.2.182:3001 | 6 monitors (5 push + 1 HTTP) |
| GitHub repo | pieChartsAreLies/buildscharacter | Public |
| Cloudflare Pages | buildscharacter.com | Live |
| Cloudflare Analytics | Zone ecdc733... | Token configured |
| Substack | buildscharacter.substack.com | First post published |

## Known Issues

- Telegram bot is outbound-only (no polling/webhook for receiving messages or approval button callbacks)
- Substack cookies expire periodically; need manual refresh in .env
- GitHub token on CT 255 is a gho_ OAuth token (may expire)
- Google API key passed explicitly to ChatGoogleGenerativeAI
- Grafana admin password was reset to temppass123 during setup; change it back and update Bitwarden
- Grafana dashboard is local-only (192.168.2.180); needs Cloudflare tunnel for public access on buildscharacter.com/dashboard

## Next Steps

1. Monitor first full week of scheduled workflows, tune prompts
2. Implement Telegram inbound polling (receive messages, handle approval callbacks)
3. Set up Cloudflare tunnel for Grafana public dashboard
4. Seed content calendar with blog post ideas
5. Create first merch designs for Printful
