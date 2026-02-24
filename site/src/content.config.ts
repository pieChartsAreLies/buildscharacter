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
