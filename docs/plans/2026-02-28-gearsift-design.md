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

**Resource isolation (bootstrap phase):** Separate LXC containers for the API and batch processing jobs (scraping, LLM extraction, feed ingestion). Prevents a large data job from spiking CPU/RAM and degrading user-facing API performance.

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
  - current_price, last_price_check, in_stock (boolean)

affiliate_clicks
  - id, product_id, retailer_id, clicked_at, referrer_url, advisor_profile_id (nullable)

retailers
  - id, name (REI, Amazon, Backcountry, etc.)
  - affiliate_program, commission_rate

reviewers
  - id, name, channel_url, platform (youtube/reddit/etc)
  - specialty_tags (text[]: "ultralight", "budget", "big-and-tall", "thru-hiking", etc.)

product_sentiment
  - product_id, reviewer_id, source_type
  - source_url
  - pros (text[]), cons (text[])
  - extracted_at

kits
  - id, name, slug, description
  - activity_type, season, budget_tier, target_weight
  - curated_by (system/user in future phases)
  - created_at, updated_at

kit_items
  - kit_id, product_id, category_id
  - reasoning (why this product in this kit)

extraction_failures (dead letter queue)
  - id, product_id, source_url, extraction_type (spec/sentiment)
  - raw_input, error_message, attempts
  - status (pending/resolved/manual_review)
  - created_at, resolved_at

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

### Schema Management & Versioning

Category spec schemas are versioned JSON Schema files stored in the repository (e.g., `schemas/tents.v1.json`). The `categories` table references a specific schema version.

**Schema change process:**
1. Create new version file (`tents.v2.json`) with the added/modified fields
2. Write a migration script that identifies products on the old version and attempts to backfill the new fields (via Tier 2 spec enrichment or manual entry)
3. Products with missing values for new fields get `null` (not excluded from results, just displayed as "Not available")
4. Update category to reference new schema version
5. Hobson monitors backfill progress and flags products still missing the new field

## Data Pipeline

### Tier 1: Affiliate Product Feeds (AvantLink)

Primary data source. Both REI and Backcountry run affiliate programs through AvantLink, which provides daily-updated product data feeds (CSV, XML, tab-delimited).

- Daily sync: download feed, parse, upsert into PostgreSQL
- Provides: product name, brand, category, price, description, product URL, affiliate URL, images
- Filterable by brand, department, category, sub-category
- Backcountry catalog: 500k+ products
- This is the day-one data source. No scraping required to launch.
- **Adapter architecture:** The feed ingestion pipeline is built with a provider-agnostic adapter pattern. Each affiliate network (AvantLink, CJ, ShareASale) gets its own adapter that normalizes feed data into the shared product schema. Adding a new network means writing a new adapter, not rearchitecting the pipeline. This mitigates single-source dependency on AvantLink.

### Tier 2: Spec Enrichment (Targeted)

Affiliate feeds provide descriptions but may lack structured specs (weight, packed dimensions, fabric denier, etc.). For products in active categories:

- Hit manufacturer spec pages for specific products (targeted, low-volume: ~100-200 products)
- LLM extraction via Ollama (CT 205) or Gemini Flash: HTML to structured JSON matching category spec_schema
- One-time per product, refresh monthly
- Surgical, not bulk. No proxy infrastructure needed for this volume.
- Failed extractions go to a dead letter queue (`extraction_failures` table) for manual review or retry with adjusted prompts.
- Hobson's "self-healing" is realistic only for prompt drift (adjusting extraction prompts). Page structure changes that break the pre-processor require manual intervention. The dead letter queue ensures nothing is silently lost.

### Tier 3: YouTube Sentiment

Aggregate community sentiment from top outdoor gear YouTubers.

- Curated list of 20-30 gear review channels, each tagged by specialty (ultralight, budget, thru-hiking, car camping, big-and-tall, etc.)
- Transcript extraction via existing YouTube pipeline (CT 202)
- Gemini Flash for structured extraction: product-specific pros and cons
- Map sentiment back to products in database via reviewer_id
- Weekly batch job
- Reviewer specialty tags add context to sentiment display: "Reviewers focused on ultralight backpacking praised this tent's low weight"

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

### Decision tree implementation:

Decision trees are defined in YAML config files, one per entry path. Each file specifies questions, possible answers, branching logic, and scoring modifications. This makes the advisor logic inspectable, modifiable, and extensible without code changes.

```yaml
# Example: advisor/trees/single-tent.yaml
entry: "I need a tent"
questions:
  - id: capacity
    text: "How many people?"
    options: [1, 2, 3-4, 5+]
    next: use_type
  - id: use_type
    text: "Backpacking or car camping?"
    options: [backpacking, car_camping]
    scoring_mods:
      backpacking: { weight_priority: +3 }
    next: budget
  - id: budget
    text: "What's your budget?"
    options: [under_150, 150_300, 300_500, no_limit]
    next: results
```

### Recommendation engine:

Rules-based scoring, not ML. Each product scored against the advisor profile:
- Activity match
- Budget fit
- Experience alignment
- Season match
- Weight score (weighted by stated priority)

Products ranked per category, top pick + 1-2 alternatives. Scoring is transparent, debuggable, tunable. When a recommendation is wrong, adjust a weight or add a rule. No black box.

**Scoring transparency for users:** The recommendation output shows the score breakdown per product, surfacing why a product was chosen and the trade-offs vs alternatives:
- "Nemo Hornet Elite 2P: Weight 10/10, Budget 7/10, Capacity 9/10, Overall Fit 9.2"
- "We chose this because your top priority was weight. The trade-off is durability; the fabrics are thinner than the Big Agnes Copper Spur, which scores higher if you're hard on your gear."

The scoring engine surfaces the delta between top picks, not just the winner. This is a major trust builder and differentiator.

**Out-of-stock handling:** Products marked `in_stock = false` are deprioritized in recommendations. If a top pick is out of stock everywhere, the next alternative is promoted with a note: "Our top pick (X) is currently out of stock. Here's the next best option."

### Affiliate link cloaking & tracking:

All affiliate links route through `gearsift.com/go/<product-slug>/<retailer>` which:
1. Logs the click to `affiliate_clicks` table (product, retailer, timestamp, referrer, advisor profile if applicable)
2. Redirects to the retailer's affiliate URL
3. Enables internal click analytics without depending on affiliate network reporting

### Output:
- Personalized gear list organized by category
- Each recommendation: product, score breakdown, why it fits, trade-offs vs alternatives, key specs, pros/cons from reviewers, affiliate links to 1-3 retailers with stock status
- Shareable via URL (no account needed)
- Phase 5: save to wishlist, price alerts

## Reviewer Attribution (Rotten Tomatoes Model)

Product pages include a "What Reviewers Are Saying" section:
- Reviewer name + channel link + video link
- 1-2 sentence paraphrased takeaway (never verbatim transcript quotes)
- Pros/cons tagged to specific reviewer
- Aggregate sentiment across reviewers (e.g., "4 of 5 reviewers highlighted weight as a strength")

Always attributed, always linked. Drives traffic to reviewers. Positions GearSift as an aggregator, not an author.

### Data Corrections

Every product page includes a subtle "Suggest a correction" link. Opens a simple form: which spec is wrong, what the correct value is, and a source URL. Creates a free QA pipeline from engaged users. Corrections go to a review queue (Hobson can flag obvious spam, human approves).

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
- Kit pages as high-value SEO landing pages (see Kits section below)
- Guide pages are written sparingly, only when data pages can't cover the search intent
- Astro static generation = pre-rendered HTML, fast, crawlable
- JSON-LD structured data on product pages
- Auto-generated sitemap from product database
- No blog for blog's sake. Every page exists because the data justifies it.

**Category page experience (beyond product lists):**
- Interactive data views: weight vs price scatter plots, filterable by construction type/material/season
- Pre-built filter combinations surfacing the structured data ("Lightest tents under $300", "3-season sleeping bags by warmth rating")
- Category pages are data discovery tools, not just product grids

## Kits (First-Class Object)

Curated gear kits are elevated from an advisor output to a standalone feature with their own pages, SEO presence, and shareable URLs.

**Examples:**
- `/kits/beginner-backpacking-under-500` - "Complete Backpacking Kit Under $500"
- `/kits/ultralight-thru-hiking` - "Sub-12lb Thru-Hiking Setup"
- `/kits/pacific-northwest-3-season` - "PNW 3-Season Backpacking Kit"

Each kit page shows: all items with specs, total weight, total cost, why each item was chosen, and affiliate links for every product. Shareable and bookmarkable.

Initially curated (system-generated from advisor logic for common profiles). Kit builder advisor path outputs can be saved as kits. Future phases could open kit creation to users.

Kits are high-value SEO targets. "Backpacking gear list for beginners" and "ultralight backpacking gear list" are real search queries with buying intent.

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

**Launch criteria per category:** Not just product count but advisor-path coverage. Before launching the advisor for a category, manually run through the top 80% of likely quiz combinations and confirm the database returns a credible, defensible result for each. If it doesn't, that category needs more data before the advisor supports it. Product browsing and comparison can go live with fewer products; the advisor needs density.

Categories expand based on data and user demand, not assumptions.

## Hobson's Role

Hobson is not the builder. Claude Code builds the platform. Hobson operates:

- **Data quality monitoring:** Feed sync health, spec extraction failures, stale data detection
- **Self-healing extraction:** Fix broken LLM extraction prompts, retry failures
- **Operational monitoring:** Affiliate link health, broken URLs, price anomalies
- **Morning briefing:** Data quality metrics, sync status, flagged products
- **Substack materials:** Operational section for the dual-voice newsletter
- **Merch operations:** Existing Printful pipeline continues if merch stays in scope

The agent excels at ongoing operational monitoring, not one-time construction.

### Public Data Quality Page

`gearsift.com/status` displays live operational metrics:
- "4,120 products with verified specs"
- "Prices updated within the last 24 hours for 98.7% of products"
- "Last AvantLink feed sync: 2 hours ago"
- Spec coverage percentages per category

Radical transparency about data operations. Differentiator for a data platform and aligns with the Substack's transparency narrative.

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

## Gemini Adversarial Review (2026-02-28)

Reviewed by Gemini 2.5 Pro. Findings and dispositions:

**Incorporated:**
- **[CRITICAL] spec_schema management undefined:** Added schema versioning strategy (versioned JSON files, migration scripts, backfill process).
- **[IMPORTANT] Data pipeline brittleness:** Added dead letter queue (`extraction_failures` table), clarified Hobson's self-healing scope (prompt drift only, not page restructuring).
- **[IMPORTANT] Cold start problem:** Launch criteria changed from product count to advisor-path coverage (top 80% of quiz combinations must return credible results).
- **[IMPORTANT] Recommendation "why" under-specified:** Added score breakdown display and trade-off surfacing between top picks.
- **[IMPORTANT] Decision tree implementation vague:** Added YAML config-based decision tree structure with example.
- **[IMPORTANT] Missing in_stock + link cloaking:** Added `in_stock` field, out-of-stock handling in recommendations, `affiliate_clicks` table, and `/go/` redirect for click tracking.
- **[IMPORTANT] AvantLink dependency:** Added adapter pattern architecture for feed ingestion, making new network integration a new adapter not a rewrite.
- **[IMPORTANT] Expose scoring to users:** Added transparent score breakdown in recommendation output.
- **[CONSIDER] Resource contention:** Added resource isolation (separate containers for API and batch jobs).
- **[CONSIDER] Browser persona underserved:** Added data visualization and interactive filtering on category pages.
- **[CONSIDER] Reviewer sentiment bias:** Added reviewer specialty tags and contextual sentiment display.
- **[CONSIDER] Kits as first-class objects:** Added Kits section with own data model, pages, SEO strategy, and shareable URLs.
- **[CONSIDER] User-submitted data corrections:** Added "Suggest a correction" feature on product pages.
- **[CONSIDER] Public data quality status page:** Added `/status` page with live operational metrics.

**Declined:**
- **[CRITICAL] Homelab SPOF:** Accepted risk for bootstrap phase. User made deliberate decision to validate on homelab before paying for cloud. Migration trigger (10 conversions) is defined.
- **[CRITICAL] Over-reliance on Claude Code:** Generic AI risk warning. User is the architect directing implementation, not blindly accepting output. Not specific to this design.
