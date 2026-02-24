# Shop Page Product Cards Design

**Date:** 2026-02-24
**Status:** Approved (revised after Gemini adversarial review)

## Goal

Replace the placeholder shop page with a product grid that Hobson can populate by writing markdown files, with product images from R2 and checkout links to Printful.

## Decisions

| Decision | Choice | Reasoning |
|---|---|---|
| Data source | Markdown content collection | Same pattern as blog. One file per product, easy to diff in PRs, Hobson already knows how to write markdown files. |
| Checkout | Printful-hosted | Zero custom checkout code. Product cards link out to Printful for purchase. Buy buttons include click tracking. |
| Layout | Responsive grid cards | 3 columns desktop, 2 tablet, 1 mobile. Clean, standard e-commerce pattern. |
| Filtering | Client-side vanilla JS (MVP) | No framework overhead. Toggle visibility via data attributes. Plan for build-time filtered routes at 50+ products. |
| Image source | R2 public URLs via Astro `<Image />` | Astro handles format conversion (WebP/AVIF) and responsive srcset at build time. |
| Price format | Numeric (not string) | `z.number().positive()` ensures data integrity. Frontend formats as currency. |
| Status | `active` or `draft` only | No `sold-out` since Printful owns inventory state. |

## Content Collection Schema

New `products` collection in `content.config.ts`, same pattern as `blog`:

```typescript
const products = defineCollection({
  loader: glob({ pattern: '**/[^_]*.{md,mdx}', base: './src/data/products' }),
  schema: z.object({
    name: z.string(),
    description: z.string(),
    price: z.number().positive(),
    image: z.string().url(),
    printful_url: z.string().url(),
    product_type: z.enum(['sticker', 'mug', 'pin', 'print', 'poster', 't-shirt']),
    status: z.enum(['active', 'draft']).default('active'),
    addedDate: z.coerce.date(),
  }),
});
```

## Product Markdown Format

One file per product in `src/data/products/`:

```yaml
---
name: "This Builds Character"
description: "A mug for people who voluntarily do hard things and want everyone to know."
price: 14.99
image: "https://pub-16bac62563eb4ef4939d29f3e11305db.r2.dev/designs/27a68b2c-this-builds-character.png"
printful_url: "https://www.printful.com/..."
product_type: "mug"
status: "active"
addedDate: 2026-02-24
---
Optional longer description or story about the design.
```

## Shop Page Layout

```
+----------------------------------------------+
| Shop                                          |
| Wearable suffering. Stickers, shirts, and     |
| gear for people who voluntarily do hard things|
|                                               |
| [All] [Stickers] [Mugs] [Pins] [Prints]      |
|                                               |
| +----------+ +----------+ +----------+       |
| |  [image] | |  [image] | |  [image] |       |
| |          | |          | |          |       |
| |  Name    | |  Name    | |  Name    |       |
| |  $14.99  | |  $14.99  | |  $14.99  |       |
| |  [mug]   | |  [pin]   | |  [mug]   |       |
| |  [Buy]   | |  [Buy]   | |  [Buy]   |       |
| +----------+ +----------+ +----------+       |
+----------------------------------------------+
```

- Responsive: 3 col desktop, 2 col tablet, 1 col mobile
- Product type badge (small pill, e.g., "mug", "sticker")
- "Buy" button links to `printful_url` (opens new tab)
- Buy button click tracking: `data-product-name` and `data-product-type` attributes, vanilla JS event listener logs to console and fires custom event for future analytics integration
- Only `status: "active"` products shown
- Empty state: show "coming soon" message if no active products
- Price formatted as USD: `$${price.toFixed(2)}`

## Image Optimization

Product images served via Astro's `<Image />` component (or `getImage()` helper for remote URLs). This provides:

- Automatic WebP/AVIF format conversion
- Responsive `srcset` generation
- Lazy loading
- Proper `width`/`height` attributes to prevent layout shift

Since images are remote (R2 URLs), Astro needs `image.domains` configured in `astro.config.mjs` to allow remote image optimization.

## Filtering

Client-side vanilla JS. Filter buttons at top:

- "All" (default, shows everything)
- One button per product type that has active products (dynamically generated from data)
- Active filter gets `text-rust` + underline treatment
- Products hidden/shown via CSS class toggle on `data-type` attribute

**Scaling plan:** At 50+ products, migrate to build-time filtered routes (`/shop/stickers`, `/shop/mugs`) using Astro dynamic routes. Client-side filtering is the MVP.

## Hobson Integration

After the design batch workflow creates a Printful product, Hobson writes a product markdown file to `site/src/data/products/` using the existing git tools (`create_blog_post_pr` in steady-state, direct push in bootstrap mode). The design batch workflow prompt needs a new step after Printful product creation.

**Build validation:** Hobson should validate the markdown frontmatter matches the Zod schema before committing. A malformed product file will crash the Astro build and block all deployments. The workflow prompt should instruct Hobson to double-check required fields and types.

## Files Changed

| File | Change |
|---|---|
| `site/src/content.config.ts` | Add `products` collection with Zod schema |
| `site/src/data/products/` | New directory with seed product files |
| `site/src/pages/shop.astro` | Replace placeholder with product grid + filter UI + buy click tracking |
| `site/astro.config.mjs` | Add R2 domain to `image.domains` for remote optimization |
| `hobson/src/hobson/workflows/design_batch.py` | Add step to write product markdown after Printful creation |
