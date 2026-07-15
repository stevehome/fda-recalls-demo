# Tableau Demo Project — Planning Notes

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
