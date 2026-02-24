# Shop Page Product Cards Design

**Date:** 2026-02-24
**Status:** Approved

## Goal

Replace the placeholder shop page with a product grid that Hobson can populate by writing markdown files, with product images from R2 and checkout links to Printful.

## Decisions

| Decision | Choice | Reasoning |
|---|---|---|
| Data source | Markdown content collection | Same pattern as blog. One file per product, easy to diff in PRs, Hobson already knows how to write markdown files. |
| Checkout | Printful-hosted | Zero custom checkout code. Product cards link out to Printful for purchase. |
| Layout | Responsive grid cards | 3 columns desktop, 2 tablet, 1 mobile. Clean, standard e-commerce pattern. |
| Filtering | Client-side vanilla JS | No framework overhead. Toggle visibility via data attributes. Product type buttons. |
| Image source | R2 public URLs | Images already hosted on R2 from the design batch workflow. No additional hosting needed. |

## Content Collection Schema

New `products` collection in `content.config.ts`, same pattern as `blog`:

```typescript
const products = defineCollection({
  loader: glob({ pattern: '**/[^_]*.{md,mdx}', base: './src/data/products' }),
  schema: z.object({
    name: z.string(),
    description: z.string(),
    price: z.string(),
    image: z.string().url(),
    printful_url: z.string().url(),
    product_type: z.enum(['sticker', 'mug', 'pin', 'print', 'poster', 't-shirt']),
    status: z.enum(['active', 'draft', 'sold-out']).default('active'),
    pubDate: z.coerce.date(),
  }),
});
```

## Product Markdown Format

One file per product in `src/data/products/`:

```yaml
---
name: "This Builds Character"
description: "A mug for people who voluntarily do hard things and want everyone to know."
price: "14.99"
image: "https://pub-16bac62563eb4ef4939d29f3e11305db.r2.dev/designs/27a68b2c-this-builds-character.png"
printful_url: "https://www.printful.com/..."
product_type: "mug"
status: "active"
pubDate: 2026-02-24
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
- Only `status: "active"` products shown
- Empty state: show "coming soon" message if no active products

## Filtering

Client-side vanilla JS. Filter buttons at top:

- "All" (default, shows everything)
- One button per product type that has active products
- Active filter gets `text-rust` + underline treatment
- Products hidden/shown via CSS class toggle on `data-type` attribute

## Hobson Integration

After the design batch workflow creates a Printful product, Hobson writes a product markdown file to `src/data/products/` using the existing git tools (`create_blog_post_pr` in steady-state, direct push in bootstrap mode). The design batch workflow prompt needs a new step after Printful product creation.

## Files Changed

| File | Change |
|---|---|
| `site/src/content.config.ts` | Add `products` collection with Zod schema |
| `site/src/data/products/` | New directory with seed product files |
| `site/src/pages/shop.astro` | Replace placeholder with product grid + filter UI |
| `hobson/src/hobson/workflows/design_batch.py` | Add step to write product markdown after Printful creation |
