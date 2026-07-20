# FDA Food Recalls: from messy government data to a working dashboard

A portfolio project built around a simple premise: a dashboard is only as convincing as
the data behind it, and most public datasets aren't clean enough to point a BI tool at
directly. This one pulls ~29,000 FDA food recall records from a live government API and
works through the real cleaning problems in that data — a corrupted date, an
inconsistent geography field, a missing structured "cause of recall" field — before any
of it reaches a chart.

The point isn't the dashboard alone. It's showing the judgment calls that got the data
there: what got fixed, what got left alone, and why.

The project started as a Tableau demo (see `planning/PLAN.md` and `tableau/` for that
work — a Hyper extract and a full build spec, both still valid). It later moved to a
self-contained, code-driven HTML dashboard instead: no GUI tool in the loop, so every
chart decision is in source control and reproducible from a single command rather than
a saved workbook.

## The data

Source: [openFDA Food Enforcement API](https://api.fda.gov/food/enforcement.json) — the
FDA's public record of food recalls, free and keyless. 29,223 individual recall records,
grouped into 7,790 real-world recall events, spanning 2008–2026.

## Problem 1: you can't just page through it

The API caps its pagination offset at 25,000 records. With ~29,200 total records,
requesting them in one sorted sequence runs straight into that wall about 85% of the
way through.

The fix: partition the extraction by year instead of relying on a single offset walk.
Querying `recall_initiation_date` year by year (2008 through 2026) keeps every single
query's result count under the cap — the largest year, 2016, still only has ~3,000
records. 29,223 of the API's reported 29,224 records came back clean. The one that
didn't turned out to be the same problem as Problem 2, from the other direction.

## Problem 2: a date that breaks the model

That single missing record had a `recall_initiation_date` of `02121207` — not a valid
year, so it fell outside every year partition and never got pulled by the loop above.

Rather than drop it, the fix started with the evidence already sitting in the same
record: `report_date` was `2013-01-23` and `center_classification_date` was
`2013-01-14` — both squarely in a window that makes sense if the initiation date is
`20121207` (December 7, 2012), not `02121207`. That reads as a straightforward digit
transposition — 2012 typed as 0212 — not a genuinely ambiguous date. The record was
corrected and recovered rather than silently dropped or left as an unexplained gap.

That's the standard applied throughout this project: don't fix what you can't justify
with evidence from the record itself, and document the fix inline rather than let it
disappear into a diff.

## Problem 3: "state" isn't one field, it's three

The raw `state` field on each recall mixes three different kinds of value: valid two-letter
US postal codes (`CA`, `TX`, …), 395 rows that are blank or the literal string `"N/A"`,
and 20 rows where the source spells out a Canadian province name in full (`British
Columbia`, `Ontario`, `Quebec`, …) instead of using a code at all. Feed that column
directly into Tableau's geographic role for US states and a chunk of it either fails to
map or maps to nothing meaningful.

The fix: keep the original value untouched in a `state_raw` column, and build a second,
strict `state` column that only contains a value when it's a real US state/territory
code — everything else becomes null. Nothing is deleted; the raw and cleaned versions
sit side by side so the decision is auditable.

## Problem 4: there's no "why" field — so one had to be built

The most valuable question a recall dataset can answer — what's actually going wrong,
and how often — doesn't exist as a structured field anywhere in the source. It's buried
in `reason_for_recall`, a free-text field written by whoever filed the paperwork:
*"The product may be contaminated with Listeria monocytogenes,"* *"Products not
manufactured under GMP's,"* *"Contains statement does not declare Pollock."*

The fix: a set of ordered keyword rules that read that free text and assign each recall
to one of twelve categories — Undeclared Allergen, Listeria, Salmonella, E. coli, Foreign
Material, Heavy Metal Contamination, Pesticide/Chemical, Temperature Abuse/Spoilage,
Labeling/Misbranding, Insanitary/Processing, Other Pathogen/Contamination, or Other. The
first pass left about 21% of records in a generic "Other" bucket — too high to be useful.
Sampling that bucket surfaced patterns the first draft missed entirely: recalls for
elevated lead levels, recalls for spoilage and temperature abuse, and recalls phrased as
*"does not declare X"* instead of *"undeclared X"* — same underlying issue, different
wording. Adding rules for those brought "Other" down to about 17%. That residual is
called out explicitly wherever the category appears — a keyword heuristic on free text
will never be perfect, and pretending otherwise would undersell the rest of the pipeline.

## Problem 5: one event, many recall rows — and a bug caught before it shipped

Recalls don't happen in isolation. One contamination incident can trigger dozens of
separate recall filings — different firms, different product lines, different lot
numbers, all tied to the same underlying event. The largest single event in this dataset
spans 409 individual recall rows.

Before building a rollup table for these events, the natural instinct — "just take the
first value of each field per event" — needed checking, not assuming. Grouping the data
and measuring it directly showed that firm, state, country, and voluntary/mandated
status are *always* identical across every recall in a given event (0% of events have
more than one distinct value), so those roll up safely. Classification and recall cause
are not always identical — they vary in 2.2% and 0.7% of events respectively — so those
needed real rules instead: an event's classification rolls up to its most severe
classification across all its recalls, and its status only reads "Terminated" once every
recall under it is actually terminated. That second rule wasn't a guess — it was directly
motivated by inspecting the largest event in the dataset, which had 404 of 409 recalls
Terminated and 5 still sitting at Completed. Calling that event "Terminated" would have
been wrong.

Building this table also caught a real bug before it reached anyone: an early version of
the rollup assigned a result Series indexed by event ID onto an output table with a plain
sequential index, and pandas silently aligned by label instead of position — producing an
entire column of nulls that looked like a legitimate "not yet closed" result until the
row counts were checked against expectations. The fix was a one-line index alignment
correction, but it's the kind of silent failure that's easy to ship if you don't check
your output against a number you already know to be true.

That same rollup process also surfaced a genuine gap in the FDA's own data: two events,
covering four recall records, are marked `Terminated` but were never given a
`termination_date` in the source. That gap is preserved as a null and logged explicitly
in the pipeline's output report — not filled in with a guessed date.

## Problem 6: a dashboard that looked fine until dark mode

The dashboard supports both light and dark mode, following a design system where every
color is validated for colorblind-safety and contrast rather than picked by eye (the
severity trend, for instance, uses one hue at three lightness steps — Class I darkest,
Class III lightest — because classification is an ordered severity scale, not an
arbitrary set of categories, and coloring it that way is what the validator's ordinal
check is for).

The first render looked correct in light mode and subtly broken in dark mode: card
backgrounds stayed light while the page around them went dark, and KPI numbers turned
invisible — white text on a card that never got the memo. The cause was a CSS scoping
mistake, not a color mistake: a wrapper element re-declared the same custom properties
that the dark-mode override was targeting on a different element, so its descendants
inherited the hardcoded light value instead of cascading through to the override. It
rendered fine in the mode that happened to match the hardcoded default and broke
silently in the other one. Caught by actually loading the page in a headless browser in
both modes and screenshotting it, rather than trusting that "it validated" meant "it
renders" — a palette check and a render check are different guarantees, and this project
had already learned (see Problem 5) that catching that kind of thing costs one screenshot
and skipping it costs a shipped bug.

## What the pipeline produces

```
openFDA API
   │  extract, year-partitioned to work around the API's pagination cap
   ▼
data/raw/food_enforcement/   — untouched API responses, one file per page
   │  clean: fix the known date typo, parse dates, normalize state, categorize cause
   ▼
data/clean/recalls.csv       — 29,223 rows, one per recall
   │  roll up on event_id, with rules only where the data actually varies
   ▼
data/clean/events.csv        — 7,790 rows, one per real-world recall event
   │  pre-aggregate + render: no raw rows shipped to the browser
   ▼
dashboard/index.html         — a single self-contained, interactive HTML file
```

Every step is a small, reproducible Python script (`src/`), not a one-off notebook or a
manually edited spreadsheet — re-running the pipeline from scratch produces the same
output from the same source data. A parallel branch of the pipeline
(`src/build_hyper.py`) still produces a Tableau-ready extract, documented in
[`tableau/BUILD_SPEC.md`](tableau/BUILD_SPEC.md), if that path is picked back up.

## Status

Extraction, cleaning, the events model, and the dashboard are all done —
[`dashboard/index.html`](dashboard/index.html) is a state breakdown, a severity trend
over time, a cause breakdown, a view of the multi-recall events uncovered above, and a
box plot of resolution time by severity, all cross-referenced against the cleaning
decisions documented here. It's a single static
file: open it in a browser, no server or build step required. Built by hand in
HTML/CSS/SVG/vanilla JS rather than a charting library, following a documented
color-and-marks system (see `references/` in the `dataviz` skill this was built with) —
every categorical/ordinal color choice is validated for colorblind-safety and contrast
before use, not eyeballed. Verified in a headless browser in both light and dark mode
before shipping (no console errors, correct data, working tooltips and table-view
fallback).

## Running it

```bash
uv sync
uv run src/extract_recalls.py    # pull raw data from openFDA
uv run src/clean_recalls.py      # produce data/clean/recalls.csv
uv run src/build_events.py       # produce data/clean/events.csv
uv run src/build_dashboard.py    # produce dashboard/index.html
```

Then open `dashboard/index.html` directly in a browser — no server needed.

Full technical detail on every transformation — exact formulas, row counts, and the
generated validation reports — lives in
[`.claude/.codebase-info/data-pipeline.md`](.claude/.codebase-info/data-pipeline.md).
