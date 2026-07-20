# Tableau Demo Project — Planning Notes

> **Update, 2026-07-20:** the project moved off Tableau entirely — Tableau Public
> couldn't open the `.hyper` extract (no local-file support), and separately Tableau's
> story-writing feature was mid-rewrite and unreliable to build against. Rather than
> keep working around a moving-target GUI tool, the dashboard step became a
> self-contained, code-driven HTML page instead (`src/build_dashboard.py` →
> `dashboard/index.html`) — no GUI dependency, fully reproducible, versioned in git like
> the rest of the pipeline. The Tableau path (`tableau/BUILD_SPEC.md`, the Hyper extract
> builder) is left in place as still-valid, just not the active path. Everything below
> is the original brainstorm and reflects the project's starting point, not its current
> state — see the README for what actually shipped.

Goal: a portfolio-style project that shows off Tableau skills end-to-end — not just a
pretty dashboard on a tidy Kaggle CSV, but a story that starts with messy public data,
shows real cleaning/prep decisions, and ends in an interactive, insight-driven dashboard.
The cleaning step matters most for credibility: anyone can point Tableau at a clean
dataset, fewer people can show the "before" state and justify their prep choices.

## What makes a good candidate dataset

- Publicly available, free, no auth wall (or a simple free API key)
- Genuinely messy: inconsistent categories, missing values, multiple files needing joins,
  wrong types, duplicate records, or unnormalized geography/time fields
- Has a natural narrative — trend over time, geographic comparison, before/after an event
- Refreshable ideally (so the dashboard could be framed as "living", not a one-off)
- Big enough to be interesting, small enough to iterate on quickly (thousands to low
  millions of rows)

## Candidate ideas (ranked by interest)

1. **FDA/CDC food recalls or foodborne illness outbreaks**
   Source: openFDA API, CDC NORS data. Messy in classic ways: free-text product
   descriptions, inconsistent state/company naming, multiple recall classes, dates in
   different formats. Story: recall trends by category/state/year, severity
   distribution, response-time (recall initiation → resolution). Cleaning work: parsing
   free text into categories, standardizing company/state names, deduplicating recall
   updates that reference the same event.

2. **US commercial flight delays (BTS On-Time Performance)**
   Source: Bureau of Transportation Statistics. Large monthly CSVs, needs airport-code
   joins, carrier-code lookups, cancellation-reason recoding, and outlier handling
   (negative delays, absurd taxi times). Story: delay patterns by airline/airport/season,
   cascading delay effects. Well-trodden territory but great for showing joins + calcs +
   parameter-driven filtering in Tableau.

3. **Local/county-level public health or housing permit data**
   Source: a city or county open-data portal (Socrata-based — e.g., NYC, Chicago, SF).
   Real-world messiness: inconsistent address formats needing geocoding, department name
   changes over time, missing permit-type codes. Story: permitting trends,
   approval-time distributions, neighborhood-level comparisons. Good if I want a strong
   geographic/map component in Tableau.

4. **Global electricity/energy mix (Our World in Data or IEA)**
   Cleaner than the others but still needs unit reconciliation, country-name
   standardization (matching to Tableau's built-in geo roles), and handling of
   discontinued country codes (USSR, Yugoslavia, etc.). Story: renewable transition by
   country/region over time. Easier build, strong visual payoff (animated map + line
   charts), less impressive as a "cleaning" showcase.

5. **Consumer complaint data (CFPB Consumer Complaint Database)**
   Free-text complaint narratives, company-name inconsistencies, product/sub-product
   taxonomy that changed over the years. Story: complaint volume by company/product,
   resolution-time analysis, timeliness-of-response trends. Good real-world "messy
   categorical" showcase.

## Leaning toward

Option 1 (FDA/CDC recalls) or 5 (CFPB complaints) — both are US federal open data (no
cost, well-documented APIs), both require nontrivial free-text/categorical cleanup
before Tableau can do anything useful with them, and both support a narrative dashboard
(trends + geography + a drill-down table) rather than a single static chart.

## Rough project shape

1. **Extract** — pull raw data via API/bulk download (Python + `uv`, since that's the
   project's Python workflow), save raw snapshot before any modification.
2. **Clean/prep** — a scripted, reproducible pipeline (not manual spreadsheet edits) so
   the cleaning logic itself is part of the demo: dedupe, standardize categories,
   parse/normalize dates, handle nulls explicitly (documented decisions, not silent
   drops), output a tidy fact table + lookup dimensions.
3. **Model** — decide star-schema-ish shape (one fact table + a couple of dimension
   tables) so Tableau relationships/joins are also part of the demo, not just a single
   flat CSV.
4. **Build in Tableau** — a small dashboard (3-4 views) with at least one map, one
   trend-over-time, one categorical breakdown, and cross-filtering via actions;
   parameters for user-driven what-if framing if the data supports it.
5. **Document** — short write-up of the cleaning decisions and why, since that's the
   part a portfolio viewer can't see just from the finished dashboard.

## Open questions

- Do I want Tableau Public (free, dashboard must be public) or Desktop/private? Affects
  whether any sensitive-ish data (e.g. consumer complaints naming real companies) is a
  concern — probably fine since it's already public federal data, but worth a sanity
  check before publishing.
- How much of the cleaning pipeline should live in this repo vs. a throwaway script —
  leaning toward keeping it in-repo since the pipeline is itself part of the portfolio
  value.

## Ideas, 2026-07-20: shrinking the dashboard + LinkedIn preview image

Not yet built — notes for a future pass on `dashboard/index.html`.

### Reducing the dashboard's footprint

Right now all five charts (state ranking, severity trend, cause breakdown, event-size
distribution, resolution-time box plot) render at full size, stacked, so the page is
tall and needs real scrolling to see everything. Idea: a compact "overview" mode with a
click-to-focus interaction, rather than shrinking the file size (32 KB is already
trivial) — the goal is screen footprint, so the whole dashboard reads as one glanceable
grid instead of a long scroll.

- **Thumbnail grid by default.** Render every chart card noticeably smaller (e.g. a
  3–4 column grid of compact cards instead of the current 2-column full-size layout) —
  smaller SVG viewBox, tighter margins, smaller fonts, caption/table-toggle hidden until
  focused. Since every chart already renders as a `viewBox`-scaled SVG (not a raster
  image), a "thumbnail" is mostly a CSS sizing change on the same markup, not a second
  rendering path — cheap to build.
- **Click to focus.** Clicking a thumbnail card expands it — likely a lightbox/modal
  (dim the background, show that one chart at full size, centered, with a close
  affordance) rather than growing it in place, since growing in place shoves the other
  cards around. The existing `render*Chart` functions could be reused unchanged, just
  invoked into a bigger container when a chart is focused (or the same SVG resized via
  CSS, since it's viewBox-based and inherently responsive).
- **Accessibility, since this project has been careful about it so far:** the focus
  interaction needs keyboard support (Enter/Space to open a thumbnail, Escape to close,
  focus trapped inside the modal while open), `role="dialog"` / `aria-modal="true"` on
  the focused view, and the closed thumbnail state should never be the *only* way to
  reach a chart's data — the "View as table" fallback should stay reachable without
  going through the focus interaction at all.
- **Nice side effect:** a compact overview grid that fits above the fold is also a much
  better screenshot for a LinkedIn post or the social-preview image below — one image
  showing all five charts at once, rather than a tall scrolling page.

### Social preview image for LinkedIn (Open Graph tags)

When a URL gets pasted into LinkedIn, the preview card LinkedIn shows comes from Open
Graph meta tags in the page's `<head>` — nothing shows up automatically without them.
Needed:

- `<meta property="og:title" content="...">`, `og:description`, `og:url`,
  `og:type" content="website"` — straightforward.
- `<meta property="og:image" content="...">` — must be an **absolute** URL (crawlers
  fetch it directly, a relative path won't resolve), ideally sized close to LinkedIn's
  recommended ~1200×627. This means generating an actual static image first — e.g. a
  screenshot of the (future compact) dashboard, committed into the repo and served via
  the same GitHub Pages URL (`https://stevehome.github.io/fda-recalls-demo/social-preview.png`).
  Playwright is already on hand from testing the dashboard during dev — the same
  headless-screenshot approach could produce this image directly instead of a manual
  crop.
- Twitter Card equivalents too (`twitter:card` = `summary_large_image`, `twitter:title`,
  `twitter:image`) — LinkedIn sometimes falls back to these, and other platforms read
  them directly.
- **Which file gets the tags matters.** The URL people will actually share is the
  GitHub Pages root (`index.html`, the meta-refresh redirect to `dashboard/index.html`)
  — crawlers read raw HTML and don't execute JS/meta-refresh, so the OG tags need to
  live on the root `index.html` itself (not only on `dashboard/index.html`) for the
  shared link's preview to work. Reasonable to duplicate the same tags onto
  `dashboard/index.html` too, in case that deeper URL gets shared directly instead.
- Separate from this: GitHub itself has its own "social preview image" setting (repo
  Settings → General) that controls the preview when someone shares the *github.com*
  repo URL specifically — a different mechanism from the Pages-site OG tags above, worth
  setting too but doesn't substitute for it.
