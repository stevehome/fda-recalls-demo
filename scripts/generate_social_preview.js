// Generates social-preview.png (1200x630, the standard Open Graph / Twitter
// Card size) from the built dashboard, for the OG image meta tags in index.html.
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

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, colorScheme: 'light' });
  const dashboardPath = 'file://' + path.resolve(__dirname, '..', 'dashboard', 'index.html');
  await page.goto(dashboardPath);
  await page.waitForTimeout(200); // let the SVG charts finish their initial render
  const outPath = path.resolve(__dirname, '..', 'social-preview.png');
  await page.screenshot({ path: outPath });
  console.log('Wrote ' + outPath);
  await browser.close();
})();
