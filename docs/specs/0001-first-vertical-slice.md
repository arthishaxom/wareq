# Spec: First vertical slice — local DuckDB completeness check via CLI

## Problem Statement

An app developer wants to catch data-quality problems before a migration merges. The first proof of the wareq engine: a local CLI that runs a completeness check against a DuckDB database, reports a stable pass/fail, and persists the result idempotently so reruns don't duplicate history.

## Solution

`wareq check` runs a hard-coded completeness check (`orders.customer_id` is required) against a local DuckDB database, prints a structured result, exits with a stable code (0 pass / 1 fail / 2 invocation or configuration error), and upserts the result into a SQLite result store keyed by a deterministic `run_id`.

## User Stories

1. As an app developer, I want to run a completeness check against a local DuckDB database, so that I can validate data before merging.
2. As an app developer, I want a stable exit code (0 pass / 1 fail / 2 error), so that CI can gate on the outcome.
3. As an app developer, I want a printed structured result (missing count, pass/fail, `run_id`), so that I can see what happened.
4. As an app developer, I want results persisted idempotently keyed by `run_id`, so that rerunning the same check doesn't duplicate history.
5. As a wareq developer, I want the check logic as a pure Python function, so that it is testable and the CLI stays thin.
6. As a wareq developer, I want passing and failing fixtures, so that both outcomes are proven.

## Implementation Decisions

- **CLI**: `wareq check --db <path> [--results-db <path>]` via Typer; a thin layer over a pure check function.
- **Check**: hard-coded completeness rule — `orders.customer_id` is required. SQL: `SELECT COUNT(*) FROM orders WHERE customer_id IS NULL`; pass iff count is zero.
- **Result**: a structured value (check name, dataset, missing count, pass/fail, `run_id`, timestamp).
- **Persistence**: SQLite result store, default `.wareq/results.db` (overridable via `--results-db`); `run_id` = deterministic hash of (db path + check name); upsert on rerun for idempotency.
- **Exit codes**: 0 all checks passed, 1 a check failed, 2 invocation or configuration error.
- **No YAML, no Pydantic, no adapters** in this slice — deferred per the vertical-slice lesson.

## Testing Decisions

- **One seam**: the CLI, tested end-to-end via `typer.testing.CliRunner` against temp DuckDB databases (passing and failing fixtures).
- Tests cover: pass → exit 0, fail → exit 1, invocation error → exit 2, printed output content, and idempotent persistence (run twice → one row per `run_id`).
- Prior art: `tests/test_cli.py` smoke test for the `version` command.

## Out of Scope

- YAML config shapes, Pydantic validation, shipped JSON Schemas
- Other check types (schema, freshness, row_count, referential_integrity, custom SQL)
- Snowflake/PySpark adapters, UI, API, scheduler, profiling
- Publishing to PyPI

## Further Notes

- First tracer bullet per the vertical-slice lesson; interface order is Python function first, then CLI.
- Governed by ADR-0001 (DuckDB-first).
- Package name `wareq` verified free on PyPI and GitHub.