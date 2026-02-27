# State

## Current Focus

Brand overhaul complete. Pivoted from humor-first "funny suffering" to composure-driven philosophy brand. All content deleted, site redesigned, prompts rewritten, Obsidian updated. Needs deploy to CT 255 and Cloudflare Pages rebuild. Bootstrap Sprint still active (BOOTSTRAP_MODE=true) for new content generation under the composure voice.

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
- [x] Telegram conversational capability
  - [x] PTB polling for inbound messages + callback buttons
  - [x] Message history in PostgreSQL (hobson.messages table)
  - [x] Approval persistence in PostgreSQL (hobson.approvals table)
  - [x] Standing Orders learning mechanism (Obsidian + confirmation flow)
  - [x] Chat authorization (only responds to configured chat_id)
  - [x] Agent updated to 22 tools (added send_standing_order_proposal)
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
- [x] Bootstrap Sprint activated (2026-02-24)
  - [x] BOOTSTRAP_MODE=true in .env, service restarted
  - [x] Scheduler: 8 jobs (3x content, daily diary, daily designs, morning briefing, Substack, business review)
  - [x] publish_blog_post tool with pre-flight validation (slug, title, desc, tags, 250-word min)
  - [x] Code-level tool selection (bootstrap gets publish_blog_post, steady-state gets create_blog_post_pr)
  - [x] Bootstrap diary workflow (daily 9pm ET, operational summary as blog content)
  - [x] Design batch bootstrap variant (create Printful drafts, skip approval)
  - [x] Threshold checking (10+ posts AND 15+ products triggers Telegram notification to switch)
  - [x] Content calendar expanded to 22 topics (listicles, gear, humor, meta/transparency)
- [x] Image Generation Integration (2026-02-24)
  - [x] Gemini Imagen 4.0 (`imagen-4.0-generate-001`) via google-genai SDK
  - [x] 4 candidates per concept, Gemini Flash vision ranking for best selection
  - [x] Cloudflare R2 storage (bucket: hobson-designs, UUID-prefixed filenames)
  - [x] PostgreSQL `hobson.design_generations` table (provenance tracking)
  - [x] Auto-upload to R2 during generation (avoids base64 context window bloat)
  - [x] generate_design_image + upload_to_r2 tools registered in agent
  - [x] Design batch workflow updated with structured prompt template
  - [x] First successful end-to-end run: 5 concepts, 3 images, 3 Printful products created

- [x] Shop Overhaul + "Build Character" Rebrand (2026-02-25)
  - [x] Rebranded "This Builds Character" to "Build Character" across brand guidelines, prompts, and site
  - [x] Removed all existing products (3 mugs, 1 t-shirt) for sticker-first relaunch
  - [x] Added LANCZOS auto-upscaling in image_gen.py (1024->1500+ for stickers)
  - [x] Added Printful Mockup Generator integration (get_mockup_styles, generate_product_mockup)
  - [x] Registered 2 new tools in agent (24 -> 26 tools)
  - [x] Updated design batch workflow with mockup generation step
  - [x] 25/25 tests passing

- [x] Visibility & Cleanup Sprint (2026-02-26)
  - [x] publish_product tool added to git_ops.py (writes product markdown to site repo via GitHub API)
  - [x] get_pending_approvals tool added to telegram.py (queries unresolved approvals for morning briefing)
  - [x] Registered 2 new tools in agent (26 -> 28 tools)
  - [x] Backfilled product markdown for 4 existing Printful products (shop page now displays them)
  - [x] Design batch workflow updated to use publish_product (future products auto-publish to site)
  - [x] Morning briefing enhanced with structured Telegram daily digest (schedule, approvals, output, attention items)
  - [x] Confirmed Telegram inbound polling is working (messages received, approval callbacks functional)
  - [x] Obsidian Task Dashboard expanded with per-project sections (#BuildsCharacter, #NanoClaw, etc.)
  - [x] Homelab-docs tasks migrated to tagged Obsidian tasks
  - [x] Hobson Task Queue cleaned up with #BuildsCharacter tags and Printful storefront checklist
  - [x] 38/38 tests passing
  - [x] Deployed to CT 255, service restarted

- [x] Order Guard (Fraud Protection, 2026-02-26)
  - [x] Fail-closed architecture: Printful holds drafts, service confirms safe orders
  - [x] FastAPI webhook service on CT 255, port 8100 (18 tests passing)
  - [x] Three rules: production cost cap ($50), per-item qty (3), hourly velocity (5)
  - [x] HMAC signature validation, async background processing, idempotent DB writes
  - [x] PostgreSQL `hobson.order_events` table on CT 201
  - [x] Telegram notifications for confirmed/held/error orders
  - [x] Cloudflare Tunnel: `webhooks.buildscharacter.com` -> CT 255:8100 (http2 protocol)
  - [x] Printful webhook configured for `order_created` events
  - [x] Systemd services: `order-guard.service` + `cloudflared.service`
  - [x] Homelab docs updated and published
  - [ ] Enable "Manually approve orders" in Printful dashboard (REQUIRED for fail-closed)
  - [ ] Add Uptime Kuma monitor for Order Guard health endpoint

- [x] Brand Overhaul: Composure Pivot (2026-02-26)
  - [x] Brand guidelines fully replaced (humor -> composure, "Thank Yourself Later" tagline)
  - [x] Agent system prompt updated (mission + voice)
  - [x] All 4 workflow prompts rewritten (content_pipeline, design_batch, substack_dispatch, bootstrap_diary)
  - [x] Site CSS: burnt rust, forest green, removed JetBrains Mono
  - [x] Layout/nav: Field Notes / Equipment / Manifesto, footer cleaned of AI references
  - [x] Homepage: "BUILDS CHARACTER" hero, "Thank Yourself Later", email capture ("The Logbook" via Formspree)
  - [x] Manifesto page (replaced About), Equipment page (replaced Shop)
  - [x] Blog routes moved to /field-notes/
  - [x] Dashboard page deleted
  - [x] All 6 blog posts deleted, all 2 product files deleted
  - [x] URL redirects: /blog/* -> /field-notes, /shop/* -> /equipment, /about -> /manifesto, /dashboard -> /
  - [x] git_ops.py: author changed from "Hobson" to "Builds Character"
  - [x] Obsidian Standing Orders: Organizational Intent rewritten for composure brand
  - [x] Obsidian Content Calendar: 8 new composure-voice topics, old content archived
  - [x] Git tag v1.0-humor-legacy preserved for rollback
  - [x] Design doc: docs/plans/2026-02-26-brand-overhaul-design.md
  - [x] Implementation plan: docs/plans/2026-02-26-brand-overhaul-plan.md
  - [x] 38/38 tests passing
  - [ ] Deploy to CT 255 (git pull + restart hobson service)
  - [ ] Verify Cloudflare Pages rebuild
  - [ ] Delete old Printful products (4 existing) via Printful dashboard
  - [ ] Set up Formspree form and replace PLACEHOLDER in index.astro

## Infrastructure

| Component | Location | Status |
|-----------|----------|--------|
| Hobson service | CT 255, Loki, 192.168.2.232:8080 | Running (BOOTSTRAP_MODE, 8 jobs, 28 tools) |
| Order Guard | CT 255, Loki, 192.168.2.232:8100 | Running (fail-closed webhook fraud protection) |
| CF Tunnel (order-guard) | webhooks.buildscharacter.com | Running (http2, 4 connections) |
| PostgreSQL schema | CT 201, Freya, hobson schema | Applied (11 tables + order_events + checkpointer) |
| Cloudflare R2 | hobson-designs bucket | Active (3 designs uploaded) |
| Obsidian vault | 98 - Hobson Builds Character/ | Created (19+ files) |
| Grafana | CT 180, 192.168.2.180:3000 | Dashboard live (9 panels, anon access) |
| Uptime Kuma | CT 182, 192.168.2.182:3001 | 6 monitors (5 push + 1 HTTP) |
| GitHub repo | pieChartsAreLies/buildscharacter | Public |
| Cloudflare Pages | buildscharacter.com | Live |
| Cloudflare Analytics | Zone ecdc733... | Token configured |
| Substack | buildscharacter.substack.com | First post published |

## Known Issues

- Synchronous DB calls in async Telegram handlers (sub-millisecond, acceptable at current scale, track for future pooling)
- Substack cookies expire periodically; need manual refresh in .env
- GitHub token on CT 255 is a gho_ OAuth token (may expire)
- Google API key passed explicitly to ChatGoogleGenerativeAI
- Grafana admin password was reset to temppass123 during setup; change it back and update Bitwarden
- Imagen outputs 1024x1024; auto-upscaled via LANCZOS to meet Printful minimums (e.g., 1500x1500 for stickers)
- Vision ranking occasionally falls back to first image on API errors (non-blocking)
- Formspree form ID is PLACEHOLDER in index.astro (needs real form created)
- Old Printful products (4) still exist; need manual deletion from Printful dashboard

## Next Steps

1. Deploy brand overhaul to CT 255 (git pull + restart hobson service)
2. Verify Cloudflare Pages rebuild (buildscharacter.com reflects new brand)
3. Delete old Printful products via Printful dashboard
4. Create Formspree form and replace PLACEHOLDER in site/src/pages/index.astro
5. Set retail prices in Printful for new products
6. Monitor morning briefing to verify Telegram daily digest format
7. Watch for threshold notification (10+ posts AND 15+ products), then set BOOTSTRAP_MODE=false and restart
8. Promote on Reddit/HN once content inventory is built
9. Restore Grafana admin password and update Bitwarden
10. Order a test sticker to verify LANCZOS upscale quality on physical product
11. Write first "From the Operator" Substack section (Michael's perspective on the brand pivot)
12. Change Instagram handle (@hobson_builds_character -> @buildscharacter or similar)
13. Design gap: approval callbacks flip DB flag but don't re-trigger workflow (approved work waits for next scheduled run)
