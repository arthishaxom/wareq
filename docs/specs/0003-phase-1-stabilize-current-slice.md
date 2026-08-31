# Phase 1: Stabilize the current slice

## Problem Statement

Wareq has a working first vertical slice for one DuckDB completeness check, but the workflow is not yet proven as a reproducible developer experience. The repository lacks a CI quality gate, a small shared fixture corpus, and concise guidance for manually running the installed CLI. The current behavior around empty datasets and result history also needs to be made explicit before the project grows.

Status: this is a planning/specification document. Phase 1 is not complete until the linked GitHub implementation tickets are merged, verified, and closed.

## Solution

Stabilize the current slice with a repository CI gate, tiny synthetic fixtures, automated CLI coverage at the existing end-to-end seam, and a manual smoke-test runbook. Preserve the current completeness semantics and result-store behavior for this phase while documenting them as provisional decisions. The first contract-aware result identity design belongs in Phase 2.

## User Stories

1. As a developer, I want the locked project environment and quality checks to run in CI, so that regressions are caught before changes merge.
2. As a developer, I want small synthetic datasets available in the repository, so that tests are deterministic and understandable during review.
3. As a developer, I want automated tests to exercise the real CLI, so that exit codes, JSON output, DuckDB execution, and result persistence are validated together.
4. As a developer, I want to run a short manual smoke test against a real DuckDB database, so that I can verify the installed CLI experience before a release or risky change.
5. As a developer, I want clean data to pass the completeness check, so that valid input is accepted.
6. As a developer, I want missing `customer_id` values to fail with a useful count, so that data defects are visible.
7. As a developer, I want missing databases, tables, and columns to produce configuration errors, so that invalid inputs are distinguishable from failed checks.
8. As a developer, I want empty datasets to pass completeness, so that completeness means no missing values rather than non-empty volume.
9. As a developer, I want repeated runs against the same database and check to remain idempotent, so that the result store does not accumulate duplicates.
10. As a developer, I want the provisional result-history behavior documented, so that later contract and data-fingerprint work can intentionally replace it.
11. As a maintainer, I want every discovered Phase 1 defect converted into a regression test, so that manual findings remain protected.

## Implementation Decisions

- The highest test seam is the existing CLI boundary: a DuckDB database enters through the public command, and JSON output, exit code, and SQLite result-store state are observed.
- CI will install from the committed lockfile and run pytest, Ruff, BasedPyright, and package/build verification.
- Only tiny, synthetic, non-sensitive fixtures will be committed. Large Kaggle data, production extracts, and unclear-license data remain outside Git.
- Tests may load fixture files into temporary DuckDB databases; tests must not depend on network access or a persistent local database.
- Phase 1 manual QA is a concise runbook executed against the real CLI. A dedicated helper script is optional and should only be added if repeated setup becomes burdensome.
- Manual QA is exploratory and smoke-oriented; repeatable known behavior belongs in automated tests.
- Completeness passes for an empty dataset because zero missing values satisfies the check. Non-empty requirements belong to a future row-count check.
- The current result-store idempotency behavior is retained provisionally: rerunning the same database/check identity upserts one result. Contract-aware check identity and data-content-aware history are deferred to Phase 2.
- Existing stable exit codes remain: `0` for all checks passed, `1` for a failed check, and `2` for invocation or configuration errors.
- No YAML contracts, additional check types, Kaggle ingestion workflow, or production-scale benchmark is included in Phase 1.

## Testing Decisions

- Tests assert externally observable behavior rather than implementation details.
- Existing CLI integration tests remain the primary prior art and should be extended with fixture-backed scenarios where useful.
- Automated coverage must include clean data, missing values, empty data, missing database, missing table, missing column, invalid result-store target, stable exit codes, structured output, and idempotent persistence.
- Manual smoke QA must verify the installed command, readable output, exit codes, and result-store behavior from a clean checkout.
- Exploratory QA should try inputs outside the written scenarios and record any surprising behavior for triage and regression coverage.

## Out of Scope

- YAML contract parsing or validation.
- General dataset and check selection.
- New data-quality pillars or check types.
- Large or remote dataset management.
- Production database adapters, scheduler, service API, dashboard, or cloud deployment.
- Redesigning result identity and historical result retention beyond the provisional Phase 1 behavior.

## Further Notes

Phase 1 is complete when CI is green, the fixture-backed automated workflow passes, the manual smoke runbook is reproducible, the agreed semantics are documented, and no known Phase 1 defect remains without either a fix or an explicit decision. Phase 2 begins with the minimal YAML contract boundary plus the first contract-aware result identity model.
