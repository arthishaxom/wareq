# Wareq

A CLI-first, DuckDB-first data-quality and data-contract engine. It validates data against contracts expressed as checks, reports results with stable exit codes, and persists results idempotently.

## Language

**Check**:
A single validation rule applied to a dataset (e.g. "orders.customer_id is required").
_Avoid_: rule, assertion, test

**Completeness check**:
A check that a required column has no NULL values.
_Avoid_: null check, required-field check

**Contract**:
The set of checks and expectations declared for a dataset, expressed as YAML in Git (v1).
_Avoid_: schema, spec, profile

**Dataset**:
A named table (or view) in a DuckDB database that checks run against.
_Avoid_: table, source, relation

**Run**:
One execution of a check against a dataset, identified by a deterministic `run_id`.
_Avoid_: execution, invocation

**Result**:
The structured outcome of a run (pass/fail, counts, timestamps), persisted idempotently.
_Avoid_: report, output, artifact

**Result store**:
The SQLite database where results are persisted, keyed by `run_id`.
_Avoid_: database, warehouse, sink

**Exit code**:
The stable process status of a CLI invocation: `0` all checks passed, `1` a check failed, `2` invocation or configuration error.
_Avoid_: return code, status code

## Accepted decisions

- Python >=3.11, managed with `uv`; `uv.lock` is committed.
- `src/` layout, Typer CLI, pytest, Ruff, Pyright.
- DuckDB-first; Snowflake/PySpark deferred from v1.
- YAML-in-Git contracts in the same repository.
- SQLite result store with idempotent writes keyed by `run_id`.
- No UI, backend/API, AI, scheduler, profiling, or cloud/Spark adapters in v1.
- Apache-2.0 license.