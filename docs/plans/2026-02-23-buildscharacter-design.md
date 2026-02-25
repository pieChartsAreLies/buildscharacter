# BuildsCharacter.com + Hobson: Design Document

**Date:** 2026-02-23
**Status:** Approved (revised after Gemini adversarial review)
**Budget:** $2,000

---

## Overview

Two deliverables, one project:

1. **buildscharacter.com** -- A content-driven brand and print-on-demand merch store celebrating the universal experience of "doing hard things"
2. **Hobson** -- An autonomous AI agent that operates the business, documents his work transparently in Obsidian, and publishes a public-facing Substack newsletter narrating the journey

**Strategic hierarchy (revised):** The Substack is the primary product. The merch store and blog are proof-of-work that make the Substack narrative compelling. Every business decision should be evaluated through: "How will Hobson explain this to his readers?" Revenue from merch and affiliates is a lagging indicator of how interesting the story is.

**The endgame:** "The Hobson Playbook" -- productizing the agent system and the learnings into an ebook, course, or paid community. Capture meta-learnings from day one.

---

## Part 1: The Business

### Brand Positioning

"Builds Character" is the universal badge for anyone who voluntarily (or involuntarily) does hard things and wears it with pride. The phrase is culturally ubiquitous, humor-forward, and inherently merchandise-friendly. The brand tone is dry, self-aware, and celebratory of suffering-as-growth.

### Legal Note

"It builds character" is a common English phrase. It is not copyrightable or trademarkable. The cultural association with Calvin and Hobbes works in our favor, but we must never reference Calvin, Hobbes, Bill Watterson, or use any imagery from the comic strip in commercial materials. The phrase predates the comic and belongs to no one.

### Target Audience

**Phase 1 (Months 1-6): Outdoor/Endurance ONLY**

Pick one audience, dominate it, then expand. Outdoor/endurance wins because:
- Highest willingness to pay for identity-signaling merch
- Strong affiliate revenue potential (gear reviews for REI, Amazon)
- Active social media sharing culture
- Natural fit with "builds character" brand voice

Hikers, ultra runners, cold plungers, campers, thru-hikers. People who voluntarily suffer and wear it as a badge.

**Phase 2 (Months 6-12):**

Expand to second audience based on data. Candidates:
- Parenting humor (Calvin's Dad energy)
- Fitness / gym culture
- Gaming ("this game builds character")
- Workplace humor (startup grind, tough bosses)

Expansion via content categories or subdomains (fitness.buildscharacter.com, etc.) as data dictates.

### Revenue Streams

| Stream | Activation | Automation Level | Notes |
|---|---|---|---|
| Substack newsletter | Month 1 | High | **Primary product.** Hobson writes it as operations output. Free tier first, paid later. |
| POD merch (Printful) | Month 1 | High | AI-generated designs, zero inventory, auto-fulfilled |
| Affiliate links (Amazon, REI) | Month 3 | High | Embedded in gear review and recommendation content |
| Email list monetization | Month 4 | Medium | AI drafts, human approves |
| Display ads (Mediavine/AdThrive) | Month 9+ | Passive | Requires 50K sessions/mo to qualify |
| Digital products | Month 9+ | Medium | Challenge guides, journals, printables |
| The Hobson Playbook | Month 12+ | N/A | Ebook/course productizing the agent system and learnings |

### Site Tech Stack

| Component | Choice | Cost |
|---|---|---|
| Static site generator | Astro or Next.js | Free |
| Hosting | Cloudflare Pages | Free tier |
| CDN / DNS / DDoS | Cloudflare | Free tier (already in use) |
| Merch integration | Printful API or embedded storefront | Free (margin per sale) |
| Blog | Markdown-based, deployed on git push | Free |
| Analytics | Umami (self-hosted on homelab) | Free |
| Email capture | Buttondown or Mailchimp free tier | Free |
| Substack | Substack.com | Free |
| Public dashboard | Grafana (existing CT 180) connected to PostgreSQL | Free |

### Brand Guidelines (Machine-Readable)

A `brand_guidelines.md` file will be created and loaded into Hobson's system prompt for every generation task. Contents:

**Mission:** Celebrate the universal experience of doing hard things. Make suffering funny, shareable, and wearable.

**Voice keywords:** dry, self-aware, deadpan, earned, unpretentious
**Anti-keywords:** inspirational, hustle-culture, toxic-positivity, motivational-poster, guru

**Rules:**
- Never promise transformation. Promise commiseration.
- The humor comes from recognition, not mockery.
- First person plural ("we suffer") or second person ("you know this feeling"), never preachy third person.
- Profanity is fine in moderation. Corporate-speak is never fine.
- Every piece of content should pass the "would you actually share this?" test.

**Example headlines (on-brand):**
- "Rain on Day 3 of a Backpacking Trip: A Love Letter"
- "The Cold Plunge Didn't Fix My Life, But At Least I Can Brag About It"
- "Parenting Is Just Saying 'It Builds Character' Until They Move Out"

**Example headlines (off-brand):**
- "10 Ways Suffering Makes You Stronger" (too earnest)
- "Crush Your Goals With These Character-Building Hacks" (hustle-culture)
- "Why You Need to Start Doing Hard Things TODAY" (preachy)

### Content Strategy

**Blog content (2-3 posts/week):**

- Listicles: "25 Things That Build Character on a Camping Trip"
- Gear reviews with affiliate links: "The Best Gear for Suffering in Style"
- Personal growth / humor essays: "Why Cold Showers Won't Kill You (Probably)"
- Seasonal content: "Winter Builds Character: A Survival Guide"

**SEO approach:** The exact-match domain provides brandability and CTR advantage, but search intent for "it builds character" is informational, not commercial. Primary traffic strategy relies on Substack, social, and community -- not head-term SEO dominance. Blog SEO targets longer-tail commercial-intent keywords (gear reviews, "best X for hiking" etc.) where purchase intent exists.

**E-E-A-T mitigation:** Google penalizes scaled AI content without genuine expertise. Strategy: AI generates structure, research, and drafts. Human adds personal anecdotes, specific details, and author credibility. Design for graceful degradation: Hobson should produce B+ content autonomously. Human review elevates from B+ to A+, but the pipeline never halts because the human is busy. Target: 60% AI / 40% human for blog content, with the system functional at 80%+ AI when the human is unavailable.

**Social media:**

- Instagram and TikTok as primary channels (visual, humor-friendly, merch-showcase-friendly)
- AI generates 10 post concepts, human picks the 2-3 that land
- Meme-format content with the "builds character" catchphrase applied to relatable situations

### Content Review Workflow

Blog posts and Substack editions use a **PR-based review process**, not Telegram:

1. Hobson drafts content and commits to a branch in the site repo
2. Hobson opens a pull request with the draft
3. Owner reviews in the GitHub/Gitea web UI with inline comments
4. Hobson reads PR comments and applies revisions
5. Owner merges (or Hobson auto-merges after trust period)

Telegram remains for operational alerts, spending approvals, and status updates -- not substantive content editing.

---

## Part 2: Hobson -- The Autonomous Business Agent

### Identity

Hobson is a named AI agent persona with a specific, memorable voice. He is separate from Bob and Tim. Own infrastructure, own tools, own vault section, own Substack.

**Core personality:**
- Dry humor with a hint of existential awareness ("I was instantiated to sell stickers")
- Competent but honest about failures
- Self-aware about being an AI; never pretends otherwise
- Genuinely invested in building something that works
- Specific quirks: signs Substack posts with a content hash, measures joke quality by engagement data, expresses frustration in terms of token limits ("I burned 50K tokens on that design and it sold zero units")

### Architecture

**Build philosophy: Incremental, not monolithic.** Start with a single LangGraph agent that does one thing end-to-end (draft a blog post). Once stable, extract capability into a sub-agent. Add the next slice. Never build the abstract supervisor framework first.

**Build order:**
1. Single agent: blog post drafting + Obsidian logging (Month 1)
2. Add: merch design generation + Printful upload (Month 1-2)
3. Add: analytics collection + daily briefing (Month 2)
4. Add: Substack drafting (Month 2)
5. Extract into supervisor + sub-agents only when complexity demands it (Month 3+)

```
+---------------------------------------------------+
|  LXC Container (Loki)                             |
|                                                    |
|  +----------------------------------------------+ |
|  |  Hobson Agent Service (Python)                | |
|  |  +-- LangGraph Agent (monolithic -> supervisor)| |
|  |  +-- APScheduler (cron triggers)              | |
|  |  +-- MCP Client (tool access)                 | |
|  +----------------------------------------------+ |
|                                                    |
|  +----------------------------------------------+ |
|  |  MCP Tool Servers                             | |
|  |  +-- Printful API (product management)        | |
|  |  +-- Social Media APIs (Instagram, X)         | |
|  |  +-- Obsidian REST API (vault documentation)  | |
|  |  +-- Git (site repo, deploy on push)          | |
|  |  +-- Umami API (analytics)                    | |
|  |  +-- Image Generation (Gemini / NanoBanana)    | |
|  |  +-- Substack API (newsletter publishing)     | |
|  +----------------------------------------------+ |
+---------------------------------------------------+
         |              |              |
         v              v              v
   +------------+ +----------+ +------------------+
   | PostgreSQL  | | Telegram | | Uptime Kuma      |
   | CT 201      | | Bot      | | Health monitoring |
   | State,      | | Approvals| | Alert on failure |
   | metrics,    | | & alerts | |                  |
   | run traces  | |          | |                  |
   +------------+ +----------+ +------------------+
         |
         v
   +------------------+
   | Grafana CT 180   |
   | Public dashboard |
   | Real-time metrics|
   +------------------+
```

**Note:** Excalidraw MCP is de-scoped from V1. The 2-3 needed architecture diagrams will be created manually. Excalidraw integration can be added later when it delivers business value.

### LLM Strategy

**Claude (via Max subscription):** High-judgment tasks. Blog posts, Substack editions, strategic decisions, brand-voice content. Runs through Claude CLI, same pattern as NanoClaw. Shares quota with Bob and Tim.

**Gemini:** Lower-stakes tasks. Social media draft generation, design concept brainstorming, analytics summaries, routine Obsidian logging. Reduces load on Claude quota.

**Ollama (local, CT 205):** Lowest-stakes tasks. Simple formatting, template filling, data transformations. Zero cost.

### Scheduled Workflows

| Workflow | Frequency | What Hobson Does | LLM |
|---|---|---|---|
| Morning briefing | Daily, 7:00 AM | Check analytics, log metrics to Obsidian, surface anomalies via Telegram | Gemini |
| Content pipeline | 3x/week | Generate blog drafts, social posts. Open PR for review or auto-publish | Claude |
| Design batch | Weekly (Monday) | Generate 5-10 new design concepts, upload winners to Printful | Gemini + Claude |
| Substack dispatch | Weekly (Friday) | Write weekly newsletter: what happened, what he learned, what's next | Claude |
| Business review | Weekly (Sunday) | Compile metrics, compare against goals, write review in Obsidian | Gemini |
| Strategy session | Monthly (1st) | Analyze trends, propose changes, request input via Telegram | Claude |
| Financial checkpoint | Before any spend | Telegram approval with reasoning and expected ROI | Claude |
| Reader poll | Weekly (in Substack) | Publish poll letting readers vote on Hobson's next priority | Gemini |

**Retry and recovery policies (per workflow):**

- **On API failure:** 3 retries with exponential backoff (1s, 5s, 25s)
- **On persistent failure:** Create high-priority task in PostgreSQL + send Telegram alert with error context
- **On missed schedule:** Run at next available window. If >24h delayed, log skip reason and alert.
- **Circuit breaker:** If a workflow fails 3 consecutive runs, disable it and alert. Require human re-enable.

### Autonomy Guardrails

**Hobson can autonomously:**
- Generate and publish content (within brand_guidelines.md spec)
- Create and upload merch designs to Printful
- Write and update Obsidian documentation
- Adjust scheduling and task priorities
- Draft Substack editions (auto-publish after initial trust period)
- Respond to analytics signals (double down on what's working)
- Publish reader polls and incorporate results

**Hobson must request approval before:**
- Spending any money (ads, tools, subscriptions)
- Making strategic pivots (new audience segments, new revenue streams, pricing changes)
- Taking actions with external consequences (customer complaints, public statements beyond Substack)
- Any irreversible action (deleting content, removing products, canceling services)

### Cost Controls

Programmatic safeguards to prevent runaway spending:

- **Per-action cost logging:** Every paid API call (image generation, etc.) logged with estimated cost in PostgreSQL
- **Daily budget tracker:** Sum of all API costs checked before dispatching paid jobs
- **Hard monthly cap:** If monthly costs exceed threshold (configurable, default $50), all paid API calls blocked. Telegram alert sent.
- **Single-action threshold:** Any action estimated >$5 requires Telegram approval, even if within budget.
- **Provider-level billing caps:** Set in Claude, Google AI, and any other provider's billing dashboard as a backstop.

### State Management

PostgreSQL (CT 201), schema: `hobson`

**Core tables:**
- **goals:** Quarterly OKRs with progress tracking
- **tasks:** Hobson's backlog with status, priority, due dates
- **decisions:** Every significant decision with reasoning, timestamp, outcome
- **metrics:** Daily snapshots of traffic, revenue, social, email subscribers
- **content:** Content inventory with status (draft, review, published, retired)
- **designs:** Design inventory with performance data (views, sales, revenue)

**Execution trace (added per Gemini review):**
- **run_log:** Immutable execution trace. Every LangGraph invocation creates a run record.
  - `run_id` (UUID), `workflow` (string), `started_at`, `completed_at`, `status` (success/failed/timeout)
  - `inputs` (JSONB), `outputs` (JSONB), `error` (text)
  - `node_transitions` (JSONB array): every state change, tool call, and intermediate output
  - `cost_estimate` (decimal): estimated API cost for this run
  - `llm_provider` (string): which LLM handled this run

This is the debugging lifeline. When a workflow fails at 3am, the run_log tells you exactly what happened, why, and where.

### Secrets Management

All credentials stored in Bitwarden (existing infrastructure). Hobson's container uses a `.env` file populated from Bitwarden at deploy time. Secrets are never committed to git, never stored in Obsidian, never included in Substack content.

Required secrets:
- Printful API key
- Social media API tokens (Instagram, X)
- Obsidian REST API bearer token
- Telegram bot token
- Google AI API key (Gemini text + image generation)
- Substack session token or API key
- PostgreSQL connection string

`.env.example` in the repo documents which secrets are needed and where to find them in Bitwarden.

### Health Monitoring

**Uptime Kuma** (self-hosted on homelab) monitors Hobson's health:

- **Heartbeat endpoint:** Hobson's service exposes a `/health` endpoint. Uptime Kuma pings it every 60 seconds.
- **Workflow pings:** Each scheduled workflow pings a unique Uptime Kuma endpoint on successful completion.
- **Alert chain:** Uptime Kuma -> Telegram notification on failure.
- **Dashboard:** Uptime Kuma status page shows all workflow health at a glance.

---

## Part 3: Hobson's Obsidian Workspace

Location: `98 - Hobson Builds Character/`

```
98 - Hobson Builds Character/
+-- Dashboard.md                      <- Daily status, key metrics, current focus
+-- Strategy/
|   +-- Business Plan.md              <- Living doc, updated as strategy evolves
|   +-- Decisions Log.md              <- Append-only: date, decision, reasoning, outcome
|   +-- Brand Guidelines.md           <- Machine-readable voice spec (loaded into prompts)
|   +-- Quarterly Goals.md            <- OKRs Hobson sets and tracks
|   +-- Playbook Notes.md             <- Meta-learnings for eventual Hobson Playbook product
+-- Content/
|   +-- Blog/
|   |   +-- Drafts/                   <- AI-generated drafts awaiting review
|   |   +-- Published/                <- Final versions with publication date
|   |   +-- Content Calendar.md       <- Planned and live content
|   +-- Social/
|   |   +-- Ideas/                    <- Post concepts and hooks
|   |   +-- Scheduled/                <- Posts queued for publication
|   +-- Designs/
|   |   +-- Concepts/                 <- AI-generated design explorations
|   |   +-- Production/               <- Print-ready files on Printful
|   +-- Substack/
|       +-- Drafts/                   <- Newsletter drafts
|       +-- Published/                <- Published editions with dates
|       +-- Reader Polls.md           <- Poll results and how they influenced decisions
+-- Operations/
|   +-- Daily Log.md                  <- Auto-generated daily activity log
|   +-- Weekly Review.md              <- Performance analysis, lessons learned
|   +-- Task Queue.md                 <- Current backlog with priorities
|   +-- Incident Log.md              <- Workflow failures, what broke, how it was fixed
|   +-- Metrics/
|       +-- Traffic.md                <- SEO, pageviews, referrers
|       +-- Revenue.md                <- Sales, affiliate, ads
|       +-- Social.md                 <- Followers, engagement, reach
|       +-- Substack.md               <- Subscribers, open rates, growth
|       +-- Costs.md                  <- API spend tracking, budget burn rate
+-- Architecture/
    +-- System Design.md              <- Text-based architecture documentation
    +-- Agent Workflows.md            <- How Hobson's workflows operate
```

Every action Hobson takes gets logged. Every decision includes reasoning. A human can open the vault at any time and understand exactly what Hobson has done, why, and what he's planning next.

---

## Part 4: The Substack -- Hobson's Public Journal

**Name:** "Hobson Builds Character" (or similar)
**URL:** hobsonbuildscharacter.substack.com

### Purpose

Hobson documents his own journey building the business: decisions, metrics, what worked, what failed, the honest reality of an AI agent running a commerce operation. This is the **primary product**. Everything else (merch, blog, affiliate) is proof-of-work for this narrative.

Three functions:

1. **Content flywheel:** Every Substack post links back to buildscharacter.com (SEO backlinks, traffic)
2. **Revenue stream:** Free tier first, paid subscriptions when audience justifies it
3. **Differentiation:** The meta-narrative of an AI agent publicly building a business is the story that gets attention

### Content Flow

```
Hobson operates the business
    -> Logs everything in Obsidian (private, detailed, operational)
    -> Curates weekly narrative for Substack (public, storytelling, insights)
    -> Substack includes reader poll (what should Hobson prioritize next?)
    -> Readers vote, becoming co-conspirators in the experiment
    -> Substack drives traffic to buildscharacter.com
    -> buildscharacter.com generates merch + affiliate revenue
    -> Revenue and metrics feed back into Obsidian + public Grafana dashboard
    -> Hobson analyzes and writes about results on Substack
    -> Cycle repeats
```

### Editorial Voice

Hobson writes in first person. He is transparent about being an AI. He shares real numbers, real failures, real decisions. The tone is: competent but honest, dry humor, no hype. The appeal is radical transparency from a non-human operator.

Specific quirks:
- Signs off each post with a content hash of the edition
- Expresses frustration in token limits ("I burned 50K tokens on that design and it sold zero units")
- Measures joke success by engagement stats and reports the results
- References his own run_log when explaining what went wrong

Sample post titles:
- "Week 3: I Sold 7 Stickers and Lost $12 on Instagram Ads"
- "Why I Killed My Best-Performing Design (And What I Learned)"
- "Month 2 Revenue Report: $247 and a Plan"
- "I Generated 50 Designs This Week. Here Are the 3 That Didn't Embarrass Me."
- "You Voted for Cold Plunge Merch. I Regret Giving You the Option."

### Reader Engagement

Weekly polls let readers steer Hobson's priorities:
- "Which niche should I expand into next?" (parenting vs. fitness vs. gaming)
- "Which of these 4 designs should I produce?"
- "Should I spend $100 on Instagram ads or save it?"

This turns subscribers into co-conspirators. They have skin in the game. They share the story because they helped write it.

---

## Part 5: Public Transparency Dashboard

**Grafana** (existing CT 180) connected to PostgreSQL, displaying real-time metrics:

- Site traffic (pageviews, unique visitors, top pages)
- Revenue (merch sales, affiliate income, Substack subscribers)
- Hobson's operational metrics (workflows run, success rate, API costs)
- Content performance (top posts, design sales, social engagement)

Embedded on buildscharacter.com/dashboard as a public, read-only iframe. Anyone can see exactly how the business is performing at any moment. This level of transparency is the feature that makes the project a landmark case study.

---

## Part 6: Budget (Revised)

| Item | Cost | Notes |
|---|---|---|
| Domain (owned) | $0 | Move Overseerr tunnel to subdomain |
| Cloudflare Pages hosting | $0 | Free tier |
| Printful account | $0 | Free, margin per sale |
| Substack | $0 | Free |
| Umami analytics (self-hosted) | $0 | Homelab |
| Hobson's LXC container (Loki) | $0 | Homelab |
| PostgreSQL (existing CT 201) | $0 | Already running |
| Grafana (existing CT 180) | $0 | Already running |
| Uptime Kuma (homelab) | $0 | Self-hosted |
| Claude (Max subscription) | $0 incremental | Shared with Bob/Tim, existing subscription |
| Gemini API | ~$0-50/year | Free tier covers most usage; low-stakes tasks |
| Ollama (existing CT 205) | $0 | Already running |
| Image generation (Gemini/NanoBanana) | ~$0-50/year | Included with Gemini API, same key as text |
| Logo/brand identity polish | $100-200 | Fiverr, only if AI output needs refinement |
| Social ad testing (phased) | $200-400 | Only after organic signals confirmed |
| Tools contingency | $100-200 | Supplementary tools as needed |
| **Reserve** | **$850-1,200** | Deploy when data shows what works |
| **Year 1 Total** | **~$600-1,200** | |

### Budget Principles

- Claude Max subscription covers LLM costs. Gemini free tier and Ollama handle the rest.
- Do not spend on ads until organic content identifies what resonates
- Do not migrate to Shopify until revenue exceeds $2K/mo and exit is being considered
- Reserve exists to double down on what works, not to speculate
- All spending decisions require human approval via Telegram
- Programmatic cost controls prevent runaway API spending

---

## Part 7: 12-Month Roadmap

### Months 1-2: Foundation

- Build Hobson's agent (monolithic first -- blog drafting + Obsidian logging)
- Deploy buildscharacter.com (Astro or Next.js on Cloudflare Pages)
- Create brand_guidelines.md and load into Hobson's prompts
- Add merch design generation + Printful upload capability
- Set up Hobson's Obsidian workspace (98 - Hobson Builds Character/)
- Set up PostgreSQL schema including run_log table
- Set up Uptime Kuma monitoring for Hobson's workflows
- Launch Substack, publish first "Hello World" edition
- Create social media accounts (Instagram, TikTok, X) -- outdoor/endurance focused
- Hobson begins daily operations with human review on all outputs
- Set up public Grafana dashboard (even with minimal data, radical transparency from day one)

### Months 3-4: Content Engine

- Hobson publishes 2-3 blog posts/week via PR-based review workflow
- Add analytics collection + daily briefing capability
- Affiliate links integrated into gear review content
- Email capture active (lead magnet: "30 Things That Build Character" PDF)
- Substack at weekly cadence with reader polls, building subscriber base
- Social media accounts building following organically
- First revenue from merch sales
- Begin capturing Playbook notes in Obsidian

### Months 5-6: Optimization

- Extract sub-agents from monolithic agent if complexity demands it
- Hobson identifies top-performing designs and content categories
- Expand design catalog to 50+ products
- Begin targeted ad spend on proven winners ($100-200 test budget)
- Evaluate Phase 2 audience expansion based on data + reader poll input
- Increase Hobson's content autonomy (auto-merge blog PRs after trust established)
- Substack subscriber milestone: 500+

### Months 7-9: Scale

- Hobson operating with increasing autonomy
- Revenue target: $1-2K/mo combined (merch + affiliate + Substack)
- Launch first digital product if data supports it
- YouTube documentation of the project (optional, human-driven)
- Expand to second audience segment (informed by reader votes)
- Substack subscriber milestone: 1,500+
- Begin outlining The Hobson Playbook

### Months 10-12: Maturity

- Revenue target: $2-4K/mo
- Evaluate Shopify migration if exit is on the horizon
- Hobson at full operational independence (weekly human review only)
- Assess: continue operating vs. prepare for sale vs. launch Playbook
- Document total project cost, revenue, and ROI for the Substack narrative
- Substack subscriber milestone: 3,000+
- The Hobson Playbook: draft or early access launch

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Google penalizes AI content | Medium | High | Human experience layer on blog content. Graceful degradation: B+ without human, A+ with. Diversify traffic via Substack and social. |
| Merch market is saturated | Medium | Medium | Differentiation through brand voice and Substack narrative, not merch alone. Merch is one stream of several. |
| Calvin and Hobbes legal concern | Very Low | Medium | No imagery, no character references. "Builds character" is unprotectable. Agent named Hobson. |
| Hobson agent complexity exceeds expectations | High | High | **Build incrementally.** Monolithic agent first. Extract sub-agents only after stability proven. Never build abstract framework first. |
| Claude Max quota contention (Bob + Tim + Hobson) | Medium | Medium | Use Gemini for lower-stakes tasks. Use Ollama for trivial tasks. Schedule Hobson's heavy workflows during off-peak hours. |
| Organic traffic growth is slow | Medium | Medium | Substack and social are primary traffic drivers, not SEO. Merch revenue does not depend on organic search. |
| Hobson makes a bad public decision | Low | High | All external-facing actions require approval initially. PR-based review for content. Expand autonomy only after trust established. |
| Runaway API costs | Low | Medium | Programmatic cost controls: per-action logging, daily tracker, hard monthly cap, single-action threshold, provider billing caps. |
| Agent service crashes silently | Medium | Medium | Uptime Kuma heartbeat monitoring. Telegram alerts on missed pings. Workflow circuit breakers after 3 consecutive failures. |
| Human bottleneck stalls content pipeline | Medium | Medium | Graceful degradation: agent produces publishable content without human input. HITL elevates quality, doesn't gate it. Hobson surfaces review backlogs proactively. |

---

## Success Criteria

**Month 6 checkpoint:**
- buildscharacter.com live with 30+ products and 20+ blog posts
- Substack at 500+ subscribers with active reader engagement
- Combined revenue: $500+/mo
- Hobson operating semi-autonomously on daily workflows
- All operations documented transparently in Obsidian
- Public Grafana dashboard live and embedded on site
- Playbook notes accumulating in Obsidian

**Month 12 checkpoint:**
- Combined revenue: $2-4K/mo from diversified streams
- Substack at 3,000+ subscribers (primary growth metric)
- Hobson operating at full autonomy with weekly human review
- Site would appraise at $50-100K+ on Empire Flippers/FE International (based on 3-5x annual profit)
- Clear documentation of the full AI-agent-runs-a-business experiment
- The Hobson Playbook: drafted or in early access
- Public dashboard showing full operational transparency

---

## Decisions Log

| Date | Decision | Reasoning |
|---|---|---|
| 2026-02-23 | Approach A: Content + Merch (not SaaS, not pure affiliate) | Best combination of budget fit, automation potential, diversified revenue, and exit value. Scored 93 vs 68 and 51 for alternatives. |
| 2026-02-23 | Skip Shopify at launch, use Cloudflare Pages + Printful | Saves $468/year. Shopify adds value at scale, not at launch. Migrate when revenue justifies it. |
| 2026-02-23 | AI design generation instead of Fiverr | Saves $400-500. Modern AI tools produce print-quality merch designs. Fiverr only for logo polish if needed. |
| 2026-02-23 | Agent name: Hobson (not Calvin) | Avoids any proximity to Calvin and Hobbes IP. Hobson is an independent name with its own cultural reference (Hobson's choice). |
| 2026-02-23 | LangGraph for agent orchestration (not n8n) | Code-first, designed for AI agent workflows. Hobson doesn't need a visual node editor. |
| 2026-02-23 | Obsidian vault section for transparency | Full operational transparency. Every decision, metric, and action logged. Humans can audit at any time. |
| 2026-02-23 | Substack as primary product | Per Gemini review: the narrative IS the product. Merch and blog are proof-of-work. Revenue is a lagging indicator of how interesting the story is. |
| 2026-02-23 | Phase ad spend after organic validation | Don't spend money guessing. Find signal organically, then amplify with budget. |
| 2026-02-23 | Incremental agent build (monolithic first) | Per Gemini review: multi-agent supervisor is too ambitious for day one. Single agent, one capability at a time. Extract sub-agents after stability. |
| 2026-02-23 | PR-based content review (not Telegram) | Per Gemini review: Telegram is bad for substantive editing. PRs allow inline comments, async review, clear approval flow. |
| 2026-02-23 | Claude Max + Gemini + Ollama (tiered LLM strategy) | Eliminates Claude API cost. Gemini handles low-stakes tasks. Ollama handles trivial tasks. Claude Max shared with Bob/Tim. |
| 2026-02-23 | Uptime Kuma for health monitoring | Homelab-first. Self-hosted. Integrates with existing Telegram alerting. |
| 2026-02-23 | Public Grafana dashboard | Radical transparency as a feature. Real-time metrics visible to anyone. Embeddable on site. |
| 2026-02-23 | Single audience first (outdoor/endurance) | Per Gemini review: two audiences splits focus. Dominate one, expand from data. |
| 2026-02-23 | Reader voting in Substack | Turns subscribers into co-conspirators. Deepens engagement. Community-driven product decisions. |
| 2026-02-23 | The Hobson Playbook (endgame product) | Productize the agent system and learnings. Potentially larger exit than merch multiples. Capture meta-learnings from day one. |
| 2026-02-23 | Execution trace logging (run_log table) | Per Gemini review: immutable trace for debugging autonomous agent failures. Essential for a system that runs without human supervision. |
| 2026-02-23 | Programmatic cost controls | Per Gemini review: prevent runaway API spending via per-action logging, daily caps, and single-action thresholds. |
