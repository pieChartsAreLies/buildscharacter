# Shop Page Product Cards Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the placeholder shop page with a product grid backed by a markdown content collection, with R2 images optimized by Astro and buy buttons linking to Printful.

**Architecture:** Add a `products` content collection (same pattern as `blog`), replace `shop.astro` with a responsive grid that filters by product type, seed with 3 products from today's design batch. All frontend, no backend changes except a workflow prompt update.

**Tech Stack:** Astro 5, Tailwind v4, Zod, vanilla JS (filtering)

---

### Task 1: Add products content collection

**Files:**
- Modify: `site/src/content.config.ts`

**Step 1: Add the products collection to content.config.ts**

Add a `products` collection alongside the existing `blog` collection:

```typescript
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
  loader: glob({ pattern: '**/[^_]*.{md,mdx}', base: './src/data/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    author: z.string().default('Hobson'),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
  }),
});

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

export const collections = { blog, products };
```

**Step 2: Create the products data directory**

```bash
mkdir -p site/src/data/products
```

**Step 3: Commit**

```bash
git add site/src/content.config.ts
git commit -m "feat: add products content collection schema"
```

---

### Task 2: Configure Astro for remote image optimization

**Files:**
- Modify: `site/astro.config.mjs`

**Step 1: Add R2 domain to image.domains**

```javascript
// @ts-check
import { defineConfig } from 'astro/config';

import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://buildscharacter.com',
  vite: {
    plugins: [tailwindcss()]
  },
  integrations: [sitemap()],
  output: 'static',
  image: {
    domains: ['pub-16bac62563eb4ef4939d29f3e11305db.r2.dev'],
  },
});
```

**Step 2: Commit**

```bash
git add site/astro.config.mjs
git commit -m "feat: allow R2 domain for Astro image optimization"
```

---

### Task 3: Seed product data files

**Files:**
- Create: `site/src/data/products/this-builds-character-mug.md`
- Create: `site/src/data/products/type-2-fun-certified-mug.md`
- Create: `site/src/data/products/i-paid-money-to-suffer-mug.md`

**Step 1: Get the R2 image URLs and Printful product URLs**

Query PostgreSQL for the image URLs:

```bash
ssh root@192.168.2.13 'pct exec 201 -- su - postgres -c "psql -d project_data -c \"SELECT concept_name, image_url FROM hobson.design_generations WHERE generation_status = '"'"'success'"'"' AND image_url IS NOT NULL AND image_url != '"'"''"'"' ORDER BY created_at DESC LIMIT 5;\""'
```

Get the Printful store product URLs:

```bash
ssh root@192.168.2.16 'pct exec 255 -- bash -c "cd /root/builds-character/hobson && .venv/bin/python -c \"
from hobson.tools.printful import list_store_products
print(list_store_products.invoke({}))
\""'
```

**Step 2: Create the three product files**

Use the actual URLs from step 1. Example format for each file:

`site/src/data/products/this-builds-character-mug.md`:

```yaml
---
name: "This Builds Character"
description: "A mug for people who voluntarily do hard things and want everyone to know."
price: 14.99
image: "https://pub-16bac62563eb4ef4939d29f3e11305db.r2.dev/designs/27a68b2c-c823-4554-8f8b-36bd67b0f1f2-this-builds-character.png"
printful_url: "https://www.printful.com/custom/mugs"
product_type: "mug"
status: "active"
addedDate: 2026-02-24
---
```

`site/src/data/products/type-2-fun-certified-mug.md`:

```yaml
---
name: "Type 2 Fun Certified"
description: "For the person who calls a 14-hour suffer-fest in the rain 'a great time' three days later."
price: 14.99
image: "https://pub-16bac62563eb4ef4939d29f3e11305db.r2.dev/designs/812f453c-1386-474c-bb2e-35affe6834cf-type-2-fun-certified.png"
printful_url: "https://www.printful.com/custom/mugs"
product_type: "mug"
status: "active"
addedDate: 2026-02-24
---
```

`site/src/data/products/i-paid-money-to-suffer-mug.md`:

```yaml
---
name: "I Paid Money to Suffer"
description: "Race day energy in ceramic form. For marathoners, triathletes, and anyone who pays entry fees to hurt."
price: 14.99
image: "https://pub-16bac62563eb4ef4939d29f3e11305db.r2.dev/designs/0604b4d3-c255-4da1-b10a-903ff2c63d01-i-paid-money-to-suffer.png"
printful_url: "https://www.printful.com/custom/mugs"
product_type: "mug"
status: "active"
addedDate: 2026-02-24
---
```

**Note:** The `printful_url` values above are placeholders. Use the actual Printful product page URLs from step 1 if available. If Printful doesn't provide individual product URLs via its API, use the store URL or leave as the custom mugs page.

**Step 3: Commit**

```bash
git add site/src/data/products/
git commit -m "feat: seed 3 product data files from first design batch"
```

---

### Task 4: Build the shop page

**Files:**
- Modify: `site/src/pages/shop.astro`

**Step 1: Replace the placeholder shop page**

```astro
---
import Base from '../layouts/Base.astro';
import { getCollection } from 'astro:content';

const products = (await getCollection('products', ({ data }) => data.status === 'active'))
  .sort((a, b) => b.data.addedDate.valueOf() - a.data.addedDate.valueOf());

const productTypes = [...new Set(products.map(p => p.data.product_type))].sort();
---

<Base title="Shop" description="Wearable suffering. Stickers, shirts, and gear for people who voluntarily do hard things.">
  <h1 class="font-display text-4xl font-bold mb-2">Shop</h1>
  <p class="text-slate mb-8">Wearable suffering. Stickers, shirts, and gear for people who voluntarily do hard things.</p>

  {products.length === 0 ? (
    <div class="border border-dashed border-charcoal/20 p-12 text-center">
      <p class="text-slate text-lg mb-4">Hobson is currently generating designs and setting up the store.</p>
      <p class="text-sm text-slate/60 font-mono">
        Check back soon, or follow on <a href="https://buildscharacter.substack.com" class="text-rust hover:underline">Substack</a> for launch announcements.
      </p>
    </div>
  ) : (
    <>
      {/* Filter buttons */}
      <div class="flex flex-wrap gap-2 mb-8">
        <button
          class="filter-btn text-sm font-mono px-3 py-1 border border-charcoal/20 text-rust underline underline-offset-4"
          data-filter="all"
        >
          All
        </button>
        {productTypes.map((type) => (
          <button
            class="filter-btn text-sm font-mono px-3 py-1 border border-charcoal/20 text-slate hover:text-rust transition-colors"
            data-filter={type}
          >
            {type.charAt(0).toUpperCase() + type.slice(1)}s
          </button>
        ))}
      </div>

      {/* Product grid */}
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {products.map((product) => (
          <div class="product-card border border-charcoal/10 bg-white overflow-hidden" data-type={product.data.product_type}>
            <div class="aspect-square overflow-hidden bg-cream">
              <img
                src={product.data.image}
                alt={product.data.name}
                width={400}
                height={400}
                loading="lazy"
                class="w-full h-full object-cover"
              />
            </div>
            <div class="p-4">
              <h2 class="font-display font-bold text-lg">{product.data.name}</h2>
              <p class="text-slate text-sm mt-1 line-clamp-2">{product.data.description}</p>
              <div class="flex items-center justify-between mt-3">
                <span class="font-mono font-medium">${product.data.price.toFixed(2)}</span>
                <span class="text-xs font-mono bg-charcoal/5 px-2 py-1 text-slate">
                  {product.data.product_type}
                </span>
              </div>
              <a
                href={product.data.printful_url}
                target="_blank"
                rel="noopener noreferrer"
                class="buy-btn block w-full mt-4 py-2 text-center text-sm font-medium bg-rust text-offwhite hover:bg-rust/90 transition-colors"
                data-product-name={product.data.name}
                data-product-type={product.data.product_type}
              >
                Buy on Printful
              </a>
            </div>
          </div>
        ))}
      </div>
    </>
  )}

  <script>
    // Product type filtering
    document.querySelectorAll('.filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const filter = btn.getAttribute('data-filter');

        // Update active button styles
        document.querySelectorAll('.filter-btn').forEach(b => {
          b.classList.remove('text-rust', 'underline', 'underline-offset-4');
          b.classList.add('text-slate');
        });
        btn.classList.remove('text-slate');
        btn.classList.add('text-rust', 'underline', 'underline-offset-4');

        // Show/hide products
        document.querySelectorAll('.product-card').forEach(card => {
          if (filter === 'all' || card.getAttribute('data-type') === filter) {
            card.classList.remove('hidden');
          } else {
            card.classList.add('hidden');
          }
        });
      });
    });

    // Buy button click tracking
    document.querySelectorAll('.buy-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const name = btn.getAttribute('data-product-name');
        const type = btn.getAttribute('data-product-type');
        console.log(`[shop] buy click: ${name} (${type})`);
      });
    });
  </script>
</Base>
```

**Note on images:** We're using a plain `<img>` tag with explicit `width`/`height` to prevent layout shift. Astro's `<Image />` component works best with local images; for remote URLs in a static build, the plain `<img>` with lazy loading is simpler and avoids build-time download issues. The R2 images are already optimized PNGs at 1024x1024. We can revisit Astro image optimization when image volume grows.

**Step 2: Verify the build locally**

```bash
cd site && npm run build
```

Expected: Build succeeds, no errors. Check `dist/shop/index.html` exists and contains product cards.

**Step 3: Commit**

```bash
git add site/src/pages/shop.astro
git commit -m "feat: replace shop placeholder with product grid and filtering"
```

---

### Task 5: Build, verify, push, and deploy

**Files:**
- No new files

**Step 1: Run the full build**

```bash
cd site && npm run build
```

Expected: Build succeeds with 0 errors.

**Step 2: Preview locally**

```bash
cd site && npm run preview
```

Open `http://localhost:4321/shop` and verify:
- 3 product cards visible
- Images load from R2
- Filter buttons work (All is active by default, only "Mugs" type since all 3 are mugs)
- "Buy on Printful" buttons link out correctly
- Responsive layout (resize browser)
- Empty state isn't shown (since we have products)

**Step 3: Push to deploy**

```bash
git push
```

Cloudflare Pages will auto-build and deploy. Verify at `https://buildscharacter.com/shop`.

**Step 4: Commit any final fixes**

If the preview revealed issues, fix and commit before pushing.

---

### Task 6: Update design batch workflow prompt

**Files:**
- Modify: `hobson/src/hobson/workflows/design_batch.py`

**Step 1: Add product markdown step to both prompts**

After the Printful product creation step (step 7), add a new step 8 that instructs Hobson to write a product markdown file:

Add this text after step 7 in `DESIGN_BATCH_PROMPT`:

```
8. **Write product data file.** For each product created on Printful, write a
   markdown file to 'site/src/data/products/{slug}.md' using create_blog_post_pr
   (steady-state) or publish_blog_post (bootstrap). The file must have this
   exact frontmatter format:

   ---
   name: "Product Name"
   description: "One sentence product description"
   price: 14.99
   image: "https://pub-16bac62563eb4ef4939d29f3e11305db.r2.dev/designs/..."
   printful_url: "https://www.printful.com/..."
   product_type: "mug"
   status: "active"
   addedDate: YYYY-MM-DD
   ---

   The slug should be lowercase-hyphenated (e.g., 'this-builds-character-mug.md').
   The price must be a number (not a string). The image URL is from the
   generate_design_image result. The addedDate is today's date.

   Double-check: name is a string, price is a number with no quotes, image and
   printful_url are valid URLs, product_type matches the enum (sticker, mug, pin,
   print, poster, t-shirt), status is "active".
```

Renumber subsequent steps (old 8 -> 9, old 9 -> 10).

Apply the same change to the bootstrap variant (the `.replace()` already swaps step 7, so the new step 8 should appear after the replaced step 7).

**Step 2: Commit**

```bash
git add hobson/src/hobson/workflows/design_batch.py
git commit -m "feat: add product markdown writing step to design batch workflow"
```

---

### Task 7: Deploy workflow update to CT 255

**Files:**
- No new files

**Step 1: Push all changes**

```bash
git push
```

**Step 2: Pull and restart on CT 255**

```bash
ssh root@192.168.2.16 'pct exec 255 -- bash -c "cd /root/builds-character && git pull origin master && cd hobson && .venv/bin/pip install -e . -q && systemctl restart hobson"'
```

**Step 3: Verify health**

```bash
ssh root@192.168.2.16 'pct exec 255 -- bash -c "curl -s http://localhost:8080/health"'
```

Expected: `{"status":"ok","agent":"hobson","version":"0.1.0"}`
