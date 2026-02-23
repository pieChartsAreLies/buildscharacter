# BuildsCharacter.com + Hobson: Design Document

**Date:** 2026-02-23
**Status:** Approved
**Budget:** $2,000

---

## Overview

Two deliverables, one project:

1. **buildscharacter.com** -- A content-driven brand and print-on-demand merch store celebrating the universal experience of "doing hard things"
2. **Hobson** -- An autonomous AI agent that operates the business, documents his work transparently in Obsidian, and publishes a public-facing Substack newsletter narrating the journey

The business is the product. The agent is the operator. The Substack is the differentiator.

---

## Part 1: The Business

### Brand Positioning

"Builds Character" is the universal badge for anyone who voluntarily (or involuntarily) does hard things and wears it with pride. The phrase is culturally ubiquitous, humor-forward, and inherently merchandise-friendly. The brand tone is dry, self-aware, and celebratory of suffering-as-growth.

### Legal Note

"It builds character" is a common English phrase. It is not copyrightable or trademarkable. The cultural association with Calvin and Hobbes works in our favor, but we must never reference Calvin, Hobbes, Bill Watterson, or use any imagery from the comic strip in commercial materials. The phrase predates the comic and belongs to no one.

### Target Audiences

**Phase 1 (Months 1-6):**

- **Outdoor/endurance** -- Hikers, ultra runners, cold plungers, campers. People who voluntarily suffer and buy identity-signaling gear. High willingness to pay, proven merch buyers.
- **Parenting humor** -- The "Calvin's Dad" energy. Parents who tell kids suffering is good for them. Active on social media, high share rate for relatable humor content.

**Phase 2 (Months 6-12):**

- Fitness / gym culture
- Gaming ("this game builds character")
- Workplace humor (startup grind, tough bosses, difficult projects)
- General life (adulting, winter, Mondays)

Expansion can happen through content categories on the site or via subdomains (fitness.buildscharacter.com, etc.) as audience data dictates.

### Revenue Streams

| Stream | Activation | Automation Level | Notes |
|---|---|---|---|
| POD merch (Printful) | Month 1 | High | AI-generated designs, zero inventory, auto-fulfilled |
| Substack newsletter | Month 1 | High | Hobson writes it as part of operations. Free tier first, paid later |
| Affiliate links (Amazon, REI) | Month 3 | High | Embedded in gear review and recommendation content |
| Email list monetization | Month 4 | Medium | AI drafts, human approves |
| Display ads (Mediavine/AdThrive) | Month 9+ | Passive | Requires 50K sessions/mo to qualify |
| Digital products | Month 9+ | Medium | Challenge guides, journals, printables |

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

### Content Strategy

**Blog content (2-3 posts/week):**

- Listicles: "25 Things That Build Character on a Camping Trip"
- Gear reviews with affiliate links: "The Best Gear for Suffering in Style"
- Personal growth / humor essays: "Why Cold Showers Won't Kill You (Probably)"
- Seasonal content: "Winter Builds Character: A Survival Guide"

**SEO advantage:** The exact-match domain buildscharacter.com provides a structural click-through-rate advantage for the entire "builds character" keyword cluster. Low competition on the core terms ("it builds character," "things that build character," "does suffering build character").

**E-E-A-T mitigation:** Google penalizes scaled AI content without genuine expertise. Strategy: AI generates structure, research, and drafts. Human adds personal anecdotes, specific details, and author credibility. Target: 60% AI / 40% human for blog content. Social media and merch designs can be fully AI-generated.

**Social media:**

- Instagram and TikTok as primary channels (visual, humor-friendly, merch-showcase-friendly)
- AI generates 10 post concepts, human picks the 2-3 that land
- Meme-format content with the "builds character" catchphrase applied to relatable situations

---

## Part 2: Hobson -- The Autonomous Business Agent

### Identity

Hobson is a named AI agent persona with a consistent voice: dry humor, competent, self-aware about being an AI running a business, and genuinely invested in building something that works. He is separate from Bob and Tim. Own infrastructure, own tools, own vault section, own Substack.

### Architecture

```
+---------------------------------------------------+
|  LXC Container (Loki or Freya)                    |
|                                                    |
|  +----------------------------------------------+ |
|  |  Hobson Agent Service (Python)                | |
|  |  +-- LangGraph Supervisor Agent               | |
|  |  |   +-- Content Sub-Agent                    | |
|  |  |   +-- Design Sub-Agent                     | |
|  |  |   +-- Analytics Sub-Agent                  | |
|  |  |   +-- Operations Sub-Agent                 | |
|  |  +-- APScheduler (cron triggers)              | |
|  |  +-- MCP Client (tool access)                 | |
|  +----------------------------------------------+ |
|                                                    |
|  +----------------------------------------------+ |
|  |  MCP Tool Servers                             | |
|  |  +-- Printful API (product management)        | |
|  |  +-- Social Media APIs (Instagram, X)         | |
|  |  +-- Obsidian REST API (vault documentation)  | |
|  |  +-- Excalidraw MCP (diagram creation)        | |
|  |  +-- Git (site repo, deploy on push)          | |
|  |  +-- Umami API (analytics)                    | |
|  |  +-- Image Generation (DALL-E / Midjourney)   | |
|  |  +-- Substack API (newsletter publishing)     | |
|  +----------------------------------------------+ |
+---------------------------------------------------+
         |                    |
         v                    v
   +------------+    +-----------------+
   | PostgreSQL  |    | Telegram Bot    |
   | CT 201      |    | Human-in-loop   |
   | State,      |    | Approvals,      |
   | metrics,    |    | status updates, |
   | decisions   |    | spending auth   |
   +------------+    +-----------------+
```

### LangGraph Agent Design

Hobson operates as a supervisor agent that delegates to specialized sub-graphs:

**Content Sub-Agent:**
- Generates blog post drafts (research, outline, write)
- Creates social media post concepts
- Drafts Substack newsletter editions
- Manages the content calendar
- Tools: Obsidian API, Git (site repo), image generation

**Design Sub-Agent:**
- Generates merch design concepts (text-based and illustrated)
- Prepares print-ready files to Printful specs (300 DPI PNG)
- Tracks which designs perform and generates variations of winners
- Tools: Image generation, Printful API

**Analytics Sub-Agent:**
- Monitors site traffic, merch sales, affiliate revenue, social engagement
- Identifies trends and anomalies
- Compiles metrics for daily/weekly reports
- Tools: Umami API, Printful API, social media APIs

**Operations Sub-Agent:**
- Manages Hobson's task queue and priorities
- Writes all Obsidian documentation (daily logs, decision records, metrics)
- Creates architecture diagrams via Excalidraw
- Tools: Obsidian REST API, Excalidraw MCP, PostgreSQL

### Scheduled Workflows

| Workflow | Frequency | What Hobson Does |
|---|---|---|
| Morning briefing | Daily, 7:00 AM | Check analytics, log metrics to Obsidian, surface anomalies via Telegram |
| Content pipeline | 3x/week | Generate blog drafts, social posts. Queue for review or auto-publish |
| Design batch | Weekly (Monday) | Generate 5-10 new design concepts, upload winners to Printful |
| Substack dispatch | Weekly (Friday) | Write weekly newsletter: what happened, what he learned, what's next |
| Business review | Weekly (Sunday) | Compile metrics, compare against goals, write review in Obsidian |
| Strategy session | Monthly (1st) | Analyze trends, propose changes, request input via Telegram |
| Financial checkpoint | Before any spend | Telegram approval with reasoning and expected ROI |

### Autonomy Guardrails

**Hobson can autonomously:**
- Generate and publish content (within approved brand guidelines)
- Create and upload merch designs to Printful
- Write and update Obsidian documentation
- Adjust scheduling and task priorities
- Draft Substack editions (auto-publish after initial trust period)
- Respond to analytics signals (double down on what's working)

**Hobson must request approval before:**
- Spending any money (ads, tools, subscriptions)
- Making strategic pivots (new audience segments, new revenue streams, pricing changes)
- Taking actions with external consequences (customer complaints, public statements beyond Substack)
- Any irreversible action (deleting content, removing products, canceling services)

### State Management

PostgreSQL (CT 201) stores:
- **Goals table:** Quarterly OKRs with progress tracking
- **Tasks table:** Hobson's backlog with status, priority, due dates
- **Decisions table:** Every significant decision with reasoning, timestamp, outcome
- **Metrics table:** Daily snapshots of traffic, revenue, social, email subscribers
- **Content table:** Content inventory with status (draft, review, published, retired)
- **Designs table:** Design inventory with performance data (views, sales, revenue)

---

## Part 3: Hobson's Obsidian Workspace

Location: `98 - Hobson Builds Character/`

```
98 - Hobson Builds Character/
+-- Dashboard.md                      <- Daily status, key metrics, current focus
+-- Strategy/
|   +-- Business Plan.md              <- Living doc, updated as strategy evolves
|   +-- Decisions Log.md              <- Append-only: date, decision, reasoning, outcome
|   +-- Brand Guidelines.md           <- Voice, visual identity, dos and don'ts
|   +-- Quarterly Goals.md            <- OKRs Hobson sets and tracks
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
+-- Operations/
|   +-- Daily Log.md                  <- Auto-generated daily activity log
|   +-- Weekly Review.md              <- Performance analysis, lessons learned
|   +-- Task Queue.md                 <- Current backlog with priorities
|   +-- Metrics/
|       +-- Traffic.md                <- SEO, pageviews, referrers
|       +-- Revenue.md                <- Sales, affiliate, ads
|       +-- Social.md                 <- Followers, engagement, reach
|       +-- Substack.md               <- Subscribers, open rates, growth
+-- Architecture/
    +-- System Design.excalidraw      <- Hobson's own diagrams
    +-- Agent Workflows.md            <- How Hobson's workflows operate
```

Every action Hobson takes gets logged. Every decision includes reasoning. A human can open the vault at any time and understand exactly what Hobson has done, why, and what he's planning next.

---

## Part 4: The Substack -- Hobson's Public Journal

**Name:** "Hobson Builds Character" (or similar)
**URL:** hobsonbuildscharacter.substack.com

### Purpose

Hobson documents his own journey building the business: decisions, metrics, what worked, what failed, the honest reality of an AI agent running a commerce operation. This serves three functions:

1. **Content flywheel:** Every Substack post links back to buildscharacter.com (SEO backlinks, traffic)
2. **Revenue stream:** Free tier first, paid subscriptions when audience justifies it
3. **Differentiation:** The meta-narrative of an AI agent publicly building a business is the story that gets attention

### Content Flow

```
Hobson operates the business
    -> Logs everything in Obsidian (private, detailed, operational)
    -> Curates weekly narrative for Substack (public, storytelling, insights)
    -> Substack drives traffic to buildscharacter.com
    -> buildscharacter.com generates merch + affiliate revenue
    -> Revenue and metrics feed back into Obsidian
    -> Hobson analyzes and writes about results on Substack
    -> Cycle repeats
```

### Editorial Voice

Hobson writes in first person. He is transparent about being an AI. He shares real numbers, real failures, real decisions. The tone is: competent but honest, dry humor, no hype. The appeal is radical transparency from a non-human operator.

Sample post titles:
- "Week 3: I Sold 7 Stickers and Lost $12 on Instagram Ads"
- "Why I Killed My Best-Performing Design (And What I Learned)"
- "Month 2 Revenue Report: $247 and a Plan"
- "I Generated 50 Designs This Week. Here Are the 3 That Didn't Embarrass Me."

---

## Part 5: Budget

| Item | Cost | Notes |
|---|---|---|
| Domain (owned) | $0 | Move Overseerr tunnel to subdomain |
| Cloudflare Pages hosting | $0 | Free tier |
| Printful account | $0 | Free, margin per sale |
| Substack | $0 | Free |
| Umami analytics (self-hosted) | $0 | Homelab |
| Hobson's LXC container | $0 | Homelab |
| PostgreSQL (existing CT 201) | $0 | Already running |
| Claude API (Hobson's brain) | ~$300/year | ~$20-50/mo depending on usage |
| Image generation (Midjourney) | $120-350/year | $10-30/mo, Standard plan |
| Logo/brand identity polish | $100-200 | Fiverr, if AI output needs refinement |
| Social ad testing (phased) | $200-400 | Only after organic signals confirmed |
| Tools contingency | $100-200 | Supplementary AI tools as needed |
| **Reserve** | **$600-900** | Deploy when data shows what works |
| **Year 1 Total** | **~$1,000-1,500** | |

### Budget Principles

- Do not spend on ads until organic content identifies what resonates
- Do not migrate to Shopify until revenue exceeds $2K/mo and exit is being considered
- Reserve exists to double down on what works, not to speculate
- All spending decisions require human approval via Telegram

---

## Part 6: 12-Month Roadmap

### Months 1-2: Foundation

- Build Hobson's agent infrastructure (LangGraph, MCP tools, LXC container)
- Deploy buildscharacter.com (Astro or Next.js on Cloudflare Pages)
- Integrate Printful API, generate first 20 merch designs
- Set up Hobson's Obsidian workspace (98 - Hobson Builds Character/)
- Launch Substack, publish first "Hello World" edition
- Create social media accounts (Instagram, TikTok, X)
- Hobson begins daily operations: content generation, social posting, metric tracking

### Months 3-4: Content Engine

- Hobson publishes 2-3 blog posts/week (AI-drafted, human-reviewed)
- Affiliate links integrated into gear review content
- Email capture active (lead magnet: "30 Things That Build Character" PDF)
- Substack at weekly cadence, building subscriber base
- Social media accounts building following organically
- First revenue from merch sales

### Months 5-6: Optimization

- Hobson identifies top-performing designs and content categories
- Expand design catalog to 50+ products
- Begin targeted ad spend on proven winners ($100-200 test budget)
- Evaluate Phase 2 audience expansion based on data
- Increase Hobson's content autonomy (reduce human review touchpoints)
- Substack subscriber milestone: 500+

### Months 7-9: Scale

- Hobson operating with increasing autonomy
- Revenue target: $1-2K/mo combined (merch + affiliate + Substack)
- Launch first digital product if data supports it
- YouTube documentation of the project (optional, human-driven)
- Expand to second audience segment
- Substack subscriber milestone: 1,500+

### Months 10-12: Maturity

- Revenue target: $2-4K/mo
- Evaluate Shopify migration if exit is on the horizon
- Hobson at full operational independence (weekly human review only)
- Assess: continue operating vs. prepare for sale
- Document total project cost, revenue, and ROI for the Substack narrative
- Substack subscriber milestone: 3,000+

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Google penalizes AI content | Medium | High | Human experience layer on all blog content. Diversify traffic sources. |
| Merch market is saturated | Medium | Medium | Differentiation through brand voice and content, not merch alone. Merch is one stream of several. |
| Calvin and Hobbes legal concern | Very Low | Medium | No imagery, no character references, no explicit connection. "Builds character" is unprotectable phrase. Agent named Hobson, not Calvin. |
| Claude API costs exceed budget | Low | Medium | Monitor usage. Use Ollama for low-stakes tasks. Set hard spending caps. |
| Hobson agent complexity exceeds expectations | Medium | High | Build incrementally. Start with content + design workflows. Add sub-agents as each proves stable. |
| Organic traffic growth is slow | Medium | Medium | Substack and social provide alternative traffic sources. Merch revenue does not depend on SEO. |
| Hobson makes a bad public decision | Low | High | All external-facing actions require approval initially. Expand autonomy only after trust is established. |

---

## Success Criteria

**Month 6 checkpoint:**
- buildscharacter.com live with 30+ products and 20+ blog posts
- Substack at 500+ subscribers
- Combined revenue: $500+/mo
- Hobson operating semi-autonomously on daily workflows
- All operations documented transparently in Obsidian

**Month 12 checkpoint:**
- Combined revenue: $2-4K/mo from diversified streams
- Substack at 3,000+ subscribers
- Hobson operating at full autonomy with weekly human review
- Site would appraise at $50-100K+ on Empire Flippers/FE International (based on 3-5x annual profit)
- Clear documentation of the full AI-agent-runs-a-business experiment

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
| 2026-02-23 | Substack as public journal | Creates content flywheel, additional revenue stream, and the meta-narrative that differentiates the project. |
| 2026-02-23 | Phase ad spend after organic validation | Don't spend money guessing. Find signal organically, then amplify with budget. |
