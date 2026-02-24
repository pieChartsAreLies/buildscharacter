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
