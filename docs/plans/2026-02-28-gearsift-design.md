# GearSift Design Document

**Date:** 2026-02-28
**Status:** Approved
**Domain:** gearsift.com
**Repository:** TBD (new repo, separate from builds-character)

## Context

BuildsCharacter.com launched as a philosophy/merch brand operated by an autonomous AI agent (Hobson). After iterating through two brand pivots (humor to composure to broader philosophy), the core problem became clear: a content brand with no subject matter has nothing to write about. The Substack documenting the build is the primary career asset; the brand site needs to be something worth documenting.

GearSift is a pivot from content brand to data platform: an outdoor gear advisor that helps people decide what to buy based on their specific needs. The Babylist model applied to outdoor gear. The Substack continues documenting the build, now with a genuinely compelling product at the center.

## Product Vision

GearSift answers one question: **"What should I buy?"**

Users describe their situation (activity type, experience level, budget, conditions). The platform returns a personalized gear list with structured specs, community sentiment from YouTube reviewers, and affiliate links to purchase.

**What it is:**
- A recommendation engine backed by a structured gear database
- A comparison tool with normalized, filterable specs across categories
- An affiliate business that earns commission by helping people make good decisions

**What it is not:**
- A review site (no editorial opinions, no "we tested this for 3 months")
- A marketplace (no direct purchasing, click-through to retailers)
- A community/forum (no UGC in early phases)

**Core differentiator:** Nobody has built a structured, queryable database of outdoor gear specs with a personalized recommendation layer on top. Review sites have opinions. Retailers have product listings. Nobody has the data layer in between.

**Revenue target:** $50k/year in affiliate revenue. Achievable at 5,600-18,800 monthly visitors depending on conversion rates. This is a math problem, not a moonshot.

**Reference models:**
- Babylist: guided discovery, curated lists, affiliate monetization
- PCPartPicker: structured specs, kit building, price tracking
- Rotten Tomatoes: aggregated reviewer sentiment with attribution and links

## Architecture

### Backend: Python + FastAPI
- REST API serving the frontend
- Async for scraping pipelines and DB queries
- Pydantic models for data validation (gear specs are schema-heavy)

### Database: PostgreSQL (CT 201, `gearsift` schema)
- Relational for shared attributes (brands, categories, retailers)
- JSONB for category-specific specs (tent specs differ from headlamp specs)
- Category-level spec schemas define what attributes each category tracks

### Frontend: Astro + React Islands
- Astro on Cloudflare Pages (first-class support, no adapter hacks)
- Static generation for product/category pages (SEO critical)
- React islands for interactive components (advisor quiz, comparison tool)
- API calls to FastAPI backend for dynamic content

### Hosting: Homelab Bootstrap, Cloud Migration on Traction

**Bootstrap phase:**

| Layer | Where | Cost |
|-------|-------|------|
| Frontend | Cloudflare Pages | Free |
| Backend API | LXC on Loki via Cloudflare Tunnel | Free |
| Database | PostgreSQL CT 201 | Free |
| Scraping/batch jobs | Same LXC container | Free |
| Domain | gearsift.com | ~$10/year |

**Post-validation (triggered by 10 affiliate conversions):**

| Layer | Where | Est. Cost |
|-------|-------|-----------|
| Frontend | Cloudflare Pages (unchanged) | Free |
| Backend API | Railway, Render, or AWS | $7-20/mo |
| Database | Managed PostgreSQL | $10-20/mo |

Dockerized from day one for portability. Migration is re-pointing Cloudflare DNS from tunnel to cloud provider.

## Data Model

```
categories
  - id, name, slug, parent_id (hierarchical: Shelter > Tents > Ultralight)
  - spec_schema (JSON schema defining what specs this category tracks)

brands
  - id, name, slug, website_url, logo_url

products
  - id, brand_id, category_id, name, slug
  - msrp, weight_oz, description
  - specs (JSONB, validated against category spec_schema)
  - status (active/discontinued/draft)
  - created_at, updated_at, last_verified_at

product_retailers
  - product_id, retailer_id, url, affiliate_url
  - current_price, last_price_check

retailers
  - id, name (REI, Amazon, Backcountry, etc.)
  - affiliate_program, commission_rate

product_sentiment
  - product_id, source_type (youtube/reddit/etc)
  - source_url, reviewer_name, reviewer_channel_url
  - pros (text[]), cons (text[])
  - extracted_at

advisor_profiles
  - id, activity_type, experience_level, budget_range
  - season, trip_duration, weight_priority, group_size
  - created_at (no user account needed initially)

advisor_recommendations
  - profile_id, product_id, category_id
  - rank, reasoning

wishlists (phase 5)
price_history (phase 5)
```

Adding a new category is a data task (define spec_schema, ingest products), not a code change.

## Data Pipeline

### Tier 1: Affiliate Product Feeds (AvantLink)

Primary data source. Both REI and Backcountry run affiliate programs through AvantLink, which provides daily-updated product data feeds (CSV, XML, tab-delimited).

- Daily sync: download feed, parse, upsert into PostgreSQL
- Provides: product name, brand, category, price, description, product URL, affiliate URL, images
- Filterable by brand, department, category, sub-category
- Backcountry catalog: 500k+ products
- This is the day-one data source. No scraping required to launch.

### Tier 2: Spec Enrichment (Targeted)

Affiliate feeds provide descriptions but may lack structured specs (weight, packed dimensions, fabric denier, etc.). For products in active categories:

- Hit manufacturer spec pages for specific products (targeted, low-volume: ~100-200 products)
- LLM extraction via Ollama (CT 205) or Gemini Flash: HTML to structured JSON matching category spec_schema
- One-time per product, refresh monthly
- Surgical, not bulk. No proxy infrastructure needed for this volume.

### Tier 3: YouTube Sentiment

Aggregate community sentiment from top outdoor gear YouTubers.

- Curated list of 20-30 gear review channels
- Transcript extraction via existing YouTube pipeline (CT 202)
- Gemini Flash for structured extraction: product-specific pros and cons
- Map sentiment back to products in database
- Weekly batch job

### Data Quality (Hobson)

- Monitor feed sync health (download success, row count drift)
- Monitor spec extraction failures (page structure changes, extraction quality)
- Fix extraction prompts when LLM output drifts (not just alert, actually adjust and retry)
- Flag products with missing specs or stale sentiment
- Report data quality metrics in morning briefing via Telegram

## Advisor Flow

The advisor is an adaptive decision tree, not a linear quiz. Each answer determines the next question. Short paths (2-3 questions) for focused needs, longer paths (4-5 questions) for kit building.

### Entry paths:

**Single item:** "I need a tent"
- How many people? > Backpacking or car camping? > Budget? > Done. 3 questions.

**Kit builder:** "I'm building a kit for my first backpacking trip"
- Budget for whole setup? > When are you going? > What do you already own? > Done. Show full gear list.

**Browser:** "I'm just looking"
- Skip quiz entirely, browse categories and products.

### UX principles:
- Never more questions than the path requires
- Every answer visibly refines the results
- "Skip" always available, defaults exist for every path
- No account wall, no email gate
- Feels like a knowledgeable friend at REI, not a lead capture form

### Recommendation engine:

Rules-based scoring, not ML. Each product scored against the advisor profile:
- Activity match
- Budget fit
- Experience alignment
- Season match
- Weight score (weighted by stated priority)

Products ranked per category, top pick + 1-2 alternatives. Scoring is transparent, debuggable, tunable. When a recommendation is wrong, adjust a weight or add a rule. No black box.

### Output:
- Personalized gear list organized by category
- Each recommendation: product, why it fits, key specs, pros/cons from reviewers, affiliate links to 1-3 retailers
- Shareable via URL (no account needed)
- Phase 5: save to wishlist, price alerts

## Reviewer Attribution (Rotten Tomatoes Model)

Product pages include a "What Reviewers Are Saying" section:
- Reviewer name + channel link + video link
- 1-2 sentence paraphrased takeaway (never verbatim transcript quotes)
- Pros/cons tagged to specific reviewer
- Aggregate sentiment across reviewers (e.g., "4 of 5 reviewers highlighted weight as a strength")

Always attributed, always linked. Drives traffic to reviewers. Positions GearSift as an aggregator, not an author.

## SEO & Discovery

Every piece of structured data becomes a search entry point.

| Page Type | Example | Search Intent |
|-----------|---------|---------------|
| Category landing | /tents | "best backpacking tents" |
| Product page | /tents/nemo-hornet-elite-2p | "nemo hornet elite 2p specs" |
| Comparison | /compare/nemo-hornet-vs-big-agnes-copper-spur | "nemo hornet vs big agnes" |
| Advisor | /advisor | "what backpacking gear do I need" |
| Guide | /guides/first-backpacking-trip | "backpacking gear list beginners" |

- Product pages with structured specs rank for long-tail queries review sites don't target
- Comparison pages are auto-generated from database for top product pairs per category
- Guide pages are written sparingly, only when data pages can't cover the search intent
- Astro static generation = pre-rendered HTML, fast, crawlable
- JSON-LD structured data on product pages
- Auto-generated sitemap from product database
- No blog for blog's sake. Every page exists because the data justifies it.

## Starting Categories

Initial set (flexible, informed by AvantLink feed coverage and product depth):
- Tents
- Sleeping bags
- Sleeping pads
- Trail running shoes
- Backpacks
- Headlamps
- Backpacking meals
- Hiking socks
- Hiking/trekking poles

Target: 10+ products from 5+ brands per category before launch. Categories expand based on data and user demand, not assumptions.

## Hobson's Role

Hobson is not the builder. Claude Code builds the platform. Hobson operates:

- **Data quality monitoring:** Feed sync health, spec extraction failures, stale data detection
- **Self-healing extraction:** Fix broken LLM extraction prompts, retry failures
- **Operational monitoring:** Affiliate link health, broken URLs, price anomalies
- **Morning briefing:** Data quality metrics, sync status, flagged products
- **Substack materials:** Operational section for the dual-voice newsletter
- **Merch operations:** Existing Printful pipeline continues if merch stays in scope

The agent excels at ongoing operational monitoring, not one-time construction.

## Substack Integration

The Substack (documenting the build) continues unchanged. GearSift gives it dramatically better material:

- "How I built a gear recommendation engine with affiliate feed data"
- "What 500k products in a database taught me about outdoor gear pricing"
- "The scoring engine: how GearSift decides what to recommend"
- Every phase, pivot, and metric is Substack content

The dual-voice structure (Michael's strategic frame + Hobson's operational report) applies. Michael writes about product decisions and data platform architecture. Hobson reports operational metrics and data quality.

## Phasing

### Phase 1: Foundation + Data
- Register gearsift.com, DNS on Cloudflare
- Provision LXC container on Loki
- PostgreSQL schema on CT 201
- AvantLink affiliate signup (REI + Backcountry)
- Feed ingestion pipeline
- Select starting categories, curate initial product set (~100 products)
- FastAPI backend with product/category API endpoints
- Astro site on Cloudflare Pages
- Product pages and category listings generated from database
- **Deliverable:** Live site with browsable products and affiliate links.

### Phase 2: Advisor
- Adaptive quiz flow (React island)
- Scoring engine on backend
- Decision tree per entry path
- Recommendation output with affiliate links
- Shareable results via URL
- **Deliverable:** Core product. Personalized gear recommendations.

### Phase 3: Spec Enrichment + Sentiment
- Targeted spec scraping from manufacturer pages
- LLM extraction pipeline (Ollama/Gemini Flash)
- YouTube reviewer list curation
- Transcript extraction via existing pipeline (CT 202)
- Sentiment extraction, "What Reviewers Are Saying" on product pages
- **Deliverable:** Rich, differentiated product pages.

### Phase 4: Comparison + SEO
- Auto-generated comparison pages
- JSON-LD structured data
- Auto-generated sitemap
- Guide pages for high-value search intents (3-5 to start)
- **Deliverable:** SEO flywheel starts. Search-driven traffic.

### Phase 5: Wishlists + Price Tracking
- Lightweight user accounts (email-only)
- Save gear lists to wishlist
- Price history from affiliate feeds
- Price drop alerts via email
- **Deliverable:** Retention mechanism.

### Phase 6: AWS Migration
- Triggered by 10 affiliate conversions
- Dockerize and deploy to cloud
- Migrate database to managed PostgreSQL
- Re-point Cloudflare DNS
- Frontend unchanged

### Explicitly Deferred
- Community features (user reviews, shared lists)
- Mobile app
- Additional affiliate networks beyond AvantLink
- ML-based recommendations
- Categories beyond initial set (expand from data)

## What Happens to BuildsCharacter.com

BuildsCharacter.com and the Hobson agent infrastructure are separate from GearSift. The existing codebase, brand, and agent continue to exist. Whether to maintain, archive, or repurpose them is a separate decision that doesn't block GearSift development.

## Affiliate Revenue Model

| Metric | Conservative | Moderate |
|--------|-------------|----------|
| Avg commission per conversion | $30 | $50 |
| Conversions needed/month for $50k/yr | 140 | 84 |
| Advisor conversion rate | 3% | 5% |
| Monthly visitors needed | ~18,800 | ~5,600 |

Key affiliate programs:
- REI: up to 5% commission, 15-day cookie (via AvantLink)
- Backcountry: 4-12% sliding scale (via AvantLink)
- Patagonia: 8%, 60-day cookie
- Hyperlite Mountain Gear: 10%, avg sale ~$350
