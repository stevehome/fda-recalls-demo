# Codebase Map — codebase-mapper

*Last Updated: 2026-07-15*

**Status: extract + clean done, Tableau build not started.** Portfolio project
demonstrating Tableau skills on openFDA Food Enforcement (recall) data — see
[architecture.md](architecture.md) for pipeline status and
[planning/PLAN.md](../../planning/PLAN.md) for the original brainstorm.

## What this project is

A reproducible pipeline pulls ~29,200 FDA food recall records from the public openFDA
API, cleans and categorizes them (see [data-pipeline.md](data-pipeline.md) for every
decision made), and will feed a Tableau dashboard (map + trend + category breakdown).

## Documents

| Doc | Contents |
|---|---|
| [architecture.md](architecture.md) | Project goal, dataset choice, pipeline stage status |
| [data-pipeline.md](data-pipeline.md) | Extraction + cleaning scripts, schema, every cleaning decision |
| [tech-landscape.md](tech-landscape.md) | Stack: Python/`uv`, httpx, pandas, Tableau |
| [directory-structure.md](directory-structure.md) | Current layout |
| [onboarding.md](onboarding.md) | Quick start, current state, next steps |

No `entry-points.md`, `modules.md`, `database.md`, `dependencies.md` (folded into
tech-landscape.md — only 2 direct deps), `patterns.md`, or `coding-style.md` — the
pipeline is two small scripts, not warranting separate docs for those yet. Revisit once
the Tableau workbook and any dimension tables exist.

## How to use this map

At session start, this file is auto-injected. Read the linked doc relevant to your task
before making changes.

## How to maintain this map

Once real code exists (extraction/cleaning scripts, a data model, a Tableau workbook),
run `update-codebase-map` to fill in the map properly — entry points, modules, patterns,
dependencies — rather than hand-editing this seed.
