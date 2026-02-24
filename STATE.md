# State

## Current Focus

Phase 1 complete. Infrastructure provisioned and verified. Ready for Phase 2 (website) and Phase 3 (core agent).

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
  - [x] PostgreSQL schema applied (8 tables, hobson schema on CT 201)
  - [x] LXC container provisioned (CT 255 on Loki, 192.168.2.232, Python 3.11)
  - [x] Obsidian vault created (98 - Hobson Builds Character/, 19 files)
- [ ] Phase 2: Site built and deployed
- [ ] Phase 3: Hobson agent built and running
- [ ] Substack launched

## Infrastructure

| Component | Location | Status |
|-----------|----------|--------|
| Hobson container | CT 255, Loki, 192.168.2.232 | Running |
| PostgreSQL schema | CT 201, Freya, hobson schema | Applied (8 tables) |
| Obsidian vault | 98 - Hobson Builds Character/ | Created |
| Ollama | CT 205, 192.168.2.71:11434 | Verified reachable |
| Grafana | CT 180, 192.168.2.180:3000 | Existing, dashboard TBD |
| Uptime Kuma | CT 182 | Existing, monitors TBD |

## Known Issues

- Overseerr Cloudflare tunnel currently on buildscharacter.com; needs to move to subdomain before site goes live
- Claude Max quota shared with Bob and Tim; monitor for rate limiting
- Substack has no public API; python-substack (reverse-engineered) is fragile
- Telegram chat ID not yet configured (need to create group and get ID)
- Debian 12 ships Python 3.11 (not 3.12); requirement relaxed, no issues
- python-substack latest is 0.1.17 (not 0.2); version pin corrected

## Next Steps

1. Phase 2: Build the Astro website (Tasks 6-7)
2. Phase 3: Build core agent (Tasks 8-14)
3. Phases 2 and 3 can run in parallel per the dependency graph
