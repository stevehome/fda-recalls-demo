// Generates social-preview.png (1200x630, the standard Open Graph / Twitter
// Card size) from the built dashboard, for the OG image meta tags in index.html
// and dashboard_template.html (og:image:width/height there declare 1200x630
// explicitly, so this script must always produce exactly that - not "however
// tall the content happens to be" - or the declared and actual dimensions
// mismatch, which some crawlers handle poorly).
//
// Not part of the Python/uv pipeline - Playwright is a dev-time-only tool here
// (see .claude/.codebase-info/tech-landscape.md), not a project dependency.
// Prerequisite: `npm install playwright` in a scratch directory, then run this
// script with node, e.g.:
//   node /path/to/generate_social_preview.js
//
// Re-run whenever the dashboard's visual design changes materially enough that
// the preview image goes stale.

const { chromium } = require('playwright');
const path = require('path');

const TARGET_WIDTH = 1200;
const TARGET_HEIGHT = 630;
const PAGE_PLANE_LIGHT = '#f9f9f7'; // matches --page-plane in dashboard_template.html

(async () => {
  const browser = await chromium.launch();

  // Step 1: screenshot just the "hero" content (header through the end of the
  // chart grid) at its natural height - not the FAQ/footer below it, and not
  // padded to any fixed size yet.
  const contentPage = await browser.newPage({ viewport: { width: TARGET_WIDTH, height: 1200 }, colorScheme: 'light' });
  const dashboardPath = 'file://' + path.resolve(__dirname, '..', 'dashboard', 'index.html');
  await contentPage.goto(dashboardPath);
  await contentPage.waitForTimeout(200); // let the SVG charts finish their initial render

  const gridBottom = await contentPage.evaluate(() => document.querySelector('.chart-grid').getBoundingClientRect().bottom);
  const contentHeight = Math.min(TARGET_HEIGHT, Math.ceil(gridBottom) + 16);
  const contentPng = await contentPage.screenshot({ clip: { x: 0, y: 0, width: TARGET_WIDTH, height: contentHeight } });
  await contentPage.close();

  // Step 2: composite that screenshot onto a canvas that is always exactly
  // TARGET_WIDTH x TARGET_HEIGHT, so the file's real dimensions always match
  // what the og:image:width/height meta tags declare, regardless of how tall
  // the dashboard's hero content happens to be on any given rebuild.
  const contentDataUrl = 'data:image/png;base64,' + contentPng.toString('base64');
  const canvasPage = await browser.newPage({ viewport: { width: TARGET_WIDTH, height: TARGET_HEIGHT } });
  await canvasPage.setContent(`
    <!doctype html><html><head><style>
      html, body { margin: 0; padding: 0; background: ${PAGE_PLANE_LIGHT}; }
      img { display: block; width: ${TARGET_WIDTH}px; }
    </style></head><body><img src="${contentDataUrl}"></body></html>
  `);
  const outPath = path.resolve(__dirname, '..', 'social-preview.png');
  await canvasPage.screenshot({ path: outPath });
  await canvasPage.close();

  console.log(`Wrote ${outPath} (${TARGET_WIDTH}x${TARGET_HEIGHT}, content height ${contentHeight})`);
  await browser.close();
})();
