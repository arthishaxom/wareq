# Mission: Build a Stack-Agnostic Data Quality Engine, Positioned at the App Developer

## Why

Ashish's internship built a Data Quality engine on Databricks that was locked to Databricks, configured via SQL tables, and had no local mode. He is now applying for Data Engineering + Python backend roles, and needs one deep, authentic, resume-worthy project. The research (2026-08) proved the DQ-engine category is high-value but crowded, and the unoccupied, defensible position is **data contract enforcement at the application developer's CI — before a migration merges** (pain point #3). We build the engine to learn it deeply; the app-developer story is the positioning; honest vs-Soda benchmarks are the proof.

## Success looks like

- A working, tested, Apache-2.0 Python engine: 3 YAML config shapes → Pydantic validation → shipped JSON Schemas → `wareq validate` + `wareq run`
- A DuckDB adapter that runs all 6 check types (schema, completeness, freshness, row_count, referential_integrity, custom SQL) with a sub-500ms local loop
- An idempotent SQLite result store keyed by `run_id`
- A CI recipe that warns an app developer before a migration merges (catalog-free, app-repo-first)
- Published honest benchmarks vs Soda Core, and a README that names Soda v4 / GX Cloud / Provero and states exactly what we re-implement and what we do differently
- A renamed project (verified free on PyPI + GitHub) — `dqx` collides with Databricks Labs; `wareq` is verified available

## Constraints

- Core engine: Python 3.11+
- Adapters: DuckDB first (Phase 1); Snowflake/PySpark deferred (Phase 2)
- Config: YAML-in-Git, 3 shapes (`wareq.yaml` + `profiles.yaml` + per-dataset contracts), same repo as the pipeline
- CLI-first, stable exit codes; no scheduler/daemon in v1 (teams own orchestration)
- Idempotent result writes; no check-level data-version watermark (does not exist in industry)
- License: Apache-2.0 from day one
- Keep lessons + reference docs updated in the learning workspace as we build

## Out of scope (v1)

- Snowflake/PySpark adapters, FastAPI backend, React dashboard, AI explainer, scheduler, auto-profiling suggestions
- BigQuery, Redshift, Polars adapters
- Claiming the lane is "empty" — we cite the small OSS tools that exist (Metaguard, FixFlow, dbt-guard…) and pick the thin slice: catalog-free, app-repo-first, app-developer-first UX

## Provenance

Migrated from `/home/justashish/Learning/project-ideas/wareq/MISSION.md` (2026-08-20). The learning workspace is an append-only archive; this file is the canonical mission.