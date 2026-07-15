# Tableau Build Spec — FDA Food Recalls Dashboard

*Last Updated: 2026-07-15*

A concrete, executable checklist for building the dashboard in Tableau Desktop/Public.
Both `data/clean/fda_recalls.hyper` (full Tableau Desktop) and `data/clean/recalls.csv`
+ `data/clean/events.csv` (Tableau Public — see the note in step 1) are already built
(see [data-pipeline.md](../.claude/.codebase-info/data-pipeline.md) for how). Facts
referenced below (row counts, date ranges) are current as of the last pipeline run — re-check
`data/clean/*_report.json` if you've re-run the pipeline since.

Data at a glance: 29,223 recalls / 7,790 events, `recall_initiation_date` spans
2008-02-22 to 2026-06-18, 52 distinct US states/territories represented, classification
split Class II 14,673 / Class I 12,809 / Class III 1,740 / Not Yet Classified 1.

---

## 1. Data source setup

**Tableau Public note:** the free Tableau Public desktop app restricts its Connect menu
to a small set of file types (Text/CSV, Excel, PDF, Spatial, Statistical, JSON) and
cannot open a standalone `.hyper` file directly — it builds its own internal extract
when you save/publish instead. If you're on Tableau Public, skip the `.hyper` file and
connect directly to the two CSVs instead:

1. Open Tableau Public, **Connect → Text File**, select `data/clean/recalls.csv`.
2. On the canvas, **Connect → Text File** again (or drag a new connection in) and add
   `data/clean/events.csv`.
3. Drag both onto the canvas and continue from step 2 below — relating on `event_id`
   works identically whether the source is the `.hyper` file or the two CSVs.

If you're on full Tableau Desktop (not Public), use the `.hyper` file — it's smaller
(9.2 MB vs. 17 MB across both CSVs) and has date/int typing already baked in:

1. Open Tableau, **Connect → To a File → More… → Hyper**, select `data/clean/fda_recalls.hyper`.
2. Drag both `recalls` and `events` onto the canvas. Tableau should auto-detect the
   relationship on `event_id` (same field name, compatible type) — verify it, or set it
   explicitly: **Relationship → event_id = event_id**. Leave it as a relationship (not a
   join or blend) so each sheet can use whichever table's grain it needs without
   duplicating rows.
3. Fix geographic roles: right-click `state` (on the `recalls` table) → **Geographic
   Role → State/Province**. Do the same for `events.state` if you build any sheet off
   that table's grain.
4. Rename the data source to `FDA Food Recalls` (top of the left pane) — this is what
   shows up in the published workbook.
5. **If connecting via the CSVs**, check the four date columns on `recalls`
   (`recall_initiation_date`, `center_classification_date`, `report_date`,
   `termination_date`) and four on `events` landed with a Date icon (#) in the Data
   pane, not Abc (string) — Tableau's text-file connector usually auto-detects `YYYY-MM-DD`
   correctly, but if any came in as strings, right-click → **Change Data Type → Date**.
   The `.hyper` file has this typing baked in already, so this step only applies to the
   Tableau Public / CSV path.

## 2. Calculated fields

Create these on the `recalls` table unless noted. Right-click in the Data pane →
**Create Calculated Field**.

| Name | Formula | Purpose |
|---|---|---|
| `Is Class I` | `IF [Classification] = "Class I" THEN 1 ELSE 0 END` | Enables `AVG()` → % Class I severity |
| `Severity Score` | `CASE [Classification]`<br>`WHEN "Class I" THEN 3`<br>`WHEN "Class II" THEN 2`<br>`WHEN "Class III" THEN 1`<br>`ELSE 0 END` | Single numeric severity measure for the map/KPIs |
| `Days to Termination` | `DATEDIFF('day', [Recall Initiation Date], [Termination Date])` | Null when not yet terminated (matches `cleaning_report.json`); used for the resolution-time view |
| `Map Color Value` | `CASE [Map Color By]`<br>`WHEN "Recall Count" THEN COUNT([Recall Number])`<br>`WHEN "% Class I (Most Severe)" THEN AVG([Is Class I])`<br>`WHEN "Avg Severity Score" THEN AVG([Severity Score])`<br>`END` | Backs the map-color parameter (step 3) |

On the `events` table:

| Name | Formula | Purpose |
|---|---|---|
| `Event Size Bucket` | `IF [Num Recalls] = 1 THEN "1 (single recall)"`<br>`ELSEIF [Num Recalls] <= 5 THEN "2–5"`<br>`ELSEIF [Num Recalls] <= 20 THEN "6–20"`<br>`ELSEIF [Num Recalls] <= 100 THEN "21–100"`<br>`ELSE "100+" END` | Buckets the heavily-skewed `num_recalls` (max 409) for a readable histogram |

## 3. Parameters

Create via the Data pane dropdown → **Create Parameter**.

- **`Map Color By`** — Data type: String. Allowable values: List — `"Recall Count"`,
  `"% Class I (Most Severe)"`, `"Avg Severity Score"`. Default: `"Recall Count"`. After
  creating, right-click it → **Show Parameter Control** (needed on the dashboard).

## 4. Worksheets

Build each as its own sheet, named exactly as below (dashboard wiring in step 5
references these names).

### Sheet: `Map — Recalls by State`
- Mark type: Filled Map (or Map if you prefer bubble sizing — filled map reads faster).
- Detail/Location: `State` (recalls table).
- Color: `Map Color Value`. Set a sequential palette (e.g. Orange, single-hue) —
  consistent low→high meaning across all three parameter options.
- Tooltip: include `State`, `Map Color Value` formatted, plus `COUNT(Recall Number)`
  and the state's top `Reason Category` (add `ATTR([Reason Category])` or a separate
  `INDEX`/`RANK` calc if you want the true mode — simplest is to just list count by
  category in the tooltip via a mini table calc, or skip if it overcomplicates the
  tooltip).
- Filter shelf: leave open for dashboard-level date filter (step 6).

### Sheet: `Trend — Recalls Over Time`
- Mark type: Line (or Area if stacking by classification).
- Columns: `YEAR(Recall Initiation Date)` (continuous, green pill).
- Rows: `COUNT(Recall Number)`.
- Color: `Classification` — use a consistent 4-color mapping (Class I most alarming
  color, e.g. red; Class III mildest, e.g. yellow/tan; Not Yet Classified neutral gray)
  and reuse this exact palette on every sheet that shows `Classification`.
- Note 2026 will show a partial-year drop-off (data through 2026-06-18) — consider a
  caption noting this so it doesn't read as a real decline.

### Sheet: `Reason — Recalls by Category`
- Mark type: Horizontal bar.
- Rows: `Reason Category`, sorted descending by `COUNT(Recall Number)`.
- Columns: `COUNT(Recall Number)`.
- Color: `Classification` (stacked bar) — shows severity mix within each cause, using
  the same palette as the trend sheet.
- Consider a reference line or label calling out `"Other"` as a heuristic bucket (~17%
  of rows) so viewers don't mistake it for a real category — see
  [data-pipeline.md](../.claude/.codebase-info/data-pipeline.md) for the exact rule set.

### Sheet: `Events — Size Distribution`
- Uses the `events` table grain — this is the sheet that justifies the events dimension
  table existing at all, so don't skip it.
- Mark type: Bar.
- Columns: `Event Size Bucket` (sorted by `Num Recalls` ascending, not alphabetically —
  set a manual sort order matching the bucket definitions).
- Rows: `COUNT(Event Id)`.
- Tooltip: mention the largest single event (409 recalls) as a callout, either in the
  tooltip or a text annotation on the dashboard.

### Sheet: `Detail — Recall Records` (drill-down table)
- Mark type: Automatic (table).
- Columns: `Recall Number`, `Recalling Firm`, `State`, `Classification`,
  `Reason Category`, `Product Description`, `Recall Initiation Date`, `Status`.
- Sort: `Recall Initiation Date` descending.
- This sheet stays empty/collapsed until a filter action drives it (step 6) — don't
  load all 29,223 rows by default on the dashboard; gate it behind a selection.

### Optional: `Resolution Time` (only if you want the response-time angle from the plan)
- Mark type: Box plot or histogram.
- Rows: `Days to Termination`.
- Columns: `Classification`.
- Story: does Class I (most severe) get resolved faster than Class III? A reasonable
  hypothesis to test visually.

## 5. Dashboard layout

New Dashboard → name it `FDA Food Recalls`. Size: Automatic or a fixed 1400×900 for
consistent Tableau Public rendering.

Suggested layout (tiled, top to bottom):
1. Title + 2-3 KPI text/number tiles across the top: total recalls, total events,
   % Class I, date range covered. Pull these from the sheets above (or build tiny
   single-value sheets) rather than hardcoding — they should update if the data refreshes.
2. `Map — Recalls by State` (left, ~50% width) next to `Trend — Recalls Over Time`
   (right, ~50% width), same row.
3. `Reason — Recalls by Category` (left, ~50%) next to `Events — Size Distribution`
   (right, ~50%), next row.
4. `Detail — Recall Records` at the bottom, initially minimized/hidden (floating,
   toggled visible by a "view details" action — see below), or just placed full-width
   and left showing all rows filtered by whatever's selected above.
5. Parameter control for `Map Color By` placed near the map.
6. A date range filter (`Recall Initiation Date`, continuous/relative) placed top-level,
   applied to **all sheets using this data source** (right-click the filter →
   **Apply to Worksheets → All Using This Data Source**).

## 6. Actions (cross-filtering)

Dashboard menu → **Actions → Add Action**.

1. **Filter action**: Source sheets `Map — Recalls by State`, `Reason — Recalls by
   Category` → Target sheets: all others except `Detail — Recall Records`. Run on:
   **Select**. Clearing the selection: **Show all values**. This is the core
   cross-filter behavior — click a state or a cause, everything else updates.
2. **Filter action to the detail table**: Source: any/all summary sheets → Target:
   `Detail — Recall Records`. Run on: **Select**. This is what makes the detail table a
   drill-down instead of a firehose.
3. (Optional) **Highlight action** instead of/in addition to filtering on the trend line,
   if you want hovering to highlight without fully filtering other views — a nice touch
   but not required by the plan.

## 7. Formatting notes

- Keep the `Classification` color mapping (Class I/II/III/Not Yet Classified) identical
  across every sheet that uses it — Tableau will do this automatically if you set it
  once on the data source's default color for that field (right-click the field in the
  Data pane → **Default Properties → Color**).
- Same for `Reason Category` if it appears as a color encoding anywhere beyond the
  category bar sheet.
- Use a clear title and a one-line subtitle stating the data source and pull date (from
  `data/raw/food_enforcement/manifest.json`) so the dashboard is self-documenting.

## 8. QA checklist before publishing

- [ ] Total recall count on the dashboard KPI matches `29223` (or the current
      `cleaning_report.json` `output_rows` if re-pulled)
- [ ] Total event count matches `7790` (or current `events_report.json` `output_event_rows`)
- [ ] Map renders all 50 states without "unknown" location warnings (Tableau will flag
      unrecognized `State` values — should be none, since `state` was already nulled for
      anything non-US/invalid in `clean_recalls.py`)
- [ ] `Map Color By` parameter switches correctly between all three options
- [ ] Clicking a state filters the trend/category/events sheets; clicking empty space
      clears the filter
- [ ] Detail table only shows rows relevant to the current selection, not all 29,223 by
      default

## 9. Publishing

- If using Tableau Public: **Server → Tableau Public → Save to Tableau Public**. Data is
  already public federal data (openFDA), so no sensitivity concerns publishing the
  extract itself.
- Save the packaged workbook (`.twbx`) into `tableau/` in this repo alongside this spec
  once built, so the repo captures the finished artifact, not just the recipe.
