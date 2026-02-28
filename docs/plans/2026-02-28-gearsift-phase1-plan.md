# GearSift Phase 1: Foundation + Data - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deploy a live outdoor gear advisor site with browsable product pages, category listings, and affiliate links, backed by a FastAPI backend and AvantLink product feed data.

**Architecture:** Astro static site on Cloudflare Pages talks to a FastAPI backend on a Loki LXC container (exposed via Cloudflare Tunnel). Product data comes from AvantLink affiliate feeds (REI + Backcountry), ingested daily into PostgreSQL on CT 201. Affiliate URLs are baked directly into static HTML (not routed through the API) so revenue is never blocked by homelab downtime. Click tracking via lightweight client-side JS or Cloudflare Worker.

**Tech Stack:** Python 3.11, FastAPI, asyncpg, Pydantic, PostgreSQL 16, Astro 5, Tailwind CSS 4, Cloudflare Pages, Cloudflare Tunnel, Docker (prepared, not required for bootstrap)

**Design Doc:** `docs/plans/2026-02-28-gearsift-design.md`

**New Repository:** `gearsift` (separate from builds-character)

---

## Task 1: Project Scaffold

**Files:**
- Create: `gearsift/` (new repo root)
- Create: `gearsift/backend/pyproject.toml`
- Create: `gearsift/backend/src/gearsift/__init__.py`
- Create: `gearsift/backend/src/gearsift/config.py`
- Create: `gearsift/site/` (Astro project, generated)
- Create: `gearsift/sql/` (migration directory)
- Create: `gearsift/schemas/` (category spec schemas)
- Create: `gearsift/.gitignore`
- Create: `gearsift/docker-compose.yml` (skeleton)
- Create: `gearsift/PROJECT.md`
- Create: `gearsift/STATE.md`

**Step 1: Create repo and directory structure**

```bash
cd /Users/llama/Development
mkdir -p gearsift/{backend/src/gearsift,backend/tests,sql,schemas,site,docs/plans}
cd gearsift
git init
```

**Step 2: Write .gitignore**

```gitignore
# Python
__pycache__/
*.pyc
.venv/
*.egg-info/
dist/
build/

# Node
node_modules/
site/dist/
site/.astro/

# Environment
.env
.env.local

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store
```

**Step 3: Write pyproject.toml**

```toml
[project]
name = "gearsift"
version = "0.1.0"
description = "Outdoor gear advisor platform"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "asyncpg>=0.30",
    "pydantic>=2.10",
    "pydantic-settings>=2.6",
    "httpx>=0.28",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "pytest-httpx>=0.35",
    "ruff>=0.8",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/gearsift"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
target-version = "py311"
line-length = 100
```

**Step 4: Write config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://gearsift:gearsift@192.168.2.67:5432/project_data"
    api_host: str = "0.0.0.0"
    api_port: int = 8200
    site_url: str = "https://gearsift.com"
    avantlink_api_key: str = ""
    avantlink_affiliate_id: str = ""
    cors_origins: list[str] = ["https://gearsift.com", "http://localhost:4321"]

    model_config = {"env_prefix": "GEARSIFT_", "env_file": ".env"}


settings = Settings()
```

**Step 5: Write PROJECT.md and STATE.md**

PROJECT.md:
```markdown
# GearSift

## Goal

Outdoor gear advisor platform that helps people decide what to buy. Babylist model: guided discovery, curated recommendations, affiliate links. Revenue through affiliate commissions (REI, Backcountry via AvantLink).

## Tech Stack

- **Backend:** Python 3.11, FastAPI, asyncpg, Pydantic
- **Database:** PostgreSQL 16 (CT 201, `gearsift` schema on `project_data` database)
- **Frontend:** Astro 5, React islands, Tailwind CSS 4, Cloudflare Pages
- **Data:** AvantLink product feeds (REI, Backcountry), YouTube transcripts for sentiment
- **Infrastructure:** LXC containers on Loki (API + batch), Cloudflare Tunnel
- **Monitoring:** Hobson agent for data quality, Uptime Kuma for health

## Architecture

Astro static site on Cloudflare Pages serves product/category pages (pre-rendered for SEO). React islands handle interactive advisor quiz. FastAPI backend provides API for dynamic content, affiliate link tracking, and feed ingestion. AvantLink product feeds are the primary data source, synced daily. Category-specific specs stored as JSONB validated against versioned JSON schemas.

## Constraints

- Bootstrap on homelab infrastructure (~$10/year). Migrate to cloud after 10 affiliate conversions.
- No ML. Rules-based scoring engine for recommendations.
- Start with 9 categories. Expand from data, not assumptions.
- Adapter pattern for feed ingestion (AvantLink first, extensible to CJ/ShareASale).

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-28 | Pivot from BuildsCharacter philosophy brand to GearSift data platform | Content brand with no subject matter has nothing to write about. Gear advisor has genuine utility and affiliate revenue potential. |
| 2026-02-28 | Astro + React islands over Next.js | First-class Cloudflare Pages support, static gen for SEO, React only where needed. |
| 2026-02-28 | AvantLink feeds over scraping | Sanctioned data source, no proxy infrastructure needed, includes affiliate URLs. |
| 2026-02-28 | Rules-based scoring over ML | Transparent, debuggable, tunable. ML only if rules aren't good enough. |
| 2026-02-28 | YAML config for advisor decision trees | Inspectable, modifiable without code changes. |
| 2026-02-28 | Separate LXC containers for API and batch jobs | Resource isolation prevents batch jobs from degrading API performance. |
```

STATE.md:
```markdown
# State

## Current Focus

Phase 1: Foundation + Data. Building the backend, database, feed ingestion, and Astro site with product/category pages.

## Status

- [ ] Project scaffolded
- [ ] PostgreSQL schema applied
- [ ] FastAPI backend running
- [ ] AvantLink feed ingestion working
- [ ] Astro site deployed to Cloudflare Pages
- [ ] Product and category pages live
- [ ] Affiliate link tracking working
- [ ] LXC containers provisioned
- [ ] Cloudflare Tunnel configured
- [ ] End-to-end integration verified

## Known Issues

None yet.

## Next Steps

1. Register gearsift.com domain
2. Sign up for AvantLink affiliate program (REI + Backcountry)
3. Scaffold project and deploy Phase 1
```

**Step 6: Write docker-compose.yml skeleton**

```yaml
services:
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8200:8200"
    env_file:
      - .env
    restart: unless-stopped

  # batch worker (Phase 1: feed ingestion, Phase 3: spec enrichment)
  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: ["python", "-m", "gearsift.ingest.cli"]
    env_file:
      - .env
    profiles:
      - batch
```

**Step 7: Initial commit**

```bash
git add -A
git commit -m "feat: project scaffold with backend, site, and infra structure"
```

---

## Task 2: PostgreSQL Schema

**Files:**
- Create: `sql/001_schema.sql`
- Create: `sql/002_seed_retailers.sql`

**Step 1: Write core schema migration**

```sql
-- sql/001_schema.sql
-- GearSift core schema for product_data database

CREATE SCHEMA IF NOT EXISTS gearsift;

-- Categories (hierarchical)
CREATE TABLE gearsift.categories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    parent_id INTEGER REFERENCES gearsift.categories(id),
    spec_schema_version TEXT NOT NULL DEFAULT 'v1',
    description TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_categories_slug ON gearsift.categories(slug);
CREATE INDEX idx_categories_parent ON gearsift.categories(parent_id);

-- Brands
CREATE TABLE gearsift.brands (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    website_url TEXT,
    logo_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_brands_slug ON gearsift.brands(slug);

-- Retailers
CREATE TABLE gearsift.retailers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    website_url TEXT NOT NULL,
    affiliate_program TEXT,
    commission_rate NUMERIC(5,2),
    cookie_days INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Products
CREATE TABLE gearsift.products (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER NOT NULL REFERENCES gearsift.brands(id),
    category_id INTEGER NOT NULL REFERENCES gearsift.categories(id),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    msrp NUMERIC(10,2),
    weight_oz NUMERIC(8,2),
    specs JSONB NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'discontinued', 'draft')),
    image_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_verified_at TIMESTAMPTZ
);

CREATE INDEX idx_products_slug ON gearsift.products(slug);
CREATE INDEX idx_products_category ON gearsift.products(category_id);
CREATE INDEX idx_products_brand ON gearsift.products(brand_id);
CREATE INDEX idx_products_status ON gearsift.products(status);
CREATE INDEX idx_products_specs ON gearsift.products USING GIN (specs);

-- Product-Retailer mapping (prices + affiliate links)
CREATE TABLE gearsift.product_retailers (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES gearsift.products(id) ON DELETE CASCADE,
    retailer_id INTEGER NOT NULL REFERENCES gearsift.retailers(id),
    url TEXT NOT NULL,
    affiliate_url TEXT NOT NULL,
    current_price NUMERIC(10,2),
    in_stock BOOLEAN NOT NULL DEFAULT true,
    last_price_check TIMESTAMPTZ,
    feed_product_id TEXT,
    UNIQUE (product_id, retailer_id)
);

CREATE INDEX idx_product_retailers_product ON gearsift.product_retailers(product_id);

-- Affiliate click tracking
CREATE TABLE gearsift.affiliate_clicks (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES gearsift.products(id),
    retailer_id INTEGER NOT NULL REFERENCES gearsift.retailers(id),
    clicked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    referrer_url TEXT,
    advisor_profile_id INTEGER
);

CREATE INDEX idx_affiliate_clicks_product ON gearsift.affiliate_clicks(product_id);
CREATE INDEX idx_affiliate_clicks_date ON gearsift.affiliate_clicks(clicked_at);

-- Reviewers
CREATE TABLE gearsift.reviewers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    channel_url TEXT NOT NULL UNIQUE,
    platform TEXT NOT NULL DEFAULT 'youtube',
    specialty_tags TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Product sentiment (from YouTube reviews)
CREATE TABLE gearsift.product_sentiment (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES gearsift.products(id) ON DELETE CASCADE,
    reviewer_id INTEGER NOT NULL REFERENCES gearsift.reviewers(id),
    source_url TEXT NOT NULL,
    pros TEXT[] NOT NULL DEFAULT '{}',
    cons TEXT[] NOT NULL DEFAULT '{}',
    extracted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (product_id, reviewer_id, source_url)
);

CREATE INDEX idx_sentiment_product ON gearsift.product_sentiment(product_id);

-- Advisor profiles (quiz results, no account needed)
CREATE TABLE gearsift.advisor_profiles (
    id SERIAL PRIMARY KEY,
    activity_type TEXT,
    experience_level TEXT,
    budget_range TEXT,
    season TEXT,
    weight_priority TEXT,
    group_size TEXT,
    owned_categories INTEGER[],
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Advisor recommendations
CREATE TABLE gearsift.advisor_recommendations (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES gearsift.advisor_profiles(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES gearsift.products(id),
    category_id INTEGER NOT NULL REFERENCES gearsift.categories(id),
    rank INTEGER NOT NULL,
    score NUMERIC(5,2),
    score_breakdown JSONB NOT NULL DEFAULT '{}',
    reasoning TEXT
);

CREATE INDEX idx_recommendations_profile ON gearsift.advisor_recommendations(profile_id);

-- Extraction failures (dead letter queue)
CREATE TABLE gearsift.extraction_failures (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES gearsift.products(id),
    source_url TEXT,
    extraction_type TEXT NOT NULL CHECK (extraction_type IN ('spec', 'sentiment')),
    raw_input TEXT,
    error_message TEXT,
    attempts INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'resolved', 'manual_review')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

CREATE INDEX idx_extraction_failures_status ON gearsift.extraction_failures(status);

-- Kits (curated gear lists)
CREATE TABLE gearsift.kits (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    activity_type TEXT,
    season TEXT,
    budget_tier TEXT,
    target_weight_oz NUMERIC(8,2),
    curated_by TEXT NOT NULL DEFAULT 'system',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_kits_slug ON gearsift.kits(slug);

-- Kit items
CREATE TABLE gearsift.kit_items (
    id SERIAL PRIMARY KEY,
    kit_id INTEGER NOT NULL REFERENCES gearsift.kits(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES gearsift.products(id),
    category_id INTEGER NOT NULL REFERENCES gearsift.categories(id),
    reasoning TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    UNIQUE (kit_id, category_id)
);

-- Data corrections (user-submitted)
CREATE TABLE gearsift.data_corrections (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES gearsift.products(id),
    field_name TEXT NOT NULL,
    current_value TEXT,
    suggested_value TEXT NOT NULL,
    source_url TEXT,
    submitter_email TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ
);

-- Feed sync log
CREATE TABLE gearsift.feed_sync_log (
    id SERIAL PRIMARY KEY,
    retailer_id INTEGER NOT NULL REFERENCES gearsift.retailers(id),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'running' CHECK (status IN ('running', 'success', 'failed')),
    products_added INTEGER DEFAULT 0,
    products_updated INTEGER DEFAULT 0,
    products_total INTEGER DEFAULT 0,
    error_message TEXT
);

-- Grant permissions
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'gearsift') THEN
        CREATE ROLE gearsift WITH LOGIN PASSWORD 'PLACEHOLDER';
    END IF;
END
$$;

GRANT USAGE, CREATE ON SCHEMA gearsift TO gearsift;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA gearsift TO gearsift;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA gearsift TO gearsift;
ALTER DEFAULT PRIVILEGES IN SCHEMA gearsift GRANT ALL ON TABLES TO gearsift;
ALTER DEFAULT PRIVILEGES IN SCHEMA gearsift GRANT ALL ON SEQUENCES TO gearsift;
```

**Step 2: Write seed data for retailers**

```sql
-- sql/002_seed_retailers.sql

INSERT INTO gearsift.retailers (name, slug, website_url, affiliate_program, commission_rate, cookie_days)
VALUES
    ('REI', 'rei', 'https://www.rei.com', 'AvantLink', 5.00, 15),
    ('Backcountry', 'backcountry', 'https://www.backcountry.com', 'AvantLink', 8.00, NULL),
    ('Amazon', 'amazon', 'https://www.amazon.com', 'Amazon Associates', 3.00, 24)
ON CONFLICT (slug) DO NOTHING;
```

**Step 3: Write initial category spec schemas**

Create `schemas/tents.v1.json`:
```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Tent Specs",
    "type": "object",
    "properties": {
        "capacity": {"type": "integer", "description": "Number of people"},
        "floor_area_sqft": {"type": "number"},
        "vestibule_area_sqft": {"type": "number"},
        "peak_height_in": {"type": "number"},
        "packed_weight_oz": {"type": "number"},
        "trail_weight_oz": {"type": "number"},
        "packed_dimensions": {"type": "string"},
        "wall_type": {"type": "string", "enum": ["single", "double"]},
        "seasons": {"type": "string", "enum": ["3-season", "4-season", "3+season"]},
        "pole_material": {"type": "string"},
        "fabric_denier": {"type": "string"},
        "vestibule_count": {"type": "integer"},
        "door_count": {"type": "integer"},
        "freestanding": {"type": "boolean"}
    }
}
```

Create `schemas/backpacks.v1.json`:
```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Backpack Specs",
    "type": "object",
    "properties": {
        "volume_liters": {"type": "number"},
        "weight_oz": {"type": "number"},
        "frame_type": {"type": "string", "enum": ["internal", "external", "frameless"]},
        "torso_range": {"type": "string"},
        "hip_belt_range": {"type": "string"},
        "fabric": {"type": "string"},
        "rain_cover_included": {"type": "boolean"},
        "hydration_compatible": {"type": "boolean"},
        "top_loading": {"type": "boolean"},
        "front_panel_access": {"type": "boolean"},
        "hip_belt_pockets": {"type": "boolean"},
        "max_carry_weight_lbs": {"type": "number"}
    }
}
```

Create `schemas/sleeping_bags.v1.json`:
```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Sleeping Bag Specs",
    "type": "object",
    "properties": {
        "temperature_rating_f": {"type": "integer"},
        "comfort_rating_f": {"type": "integer"},
        "fill_type": {"type": "string", "enum": ["down", "synthetic"]},
        "fill_power": {"type": "integer"},
        "fill_weight_oz": {"type": "number"},
        "total_weight_oz": {"type": "number"},
        "packed_dimensions": {"type": "string"},
        "shape": {"type": "string", "enum": ["mummy", "rectangular", "semi-rectangular", "quilt"]},
        "length": {"type": "string", "enum": ["regular", "long", "short"]},
        "zipper_side": {"type": "string"},
        "water_resistant": {"type": "boolean"}
    }
}
```

**Step 4: Apply schema to CT 201**

```bash
# From local machine, SSH to Freya, exec into CT 201
ssh root@192.168.2.13 'pct exec 201 -- psql -U postgres -d project_data' < sql/001_schema.sql
ssh root@192.168.2.13 'pct exec 201 -- psql -U postgres -d project_data' < sql/002_seed_retailers.sql
```

Note: Set actual password for `gearsift` role via Bitwarden. Replace PLACEHOLDER in 001_schema.sql before applying.

**Step 5: Verify and commit**

```bash
# Verify tables exist
ssh root@192.168.2.13 'pct exec 201 -- psql -U postgres -d project_data -c "SELECT table_name FROM information_schema.tables WHERE table_schema = '\''gearsift'\'' ORDER BY table_name;"'

git add sql/ schemas/
git commit -m "feat: PostgreSQL schema and category spec schemas"
```

---

## Task 3: FastAPI Backend - Database Client

**Files:**
- Create: `backend/src/gearsift/db.py`
- Create: `backend/tests/test_db.py`

**Step 1: Write the database client**

```python
# backend/src/gearsift/db.py
import asyncpg
from gearsift.config import settings


class Database:
    def __init__(self):
        self._pool: asyncpg.Pool | None = None

    async def connect(self):
        self._pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=2,
            max_size=10,
        )

    async def disconnect(self):
        if self._pool:
            await self._pool.close()

    @property
    def pool(self) -> asyncpg.Pool:
        if not self._pool:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._pool

    async def fetch(self, query: str, *args) -> list[asyncpg.Record]:
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> asyncpg.Record | None:
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    async def execute(self, query: str, *args) -> str:
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)


db = Database()
```

**Step 2: Write test**

```python
# backend/tests/test_db.py
import pytest
from gearsift.db import Database


@pytest.fixture
def database():
    return Database()


def test_pool_raises_before_connect(database):
    with pytest.raises(RuntimeError, match="Database not connected"):
        _ = database.pool
```

**Step 3: Run test**

```bash
cd backend && python -m pytest tests/test_db.py -v
```

**Step 4: Commit**

```bash
git add backend/src/gearsift/db.py backend/tests/test_db.py
git commit -m "feat: async database client with connection pooling"
```

---

## Task 4: FastAPI Backend - Models

**Files:**
- Create: `backend/src/gearsift/models.py`
- Create: `backend/tests/test_models.py`

**Step 1: Write Pydantic models**

```python
# backend/src/gearsift/models.py
from pydantic import BaseModel
from datetime import datetime


class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    parent_id: int | None
    description: str | None
    sort_order: int


class BrandOut(BaseModel):
    id: int
    name: str
    slug: str
    website_url: str | None
    logo_url: str | None


class RetailerPrice(BaseModel):
    retailer_name: str
    retailer_slug: str
    current_price: float | None
    in_stock: bool
    url: str
    affiliate_url: str


class ProductOut(BaseModel):
    id: int
    name: str
    slug: str
    brand: BrandOut
    category: CategoryOut
    description: str | None
    msrp: float | None
    weight_oz: float | None
    specs: dict
    status: str
    image_url: str | None
    retailers: list[RetailerPrice]
    updated_at: datetime


class ProductListItem(BaseModel):
    id: int
    name: str
    slug: str
    brand_name: str
    brand_slug: str
    category_slug: str
    msrp: float | None
    weight_oz: float | None
    image_url: str | None
    lowest_price: float | None
    in_stock: bool


class CategoryWithProducts(BaseModel):
    category: CategoryOut
    products: list[ProductListItem]
    total: int


class AffiliateClickOut(BaseModel):
    redirect_url: str


class FeedSyncStatus(BaseModel):
    retailer: str
    status: str
    started_at: datetime
    completed_at: datetime | None
    products_added: int
    products_updated: int
    products_total: int


class HealthOut(BaseModel):
    status: str
    version: str
    products_count: int
    categories_count: int
    last_feed_sync: FeedSyncStatus | None
```

**Step 2: Write test**

```python
# backend/tests/test_models.py
from gearsift.models import ProductListItem, CategoryOut


def test_product_list_item():
    item = ProductListItem(
        id=1,
        name="Nemo Hornet Elite 2P",
        slug="nemo-hornet-elite-2p",
        brand_name="Nemo",
        brand_slug="nemo",
        category_slug="tents",
        msrp=449.95,
        weight_oz=28.0,
        image_url=None,
        lowest_price=399.95,
        in_stock=True,
    )
    assert item.name == "Nemo Hornet Elite 2P"
    assert item.in_stock is True


def test_category_out():
    cat = CategoryOut(
        id=1, name="Tents", slug="tents", parent_id=None, description="Shelter", sort_order=0
    )
    assert cat.slug == "tents"
```

**Step 3: Run tests, commit**

```bash
cd backend && python -m pytest tests/test_models.py -v
git add backend/src/gearsift/models.py backend/tests/test_models.py
git commit -m "feat: Pydantic models for products, categories, and API responses"
```

---

## Task 5: FastAPI Backend - API Endpoints

**Files:**
- Create: `backend/src/gearsift/app.py`
- Create: `backend/src/gearsift/routes/__init__.py`
- Create: `backend/src/gearsift/routes/products.py`
- Create: `backend/src/gearsift/routes/categories.py`
- Create: `backend/src/gearsift/routes/affiliate.py`
- Create: `backend/src/gearsift/routes/health.py`
- Create: `backend/tests/test_routes.py`

**Step 1: Write the FastAPI app**

```python
# backend/src/gearsift/app.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from gearsift.config import settings
from gearsift.db import db
from gearsift.routes import products, categories, affiliate, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    yield
    await db.disconnect()


app = FastAPI(title="GearSift API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(affiliate.router, tags=["affiliate"])
```

**Step 2: Write category routes**

```python
# backend/src/gearsift/routes/categories.py
from fastapi import APIRouter, HTTPException
from gearsift.db import db
from gearsift.models import CategoryOut, CategoryWithProducts, ProductListItem

router = APIRouter()


@router.get("/", response_model=list[CategoryOut])
async def list_categories():
    rows = await db.fetch(
        "SELECT id, name, slug, parent_id, description, sort_order "
        "FROM gearsift.categories ORDER BY sort_order, name"
    )
    return [CategoryOut(**dict(r)) for r in rows]


@router.get("/{slug}", response_model=CategoryWithProducts)
async def get_category(slug: str):
    cat = await db.fetchrow(
        "SELECT id, name, slug, parent_id, description, sort_order "
        "FROM gearsift.categories WHERE slug = $1",
        slug,
    )
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    products = await db.fetch(
        """
        SELECT p.id, p.name, p.slug, b.name as brand_name, b.slug as brand_slug,
               c.slug as category_slug, p.msrp, p.weight_oz, p.image_url,
               MIN(pr.current_price) as lowest_price,
               BOOL_OR(pr.in_stock) as in_stock
        FROM gearsift.products p
        JOIN gearsift.brands b ON p.brand_id = b.id
        JOIN gearsift.categories c ON p.category_id = c.id
        LEFT JOIN gearsift.product_retailers pr ON p.id = pr.product_id
        WHERE p.category_id = $1 AND p.status = 'active'
        GROUP BY p.id, p.name, p.slug, b.name, b.slug, c.slug, p.msrp, p.weight_oz, p.image_url
        ORDER BY p.name
        """,
        cat["id"],
    )

    return CategoryWithProducts(
        category=CategoryOut(**dict(cat)),
        products=[ProductListItem(**dict(p)) for p in products],
        total=len(products),
    )
```

**Step 3: Write product routes**

```python
# backend/src/gearsift/routes/products.py
from fastapi import APIRouter, HTTPException
from gearsift.db import db
from gearsift.models import ProductOut, BrandOut, CategoryOut, RetailerPrice

router = APIRouter()


@router.get("/{category_slug}/{product_slug}", response_model=ProductOut)
async def get_product(category_slug: str, product_slug: str):
    row = await db.fetchrow(
        """
        SELECT p.id, p.name, p.slug, p.description, p.msrp, p.weight_oz,
               p.specs, p.status, p.image_url, p.updated_at,
               b.id as brand_id, b.name as brand_name, b.slug as brand_slug,
               b.website_url as brand_website, b.logo_url as brand_logo,
               c.id as cat_id, c.name as cat_name, c.slug as cat_slug,
               c.parent_id as cat_parent, c.description as cat_desc, c.sort_order
        FROM gearsift.products p
        JOIN gearsift.brands b ON p.brand_id = b.id
        JOIN gearsift.categories c ON p.category_id = c.id
        WHERE p.slug = $1 AND c.slug = $2
        """,
        product_slug,
        category_slug,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")

    retailers = await db.fetch(
        """
        SELECT r.name as retailer_name, r.slug as retailer_slug,
               pr.current_price, pr.in_stock, pr.url, pr.affiliate_url
        FROM gearsift.product_retailers pr
        JOIN gearsift.retailers r ON pr.retailer_id = r.id
        WHERE pr.product_id = $1
        ORDER BY pr.current_price ASC NULLS LAST
        """,
        row["id"],
    )

    return ProductOut(
        id=row["id"],
        name=row["name"],
        slug=row["slug"],
        description=row["description"],
        msrp=row["msrp"],
        weight_oz=row["weight_oz"],
        specs=row["specs"],
        status=row["status"],
        image_url=row["image_url"],
        updated_at=row["updated_at"],
        brand=BrandOut(
            id=row["brand_id"],
            name=row["brand_name"],
            slug=row["brand_slug"],
            website_url=row["brand_website"],
            logo_url=row["brand_logo"],
        ),
        category=CategoryOut(
            id=row["cat_id"],
            name=row["cat_name"],
            slug=row["cat_slug"],
            parent_id=row["cat_parent"],
            description=row["cat_desc"],
            sort_order=row["sort_order"],
        ),
        retailers=[RetailerPrice(**dict(r)) for r in retailers],
    )
```

**Step 4: Write affiliate click redirect**

```python
# backend/src/gearsift/routes/affiliate.py
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from gearsift.db import db

router = APIRouter()


@router.get("/go/{product_slug}/{retailer_slug}")
async def track_affiliate_click(product_slug: str, retailer_slug: str, request: Request):
    row = await db.fetchrow(
        """
        SELECT pr.affiliate_url, p.id as product_id, r.id as retailer_id
        FROM gearsift.product_retailers pr
        JOIN gearsift.products p ON pr.product_id = p.id
        JOIN gearsift.retailers r ON pr.retailer_id = r.id
        WHERE p.slug = $1 AND r.slug = $2
        """,
        product_slug,
        retailer_slug,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Product/retailer combination not found")

    # Log click asynchronously (fire and forget)
    referrer = request.headers.get("referer", "")
    await db.execute(
        """
        INSERT INTO gearsift.affiliate_clicks (product_id, retailer_id, referrer_url)
        VALUES ($1, $2, $3)
        """,
        row["product_id"],
        row["retailer_id"],
        referrer,
    )

    return RedirectResponse(url=row["affiliate_url"], status_code=302)
```

**Step 5: Write health endpoint**

```python
# backend/src/gearsift/routes/health.py
from fastapi import APIRouter
from gearsift.db import db
from gearsift.models import HealthOut

router = APIRouter()


@router.get("/health", response_model=HealthOut)
async def health_check():
    products_count = await db.fetchval("SELECT COUNT(*) FROM gearsift.products")
    categories_count = await db.fetchval("SELECT COUNT(*) FROM gearsift.categories")

    last_sync = await db.fetchrow(
        """
        SELECT r.name as retailer, fsl.status, fsl.started_at, fsl.completed_at,
               fsl.products_added, fsl.products_updated, fsl.products_total
        FROM gearsift.feed_sync_log fsl
        JOIN gearsift.retailers r ON fsl.retailer_id = r.id
        ORDER BY fsl.started_at DESC LIMIT 1
        """
    )

    return HealthOut(
        status="ok",
        version="0.1.0",
        products_count=products_count,
        categories_count=categories_count,
        last_feed_sync=dict(last_sync) if last_sync else None,
    )
```

**Step 6: Write routes __init__**

```python
# backend/src/gearsift/routes/__init__.py
```

**Step 7: Write __main__ entry point**

```python
# backend/src/gearsift/__main__.py
import uvicorn
from gearsift.config import settings

uvicorn.run("gearsift.app:app", host=settings.api_host, port=settings.api_port, reload=False)
```

**Step 8: Write API tests**

```python
# backend/tests/test_routes.py
"""
Integration tests - require running PostgreSQL with gearsift schema.
Run with: pytest tests/test_routes.py -v -m integration
Skip in CI with: pytest -m "not integration"
"""
import pytest
from httpx import AsyncClient, ASGITransport
from gearsift.app import app

pytestmark = pytest.mark.integration


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


async def test_list_categories(client):
    resp = await client.get("/api/categories/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_category_not_found(client):
    resp = await client.get("/api/categories/nonexistent")
    assert resp.status_code == 404


async def test_product_not_found(client):
    resp = await client.get("/api/products/tents/nonexistent")
    assert resp.status_code == 404


async def test_affiliate_redirect_not_found(client):
    resp = await client.get("/go/nonexistent/rei", follow_redirects=False)
    assert resp.status_code == 404
```

**Step 9: Run tests, commit**

```bash
cd backend && python -m pytest tests/test_models.py tests/test_db.py -v
git add backend/src/gearsift/ backend/tests/
git commit -m "feat: FastAPI app with product, category, affiliate, and health endpoints"
```

---

## Task 6: Feed Ingestion Pipeline

**Files:**
- Create: `backend/src/gearsift/ingest/__init__.py`
- Create: `backend/src/gearsift/ingest/base.py`
- Create: `backend/src/gearsift/ingest/avantlink.py`
- Create: `backend/src/gearsift/ingest/loader.py`
- Create: `backend/src/gearsift/ingest/cli.py`
- Create: `backend/tests/test_ingest.py`

**Step 1: Write the base adapter interface**

```python
# backend/src/gearsift/ingest/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class FeedProduct:
    """Normalized product from any affiliate feed."""
    feed_product_id: str
    name: str
    brand_name: str
    category_name: str
    description: str
    price: float | None
    msrp: float | None
    product_url: str
    affiliate_url: str
    image_url: str | None
    in_stock: bool
    retailer_slug: str


class FeedAdapter(ABC):
    """Base class for affiliate feed adapters."""

    @abstractmethod
    async def fetch_feed(self, category_filter: str | None = None) -> list[FeedProduct]:
        """Download and parse feed, returning normalized products."""
        ...

    @abstractmethod
    def retailer_slug(self) -> str:
        """Which retailer this adapter serves."""
        ...
```

**Step 2: Write the AvantLink adapter**

```python
# backend/src/gearsift/ingest/avantlink.py
import csv
import io
import httpx
from gearsift.config import settings
from gearsift.ingest.base import FeedAdapter, FeedProduct


class AvantLinkAdapter(FeedAdapter):
    """Adapter for AvantLink product data feeds (REI, Backcountry)."""

    BASE_URL = "https://classic.avantlink.com/api.php"

    def __init__(self, merchant_id: str, retailer_slug: str):
        self._merchant_id = merchant_id
        self._retailer_slug = retailer_slug

    def retailer_slug(self) -> str:
        return self._retailer_slug

    async def fetch_feed(self, category_filter: str | None = None) -> list[FeedProduct]:
        """Fetch product feed from AvantLink API.

        AvantLink provides feeds as CSV/TSV. The exact field names depend on the
        merchant's feed configuration. This adapter handles the common fields.
        Adjust field mapping after inspecting actual feed output from REI/Backcountry.
        """
        params = {
            "affiliate_id": settings.avantlink_affiliate_id,
            "module": "ProductFeed",
            "merchant_id": self._merchant_id,
            "output": "csv",
            "auth_key": settings.avantlink_api_key,
        }
        if category_filter:
            params["search_results_category"] = category_filter

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.get(self.BASE_URL, params=params)
            resp.raise_for_status()

        return self._parse_csv(resp.text)

    def _parse_csv(self, text: str) -> list[FeedProduct]:
        products = []
        reader = csv.DictReader(io.StringIO(text))
        for row in reader:
            # Field names are AvantLink standard; adjust after inspecting real feed
            product = FeedProduct(
                feed_product_id=row.get("Product_Id", row.get("SKU", "")),
                name=row.get("Product_Name", ""),
                brand_name=row.get("Brand_Name", row.get("Manufacturer", "")),
                category_name=row.get("Category", row.get("Product_Group", "")),
                description=row.get("Long_Description", row.get("Description", "")),
                price=self._parse_price(row.get("Sale_Price", row.get("Price", ""))),
                msrp=self._parse_price(row.get("Retail_Price", "")),
                product_url=row.get("Buy_Link", row.get("Product_URL", "")),
                affiliate_url=row.get("Buy_Link", ""),
                image_url=row.get("Image_URL", None),
                in_stock=row.get("In_Stock", "yes").lower() in ("yes", "true", "1"),
                retailer_slug=self._retailer_slug,
            )
            if product.name and product.feed_product_id:
                products.append(product)
        return products

    @staticmethod
    def _parse_price(val: str) -> float | None:
        if not val:
            return None
        try:
            return float(val.replace("$", "").replace(",", "").strip())
        except (ValueError, AttributeError):
            return None
```

**Step 3: Write the database loader**

```python
# backend/src/gearsift/ingest/loader.py
import re
from gearsift.db import db
from gearsift.ingest.base import FeedProduct


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


async def upsert_brand(name: str) -> int:
    slug = slugify(name)
    row = await db.fetchrow(
        """
        INSERT INTO gearsift.brands (name, slug)
        VALUES ($1, $2)
        ON CONFLICT (slug) DO UPDATE SET name = EXCLUDED.name
        RETURNING id
        """,
        name,
        slug,
    )
    return row["id"]


async def get_or_create_category(name: str) -> int | None:
    """Look up category by name. Returns None if no matching category exists.

    Categories are pre-seeded; feed categories are mapped via a config table.
    """
    slug = slugify(name)
    row = await db.fetchrow(
        "SELECT id FROM gearsift.categories WHERE slug = $1", slug
    )
    return row["id"] if row else None


async def get_retailer_id(slug: str) -> int:
    row = await db.fetchrow(
        "SELECT id FROM gearsift.retailers WHERE slug = $1", slug
    )
    if not row:
        raise ValueError(f"Retailer '{slug}' not found. Seed retailers first.")
    return row["id"]


async def load_product(product: FeedProduct, category_id: int) -> tuple[int, bool]:
    """Upsert a product and its retailer pricing. Returns (product_id, is_new)."""
    brand_id = await upsert_brand(product.brand_name)
    slug = slugify(f"{product.brand_name} {product.name}")

    # Upsert product
    existing = await db.fetchrow(
        "SELECT id FROM gearsift.products WHERE slug = $1", slug
    )

    if existing:
        product_id = existing["id"]
        await db.execute(
            """
            UPDATE gearsift.products
            SET msrp = COALESCE($2, msrp),
                description = COALESCE($3, description),
                image_url = COALESCE($4, image_url),
                updated_at = NOW(),
                last_verified_at = NOW()
            WHERE id = $1
            """,
            product_id,
            product.msrp,
            product.description,
            product.image_url,
        )
        is_new = False
    else:
        row = await db.fetchrow(
            """
            INSERT INTO gearsift.products
                (brand_id, category_id, name, slug, description, msrp, image_url, last_verified_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
            RETURNING id
            """,
            brand_id,
            category_id,
            product.name,
            slug,
            product.description,
            product.msrp,
            product.image_url,
        )
        product_id = row["id"]
        is_new = True

    # Upsert retailer pricing
    retailer_id = await get_retailer_id(product.retailer_slug)
    await db.execute(
        """
        INSERT INTO gearsift.product_retailers
            (product_id, retailer_id, url, affiliate_url, current_price, in_stock,
             last_price_check, feed_product_id)
        VALUES ($1, $2, $3, $4, $5, $6, NOW(), $7)
        ON CONFLICT (product_id, retailer_id) DO UPDATE SET
            url = EXCLUDED.url,
            affiliate_url = EXCLUDED.affiliate_url,
            current_price = EXCLUDED.current_price,
            in_stock = EXCLUDED.in_stock,
            last_price_check = NOW(),
            feed_product_id = EXCLUDED.feed_product_id
        """,
        product_id,
        retailer_id,
        product.product_url,
        product.affiliate_url,
        product.price,
        product.in_stock,
        product.feed_product_id,
    )

    return product_id, is_new


async def run_feed_sync(adapter, category_map: dict[str, int] | None = None):
    """Run a full feed sync for an adapter.

    category_map: optional dict mapping feed category names to gearsift category IDs.
    If None, products without a matching category are skipped.
    """
    retailer_id = await get_retailer_id(adapter.retailer_slug())

    # Log sync start
    sync_id = await db.fetchval(
        """
        INSERT INTO gearsift.feed_sync_log (retailer_id, status)
        VALUES ($1, 'running') RETURNING id
        """,
        retailer_id,
    )

    try:
        products = await adapter.fetch_feed()
        added, updated, total = 0, 0, 0

        for fp in products:
            # Map feed category to our category
            cat_id = None
            if category_map:
                cat_id = category_map.get(fp.category_name)
            if not cat_id:
                cat_id = await get_or_create_category(fp.category_name)
            if not cat_id:
                continue  # Skip products we can't categorize

            product_id, is_new = await load_product(fp, cat_id)
            if is_new:
                added += 1
            else:
                updated += 1
            total += 1

        await db.execute(
            """
            UPDATE gearsift.feed_sync_log
            SET status = 'success', completed_at = NOW(),
                products_added = $2, products_updated = $3, products_total = $4
            WHERE id = $1
            """,
            sync_id,
            added,
            updated,
            total,
        )
        return {"added": added, "updated": updated, "total": total}

    except Exception as e:
        await db.execute(
            """
            UPDATE gearsift.feed_sync_log
            SET status = 'failed', completed_at = NOW(), error_message = $2
            WHERE id = $1
            """,
            sync_id,
            str(e),
        )
        raise
```

**Step 4: Write CLI entry point**

```python
# backend/src/gearsift/ingest/cli.py
import asyncio
import argparse
from gearsift.db import db
from gearsift.ingest.avantlink import AvantLinkAdapter
from gearsift.ingest.loader import run_feed_sync


async def main(args):
    await db.connect()
    try:
        if args.command == "sync":
            # TODO: merchant IDs will come from AvantLink dashboard after signup
            adapters = {
                "rei": AvantLinkAdapter(merchant_id=args.merchant_id, retailer_slug="rei"),
                "backcountry": AvantLinkAdapter(
                    merchant_id=args.merchant_id, retailer_slug="backcountry"
                ),
            }
            adapter = adapters.get(args.retailer)
            if not adapter:
                print(f"Unknown retailer: {args.retailer}")
                return

            print(f"Syncing feed for {args.retailer}...")
            result = await run_feed_sync(adapter)
            print(
                f"Done: {result['added']} added, {result['updated']} updated, "
                f"{result['total']} total"
            )
    finally:
        await db.disconnect()


def cli():
    parser = argparse.ArgumentParser(description="GearSift feed ingestion")
    sub = parser.add_subparsers(dest="command")

    sync_parser = sub.add_parser("sync", help="Sync affiliate feed")
    sync_parser.add_argument("retailer", choices=["rei", "backcountry"])
    sync_parser.add_argument("--merchant-id", required=True, help="AvantLink merchant ID")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    asyncio.run(main(args))


if __name__ == "__main__":
    cli()
```

**Step 5: Write ingest __init__**

```python
# backend/src/gearsift/ingest/__init__.py
```

**Step 6: Write tests**

```python
# backend/tests/test_ingest.py
from gearsift.ingest.base import FeedProduct
from gearsift.ingest.avantlink import AvantLinkAdapter
from gearsift.ingest.loader import slugify


def test_slugify():
    assert slugify("Nemo Hornet Elite 2P") == "nemo-hornet-elite-2p"
    assert slugify("Big Agnes Copper Spur HV UL2") == "big-agnes-copper-spur-hv-ul2"
    assert slugify("  spaces  and -- dashes  ") == "spaces-and-dashes"


def test_feed_product_creation():
    fp = FeedProduct(
        feed_product_id="12345",
        name="Hornet Elite 2P",
        brand_name="Nemo",
        category_name="Tents",
        description="Ultralight 2-person tent",
        price=399.95,
        msrp=449.95,
        product_url="https://rei.com/product/12345",
        affiliate_url="https://avantlink.com/click?...",
        image_url="https://rei.com/images/12345.jpg",
        in_stock=True,
        retailer_slug="rei",
    )
    assert fp.name == "Hornet Elite 2P"
    assert fp.price == 399.95


def test_avantlink_parse_price():
    assert AvantLinkAdapter._parse_price("$449.95") == 449.95
    assert AvantLinkAdapter._parse_price("1,299.00") == 1299.00
    assert AvantLinkAdapter._parse_price("") is None
    assert AvantLinkAdapter._parse_price(None) is None


def test_avantlink_parse_csv():
    adapter = AvantLinkAdapter(merchant_id="test", retailer_slug="rei")
    csv_text = (
        "Product_Id,Product_Name,Brand_Name,Category,Long_Description,"
        "Sale_Price,Retail_Price,Buy_Link,Image_URL,In_Stock\n"
        "12345,Hornet Elite 2P,Nemo,Tents,Great tent,$399.95,$449.95,"
        "https://avantlink.com/click,https://img.com/tent.jpg,yes\n"
    )
    products = adapter._parse_csv(csv_text)
    assert len(products) == 1
    assert products[0].name == "Hornet Elite 2P"
    assert products[0].brand_name == "Nemo"
    assert products[0].price == 399.95
    assert products[0].in_stock is True
```

**Step 7: Run tests, commit**

```bash
cd backend && python -m pytest tests/test_ingest.py -v
git add backend/src/gearsift/ingest/ backend/tests/test_ingest.py
git commit -m "feat: feed ingestion pipeline with AvantLink adapter and DB loader"
```

---

## Task 7: Seed Categories

**Files:**
- Create: `sql/003_seed_categories.sql`

**Step 1: Write category seed data**

```sql
-- sql/003_seed_categories.sql
-- Initial categories for Phase 1 launch

INSERT INTO gearsift.categories (name, slug, description, sort_order, spec_schema_version)
VALUES
    ('Tents', 'tents', 'Shelters for backpacking and camping', 1, 'tents.v1'),
    ('Sleeping Bags', 'sleeping-bags', 'Insulated sleeping systems', 2, 'sleeping_bags.v1'),
    ('Sleeping Pads', 'sleeping-pads', 'Insulation and cushioning for ground sleeping', 3, 'sleeping_pads.v1'),
    ('Backpacks', 'backpacks', 'Packs for carrying gear on the trail', 4, 'backpacks.v1'),
    ('Trail Running Shoes', 'trail-running-shoes', 'Footwear for trail running and hiking', 5, 'shoes.v1'),
    ('Headlamps', 'headlamps', 'Hands-free lighting for trail and camp', 6, 'headlamps.v1'),
    ('Backpacking Meals', 'backpacking-meals', 'Lightweight food for the trail', 7, 'meals.v1'),
    ('Hiking Socks', 'hiking-socks', 'Performance socks for the trail', 8, 'socks.v1'),
    ('Trekking Poles', 'trekking-poles', 'Adjustable poles for stability and load distribution', 9, 'trekking_poles.v1')
ON CONFLICT (slug) DO NOTHING;
```

**Step 2: Apply and commit**

```bash
ssh root@192.168.2.13 'pct exec 201 -- psql -U postgres -d project_data' < sql/003_seed_categories.sql
git add sql/003_seed_categories.sql
git commit -m "feat: seed 9 starting categories"
```

---

## Task 8: Astro Frontend Scaffold

**Files:**
- Create: `site/` (Astro project via `create astro`)
- Create: `site/src/pages/index.astro`
- Create: `site/src/layouts/Base.astro`
- Create: `site/src/styles/global.css`
- Create: `site/astro.config.mjs`

**Step 1: Initialize Astro project**

```bash
cd /Users/llama/Development/gearsift
npm create astro@latest site -- --template minimal --no-install --no-git
cd site
npm install
npm install @astrojs/sitemap @astrojs/react @astrojs/tailwind
npm install react react-dom
npm install -D @types/react @types/react-dom tailwindcss @tailwindcss/vite
```

**Step 2: Configure Astro**

```javascript
// site/astro.config.mjs
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: 'https://gearsift.com',
  integrations: [sitemap(), react()],
  vite: {
    plugins: [tailwindcss()],
  },
  output: 'static',
});
```

**Step 3: Write base layout**

```astro
---
// site/src/layouts/Base.astro
interface Props {
  title: string;
  description?: string;
}

const { title, description = "Find the right outdoor gear. Answer a few questions, get personalized recommendations." } = Astro.props;
const apiUrl = import.meta.env.PUBLIC_API_URL || 'https://api.gearsift.com';
---
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content={description} />
  <title>{title} | GearSift</title>
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  <meta name="generator" content={Astro.generator} />
</head>
<body class="bg-stone-50 text-stone-900 antialiased">
  <nav class="border-b border-stone-200 bg-white">
    <div class="mx-auto max-w-6xl px-4 py-4 flex items-center justify-between">
      <a href="/" class="text-xl font-bold tracking-tight">GearSift</a>
      <div class="flex gap-6 text-sm font-medium">
        <a href="/categories" class="hover:text-emerald-700">Gear</a>
        <a href="/advisor" class="hover:text-emerald-700">Advisor</a>
        <a href="/kits" class="hover:text-emerald-700">Kits</a>
      </div>
    </div>
  </nav>

  <main>
    <slot />
  </main>

  <footer class="border-t border-stone-200 bg-white mt-16">
    <div class="mx-auto max-w-6xl px-4 py-8 text-sm text-stone-500">
      <p>&copy; {new Date().getFullYear()} GearSift. Recommendations based on specs and community reviews.</p>
    </div>
  </footer>
</body>
</html>
```

**Step 4: Write global CSS**

```css
/* site/src/styles/global.css */
@import "tailwindcss";
```

**Step 5: Write homepage**

```astro
---
// site/src/pages/index.astro
import Base from '../layouts/Base.astro';
---
<Base title="Find the Right Outdoor Gear">
  <section class="mx-auto max-w-6xl px-4 py-24 text-center">
    <h1 class="text-5xl font-bold tracking-tight mb-4">
      Stop guessing.<br/>Start with the specs.
    </h1>
    <p class="text-xl text-stone-600 max-w-2xl mx-auto mb-8">
      Answer a few questions about your trip. Get personalized gear recommendations
      backed by structured data and community reviews.
    </p>
    <a
      href="/advisor"
      class="inline-block bg-emerald-700 text-white px-8 py-3 rounded-lg font-medium hover:bg-emerald-800 transition"
    >
      What gear do you need?
    </a>
  </section>

  <section class="mx-auto max-w-6xl px-4 py-16">
    <h2 class="text-2xl font-bold mb-8">Browse by Category</h2>
    <div class="grid grid-cols-2 md:grid-cols-3 gap-4" id="category-grid">
      <!-- Populated at build time from API in later task -->
      <p class="text-stone-500 col-span-full">Categories loading...</p>
    </div>
  </section>
</Base>
```

**Step 6: Verify build**

```bash
cd site && npm run build
```

**Step 7: Commit**

```bash
cd /Users/llama/Development/gearsift
git add site/
git commit -m "feat: Astro site scaffold with base layout, homepage, and Tailwind CSS"
```

---

## Task 9: Astro Category and Product Pages

**Files:**
- Create: `site/src/pages/categories/index.astro`
- Create: `site/src/pages/categories/[slug].astro`
- Create: `site/src/pages/[category]/[product].astro`
- Create: `site/src/lib/api.ts`

**Step 1: Write API client helper**

```typescript
// site/src/lib/api.ts
const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8200';

export async function fetchCategories() {
  const resp = await fetch(`${API_URL}/api/categories/`);
  if (!resp.ok) throw new Error(`Failed to fetch categories: ${resp.status}`);
  return resp.json();
}

export async function fetchCategory(slug: string) {
  const resp = await fetch(`${API_URL}/api/categories/${slug}`);
  if (!resp.ok) throw new Error(`Failed to fetch category ${slug}: ${resp.status}`);
  return resp.json();
}

export async function fetchProduct(categorySlug: string, productSlug: string) {
  const resp = await fetch(`${API_URL}/api/products/${categorySlug}/${productSlug}`);
  if (!resp.ok) throw new Error(`Failed to fetch product: ${resp.status}`);
  return resp.json();
}

export function affiliateUrl(productSlug: string, retailerSlug: string) {
  return `${API_URL}/go/${productSlug}/${retailerSlug}`;
}
```

**Step 2: Write categories listing page**

```astro
---
// site/src/pages/categories/index.astro
import Base from '../../layouts/Base.astro';
import { fetchCategories } from '../../lib/api';

let categories = [];
try {
  categories = await fetchCategories();
} catch (e) {
  console.error('Failed to fetch categories:', e);
}
---
<Base title="Browse Gear Categories">
  <section class="mx-auto max-w-6xl px-4 py-12">
    <h1 class="text-3xl font-bold mb-8">Gear Categories</h1>
    <div class="grid grid-cols-2 md:grid-cols-3 gap-6">
      {categories.map((cat: any) => (
        <a
          href={`/categories/${cat.slug}`}
          class="block p-6 bg-white rounded-lg border border-stone-200 hover:border-emerald-500 hover:shadow-md transition"
        >
          <h2 class="text-lg font-semibold">{cat.name}</h2>
          {cat.description && <p class="text-sm text-stone-500 mt-1">{cat.description}</p>}
        </a>
      ))}
    </div>
  </section>
</Base>
```

**Step 3: Write category detail page (with product grid)**

```astro
---
// site/src/pages/categories/[slug].astro
import Base from '../../layouts/Base.astro';
import { fetchCategories, fetchCategory } from '../../lib/api';

export async function getStaticPaths() {
  let categories = [];
  try {
    categories = await fetchCategories();
  } catch (e) {
    console.error('Failed to fetch categories for paths:', e);
    return [];
  }
  return categories.map((cat: any) => ({ params: { slug: cat.slug } }));
}

const { slug } = Astro.params;
let data = null;
try {
  data = await fetchCategory(slug!);
} catch (e) {
  return Astro.redirect('/categories');
}

const { category, products } = data;
---
<Base title={category.name} description={`Compare ${category.name.toLowerCase()} specs, prices, and reviews. Find the right ${category.name.toLowerCase()} for your next trip.`}>
  <section class="mx-auto max-w-6xl px-4 py-12">
    <nav class="text-sm text-stone-500 mb-4">
      <a href="/categories" class="hover:text-emerald-700">Gear</a>
      <span class="mx-2">/</span>
      <span>{category.name}</span>
    </nav>

    <h1 class="text-3xl font-bold mb-2">{category.name}</h1>
    <p class="text-stone-600 mb-8">{products.length} products from {new Set(products.map((p: any) => p.brand_name)).size} brands</p>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {products.map((p: any) => (
        <a
          href={`/${category.slug}/${p.slug}`}
          class="block bg-white rounded-lg border border-stone-200 hover:border-emerald-500 hover:shadow-md transition overflow-hidden"
        >
          {p.image_url && (
            <img src={p.image_url} alt={p.name} class="w-full h-48 object-contain bg-stone-100 p-4" loading="lazy" />
          )}
          <div class="p-4">
            <p class="text-xs text-stone-400 uppercase tracking-wider">{p.brand_name}</p>
            <h3 class="font-semibold mt-1">{p.name}</h3>
            <div class="flex items-center gap-3 mt-2 text-sm">
              {p.lowest_price && (
                <span class="text-emerald-700 font-medium">${p.lowest_price.toFixed(2)}</span>
              )}
              {p.weight_oz && (
                <span class="text-stone-500">{p.weight_oz} oz</span>
              )}
            </div>
            {!p.in_stock && (
              <span class="text-xs text-red-600 mt-1 inline-block">Out of stock</span>
            )}
          </div>
        </a>
      ))}
    </div>
  </section>
</Base>
```

**Step 4: Write product detail page**

```astro
---
// site/src/pages/[category]/[product].astro
import Base from '../../layouts/Base.astro';
import { fetchCategories, fetchCategory, fetchProduct, affiliateUrl } from '../../lib/api';

export async function getStaticPaths() {
  let paths: any[] = [];
  try {
    const categories = await fetchCategories();
    for (const cat of categories) {
      const data = await fetchCategory(cat.slug);
      for (const p of data.products) {
        paths.push({
          params: { category: cat.slug, product: p.slug },
        });
      }
    }
  } catch (e) {
    console.error('Failed to build product paths:', e);
  }
  return paths;
}

const { category: catSlug, product: productSlug } = Astro.params;
let product: any = null;
try {
  product = await fetchProduct(catSlug!, productSlug!);
} catch (e) {
  return Astro.redirect('/categories');
}

const specs = product.specs || {};
const specEntries = Object.entries(specs).filter(([_, v]) => v != null);
---
<Base title={`${product.name} by ${product.brand.name}`} description={`${product.name} specs, prices, and reviews. Compare with alternatives.`}>
  <section class="mx-auto max-w-6xl px-4 py-12">
    <nav class="text-sm text-stone-500 mb-4">
      <a href="/categories" class="hover:text-emerald-700">Gear</a>
      <span class="mx-2">/</span>
      <a href={`/categories/${product.category.slug}`} class="hover:text-emerald-700">{product.category.name}</a>
      <span class="mx-2">/</span>
      <span>{product.name}</span>
    </nav>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
      <!-- Left: Image -->
      <div>
        {product.image_url ? (
          <img src={product.image_url} alt={product.name} class="w-full rounded-lg bg-stone-100 p-8 object-contain" />
        ) : (
          <div class="w-full aspect-square rounded-lg bg-stone-100 flex items-center justify-center text-stone-400">
            No image available
          </div>
        )}
      </div>

      <!-- Right: Details -->
      <div>
        <p class="text-sm text-stone-400 uppercase tracking-wider">{product.brand.name}</p>
        <h1 class="text-3xl font-bold mt-1">{product.name}</h1>

        {product.msrp && (
          <p class="text-2xl font-medium text-emerald-700 mt-4">
            ${product.msrp.toFixed(2)}
          </p>
        )}

        {product.description && (
          <p class="text-stone-600 mt-4 leading-relaxed">{product.description}</p>
        )}

        <!-- Buy links -->
        <div class="mt-6 space-y-2">
          <h3 class="text-sm font-semibold text-stone-500 uppercase">Buy from</h3>
          {product.retailers.map((r: any) => (
            <a
              href={affiliateUrl(product.slug, r.retailer_slug)}
              target="_blank"
              rel="noopener noreferrer"
              class="flex items-center justify-between p-3 bg-white border border-stone-200 rounded-lg hover:border-emerald-500 transition"
            >
              <span class="font-medium">{r.retailer_name}</span>
              <div class="flex items-center gap-3">
                {!r.in_stock && <span class="text-xs text-red-500">Out of stock</span>}
                {r.current_price && <span class="font-semibold">${r.current_price.toFixed(2)}</span>}
              </div>
            </a>
          ))}
        </div>
      </div>
    </div>

    <!-- Specs table -->
    {specEntries.length > 0 && (
      <div class="mt-16">
        <h2 class="text-2xl font-bold mb-6">Specifications</h2>
        <div class="bg-white rounded-lg border border-stone-200 overflow-hidden">
          {specEntries.map(([key, value], i) => (
            <div class={`flex px-6 py-3 ${i % 2 === 0 ? 'bg-stone-50' : ''}`}>
              <span class="w-1/3 text-sm text-stone-500 capitalize">
                {key.replace(/_/g, ' ')}
              </span>
              <span class="w-2/3 text-sm font-medium">
                {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : String(value)}
              </span>
            </div>
          ))}
        </div>
      </div>
    )}

    <!-- Suggest a correction -->
    <div class="mt-8 text-center">
      <a href={`mailto:corrections@gearsift.com?subject=Correction: ${product.name}&body=Product: ${product.name}%0AField: %0ACurrent value: %0ACorrect value: %0ASource: `} class="text-sm text-stone-400 hover:text-emerald-700">
        See an error? Suggest a correction
      </a>
    </div>
  </section>
</Base>
```

**Step 5: Verify build (with mock API or skip for now)**

Note: Static build requires the API to be running. During development, use `npm run dev` with the API running locally. For CI/Cloudflare Pages builds, the API must be accessible at `PUBLIC_API_URL`.

**Step 6: Commit**

```bash
git add site/src/
git commit -m "feat: category listing, category detail, and product detail pages"
```

---

## Task 10: Infrastructure - LXC Containers and Cloudflare Tunnel

**Files:**
- Create: `deploy/gearsift-api.service`
- Create: `deploy/provision.sh`

**Step 1: Write systemd service file**

```ini
# deploy/gearsift-api.service
[Unit]
Description=GearSift API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/gearsift/backend
Environment=PATH=/root/gearsift/backend/.venv/bin:/usr/local/bin:/usr/bin
ExecStart=/root/gearsift/backend/.venv/bin/python -m gearsift
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Step 2: Write provisioning script (reference, run manually)**

```bash
#!/bin/bash
# deploy/provision.sh
# Reference script for provisioning GearSift API container on Loki
# Run commands manually via SSH, not as an automated script.

# 1. Create API container (CT 260 on Loki)
# ssh root@192.168.2.16
# pct create 260 local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst \
#   --hostname gearsift-api \
#   --memory 1024 \
#   --swap 512 \
#   --cores 2 \
#   --rootfs local-lvm:8 \
#   --net0 name=eth0,bridge=vmbr0,ip=192.168.2.260/24,gw=192.168.2.1 \
#   --unprivileged 1 \
#   --start 1

# 2. Install Python 3.11 and dependencies
# pct exec 260 -- bash -c 'apt update && apt install -y python3 python3-pip python3-venv git'

# 3. Clone repo and set up venv
# pct exec 260 -- bash -c 'cd /root && git clone <repo_url> gearsift'
# pct exec 260 -- bash -c 'cd /root/gearsift/backend && python3 -m venv .venv && .venv/bin/pip install -e .'

# 4. Copy .env file
# pct push 260 /path/to/.env /root/gearsift/.env

# 5. Install and start service
# pct push 260 deploy/gearsift-api.service /etc/systemd/system/gearsift-api.service
# pct exec 260 -- systemctl daemon-reload
# pct exec 260 -- systemctl enable --now gearsift-api

# 6. Install cloudflared for tunnel
# pct exec 260 -- bash -c 'curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && dpkg -i cloudflared.deb && rm cloudflared.deb'

# 7. Configure tunnel (run interactively)
# pct exec 260 -- cloudflared tunnel login
# pct exec 260 -- cloudflared tunnel create gearsift-api
# Configure tunnel to route api.gearsift.com -> localhost:8200

# 8. Create batch worker container (CT 261) - same process but for feed ingestion
# Can share the same container initially if resource contention is not observed.
```

**Step 3: Write .env.example**

```bash
# .env.example
GEARSIFT_DATABASE_URL=postgresql://gearsift:<password>@192.168.2.67:5432/project_data
GEARSIFT_API_HOST=0.0.0.0
GEARSIFT_API_PORT=8200
GEARSIFT_SITE_URL=https://gearsift.com
GEARSIFT_AVANTLINK_API_KEY=
GEARSIFT_AVANTLINK_AFFILIATE_ID=
GEARSIFT_CORS_ORIGINS=["https://gearsift.com","http://localhost:4321"]
PUBLIC_API_URL=https://api.gearsift.com
```

**Step 4: Commit**

```bash
git add deploy/ .env.example
git commit -m "feat: deployment config - systemd service, provisioning reference, env template"
```

---

## Task 11: End-to-End Integration Test

**Step 1: Seed test data**

```sql
-- sql/004_test_seed.sql (for development/testing only)

-- Insert a test brand
INSERT INTO gearsift.brands (name, slug, website_url)
VALUES ('Nemo', 'nemo', 'https://www.nemoequipment.com')
ON CONFLICT (slug) DO NOTHING;

-- Insert a test product
INSERT INTO gearsift.products (brand_id, category_id, name, slug, description, msrp, weight_oz, specs, image_url)
SELECT b.id, c.id, 'Hornet Elite 2P', 'nemo-hornet-elite-2p',
       'The lightest freestanding backpacking tent in its class.',
       449.95, 28.0,
       '{"capacity": 2, "floor_area_sqft": 27.5, "peak_height_in": 38, "packed_weight_oz": 31.7, "trail_weight_oz": 28.0, "wall_type": "double", "seasons": "3-season", "pole_material": "DAC Featherlite NSL", "freestanding": true}'::jsonb,
       NULL
FROM gearsift.brands b, gearsift.categories c
WHERE b.slug = 'nemo' AND c.slug = 'tents'
ON CONFLICT (slug) DO NOTHING;

-- Link product to REI retailer
INSERT INTO gearsift.product_retailers (product_id, retailer_id, url, affiliate_url, current_price, in_stock)
SELECT p.id, r.id, 'https://www.rei.com/product/nemo-hornet-elite-2p', 'https://avantlink.com/click/nemo-hornet',
       399.95, true
FROM gearsift.products p, gearsift.retailers r
WHERE p.slug = 'nemo-hornet-elite-2p' AND r.slug = 'rei'
ON CONFLICT (product_id, retailer_id) DO NOTHING;
```

**Step 2: Apply test seed**

```bash
ssh root@192.168.2.13 'pct exec 201 -- psql -U postgres -d project_data' < sql/004_test_seed.sql
```

**Step 3: Start API locally and verify**

```bash
cd backend
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m gearsift
```

In a separate terminal:
```bash
# Health check
curl http://localhost:8200/health | python -m json.tool

# List categories
curl http://localhost:8200/api/categories/ | python -m json.tool

# Get tents category with products
curl http://localhost:8200/api/categories/tents | python -m json.tool

# Get specific product
curl http://localhost:8200/api/products/tents/nemo-hornet-elite-2p | python -m json.tool

# Test affiliate redirect (should 302)
curl -I http://localhost:8200/go/nemo-hornet-elite-2p/rei
```

**Step 4: Build Astro site against local API**

```bash
cd site
PUBLIC_API_URL=http://localhost:8200 npm run build
```

Verify that `dist/categories/tents/index.html` exists and contains product data.

**Step 5: Run full test suite**

```bash
cd backend && .venv/bin/python -m pytest tests/ -v
```

**Step 6: Final commit**

```bash
git add sql/004_test_seed.sql
git commit -m "feat: test seed data and integration verification"
```

**Step 7: Update STATE.md**

Mark completed items and update next steps based on actual state.

---

## Post-Phase 1 Checklist (Manual Steps)

These require human action and cannot be automated:

1. **Register gearsift.com** on Cloudflare or preferred registrar
2. **Sign up for AvantLink** affiliate program (apply to REI + Backcountry merchants)
3. **Create GitHub repo** (`gearsift`) and push code
4. **Connect Cloudflare Pages** to GitHub repo (site directory: `site`, build command: `npm run build`)
5. **Provision LXC container** on Loki using `deploy/provision.sh` as reference
6. **Configure Cloudflare Tunnel** for `api.gearsift.com`
7. **Set environment variables** in `.env` on the container
8. **Create gearsift PostgreSQL role** with actual password (store in Bitwarden)
9. **Configure pg_hba.conf** on CT 201 for gearsift user subnet access
10. **Run first feed sync** after AvantLink approval: `python -m gearsift.ingest.cli sync rei --merchant-id <ID>`
11. **Rebuild Astro site** against live API to generate product pages
12. **Update homelab-docs** with new container, service, and Cloudflare Tunnel documentation

---

## Phase 1 Success Criteria

- [ ] gearsift.com resolves and shows the homepage
- [ ] `/categories` lists all 9 categories
- [ ] At least one category has 10+ products from 5+ brands
- [ ] Product pages show specs, prices, and affiliate links
- [ ] Affiliate links go directly to retailer (no API dependency)
- [ ] `/health` returns ok with product and category counts
- [ ] Feed sync CLI runs successfully and updates product data
- [ ] Feed sync triggers Cloudflare Pages rebuild automatically
- [ ] Astro static build generates all product and category pages
- [ ] SEO: product pages have proper title, description, OG tags, JSON-LD

---

## Gemini Adversarial Review Revisions (2026-02-28)

The following changes MUST be applied during implementation. They override the original task descriptions where they conflict.

### R1: Decouple affiliate links from API (CRITICAL)

**Removes:** The `/go/` redirect endpoint (routes/affiliate.py). Affiliate URLs go directly in the static HTML, not through the FastAPI backend.

**Why:** If the homelab goes down, the static site still loads on Cloudflare's edge, but every affiliate link would fail if routed through the API. Revenue must never depend on homelab uptime.

**Implementation:**
- In Task 9 product pages: use the raw `affiliate_url` from the database directly in the `<a href>`. No `/go/` redirect.
- Click tracking: add a lightweight `data-affiliate` attribute to affiliate links and a small inline JS snippet that fires a `navigator.sendBeacon()` to the API for tracking. If the API is down, the click still works (the user reaches the retailer), tracking just silently fails.
- The `affiliate_clicks` table and tracking endpoint still exist in the API for analytics, but they are fire-and-forget, never in the critical purchase path.

### R2: Stream CSV parsing (CRITICAL)

**Applies to:** Task 6, AvantLinkAdapter.fetch_feed()

**Change:** Do NOT load the full CSV response into memory. Stream the HTTP response to a temp file, then iterate with `csv.DictReader` line by line. Upsert in batches of 100. REI feeds can be hundreds of MB.

```python
async def fetch_feed(self, ...):
    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream("GET", self.BASE_URL, params=params) as resp:
            resp.raise_for_status()
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                async for chunk in resp.aiter_text():
                    f.write(chunk)
                tmp_path = f.name

    with open(tmp_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield self._parse_row(row)  # Generator, not list

    os.unlink(tmp_path)
```

### R3: Register asyncpg JSONB codec (CRITICAL)

**Applies to:** Task 3, Database.connect()

**Change:** Register JSONB type codec so asyncpg returns Python dicts instead of strings.

```python
import json

async def connect(self):
    self._pool = await asyncpg.create_pool(
        settings.database_url,
        min_size=2,
        max_size=10,
        init=self._init_connection,
    )

@staticmethod
async def _init_connection(conn):
    await conn.set_type_codec(
        'jsonb',
        encoder=json.dumps,
        decoder=json.loads,
        schema='pg_catalog',
    )
```

### R4: Add daily feed sync scheduler (CRITICAL)

**Applies to:** Task 10, new file `deploy/gearsift-sync.timer`

```ini
# deploy/gearsift-sync.timer
[Unit]
Description=Daily GearSift feed sync

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

```ini
# deploy/gearsift-sync.service
[Unit]
Description=GearSift feed sync job

[Service]
Type=oneshot
User=root
WorkingDirectory=/root/gearsift/backend
Environment=PATH=/root/gearsift/backend/.venv/bin:/usr/local/bin:/usr/bin
ExecStart=/root/gearsift/backend/.venv/bin/python -m gearsift.ingest.cli sync rei --merchant-id <ID>
ExecStartPost=/usr/bin/curl -s -X POST https://api.cloudflare.com/client/v4/pages/webhooks/deploy_hooks/<HOOK_ID>
```

### R5: AvantLink approval risk mitigation (CRITICAL)

**Applies to:** Post-Phase 1 checklist, Task 11

**Change:** Do not apply to AvantLink with a bare site. Phase 1 should launch with manually curated seed data (enough products to make the site look real) and 3-5 guide pages. Apply to AvantLink once the site has content and some organic traffic. The feed ingestion pipeline will be built and tested against mock CSV data until AvantLink credentials are obtained.

Add to Task 6 tests: a mock CSV file with realistic AvantLink field names and dirty data (missing columns, malformed prices, empty rows).

### R6: SEO meta tags (CRITICAL)

**Applies to:** Tasks 8 and 9

**Change:** Base layout must accept and inject:
- `<title>` (dynamic per page)
- `<meta name="description">` (dynamic per page)
- `<link rel="canonical">` (full URL)
- OpenGraph tags (og:title, og:description, og:image, og:url)
- JSON-LD Product schema on product pages

Product page title format: `{Product Name} by {Brand} | GearSift`
Category page title format: `{Category Name} - Compare Specs & Prices | GearSift`

### R7: Cloudflare Pages deploy hook after feed sync (IMPORTANT)

**Applies to:** Task 6, run_feed_sync()

**Change:** After a successful feed sync, trigger a Cloudflare Pages deploy hook to rebuild the static site with fresh data. Add `GEARSIFT_CF_DEPLOY_HOOK_URL` to config.py.

### R8: Task reordering (IMPORTANT)

**Execution order should be:** 1, 2, 7 (seed categories), 3, 4, 5, 6, 8, 9, 10, 11

Move category and test product seeding before API development so endpoints can be tested against real data.

### R9: Out-of-stock logic for missing feed products (IMPORTANT)

**Applies to:** Task 6, run_feed_sync()

**Change:** After processing the full feed, mark any `product_retailers` rows for this retailer that were NOT in today's feed as `in_stock = false`. Products that disappear from the feed are assumed out of stock, not deleted.

```python
# At the end of run_feed_sync(), after processing all products:
await db.execute(
    """
    UPDATE gearsift.product_retailers
    SET in_stock = false
    WHERE retailer_id = $1
      AND last_price_check < $2
    """,
    retailer_id,
    sync_start_time,
)
```

### R10: Cloudflare Pages build env (IMPORTANT)

**Applies to:** Task 9, Task 10

**Change:** Cloudflare Pages build environment must have `PUBLIC_API_URL` set to `https://api.gearsift.com` (via Cloudflare Tunnel), not localhost. Document this in the post-Phase 1 checklist: "Set PUBLIC_API_URL environment variable in Cloudflare Pages project settings."

### R11: API pagination (IMPORTANT)

**Applies to:** Task 5, category routes

**Change:** Add `limit` and `offset` query parameters to the category products endpoint. Default limit=50, max limit=200.

```python
@router.get("/{slug}", response_model=CategoryWithProducts)
async def get_category(slug: str, limit: int = 50, offset: int = 0):
    # ... add LIMIT $2 OFFSET $3 to the products query
```

### R12: Remove React from Phase 1 (IMPORTANT)

**Applies to:** Task 8

**Change:** Do not install `@astrojs/react`, `react`, or `react-dom` in Phase 1. The entire site is static HTML. React islands are introduced in Phase 2 when the advisor quiz is built.
