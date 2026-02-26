// Usage: node screenshot.mjs <svg-path> <width> <output-png>
import { chromium } from 'playwright';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const [svgPath, width, outputPath] = process.argv.slice(2);
const svgContent = readFileSync(resolve(svgPath), 'utf-8');
const w = parseInt(width) || 512;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: w, height: w } });
await page.setContent(`
  <html>
    <head>
      <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
      <style>
        body { margin: 0; display: flex; justify-content: center; align-items: center;
               min-height: 100vh; background: white; }
        img { max-width: 90%; max-height: 90%; }
      </style>
    </head>
    <body>
      <img src="data:image/svg+xml;base64,${Buffer.from(svgContent).toString('base64')}" />
    </body>
  </html>
`);
await page.waitForTimeout(1000); // wait for font load
await page.screenshot({ path: resolve(outputPath || 'screenshot.png') });
await browser.close();
