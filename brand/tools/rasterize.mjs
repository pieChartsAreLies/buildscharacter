// Usage: node rasterize.mjs <svg-path> <width> <height> <output-png>
import sharp from 'sharp';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const [svgPath, w, h, outputPath] = process.argv.slice(2);
const svgBuffer = readFileSync(resolve(svgPath));
await sharp(svgBuffer)
  .resize(parseInt(w), parseInt(h), { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
  .png()
  .toFile(resolve(outputPath));
console.log(`Rasterized ${svgPath} -> ${outputPath} (${w}x${h})`);
