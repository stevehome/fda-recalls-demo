# Codebase Map — codebase-mapper

*Last Updated: 2026-07-20*

**Status: complete.** Portfolio project: a reproducible data-cleaning pipeline plus a
finished interactive dashboard, on openFDA Food Enforcement (recall) data. Started as a
Tableau demo, pivoted to a code-driven HTML dashboard on 2026-07-20 (Tableau Public
couldn't open the `.hyper` extract; Tableau's story feature was mid-rewrite) — see
[architecture.md](architecture.md) for the full pipeline status and
[planning/PLAN.md](../../planning/PLAN.md) for the original brainstorm.

## What this project is

A reproducible pipeline pulls ~29,200 FDA food recall records from the public openFDA
API, cleans and categorizes them (see [data-pipeline.md](data-pipeline.md) for every
decision made), and renders them into
[`dashboard/index.html`](../../dashboard/index.html) — a self-contained interactive
dashboard (state ranking, severity trend, cause breakdown, multi-recall events), no
server or GUI tool required to view it. The narrative write-up is in
[README.md](../../README.md).

## Documents

| Doc | Contents |
|---|---|
| [architecture.md](architecture.md) | Project goal, dataset choice, pipeline stage status, the Tableau pivot |
| [data-pipeline.md](data-pipeline.md) | Extraction, cleaning, events model, dashboard build — every decision made |
| [tech-landscape.md](tech-landscape.md) | Stack: Python/`uv`, httpx, pandas, hand-written HTML/CSS/SVG/JS |
| [directory-structure.md](directory-structure.md) | Current layout |
| [onboarding.md](onboarding.md) | Quick start, current state, possible next steps |

No `entry-points.md`, `modules.md`, `database.md`, `dependencies.md` (folded into
tech-landscape.md — few direct deps), `patterns.md`, or `coding-style.md` — the pipeline
is a handful of small, single-purpose scripts, not warranting separate docs for those.

## How to use this map

At session start, this file is auto-injected. Read the linked doc relevant to your task
before making changes.

## How to maintain this map

Run `update-codebase-map` if the dashboard's chart set changes materially, a filter
control is added, or the Tableau path is revived.
