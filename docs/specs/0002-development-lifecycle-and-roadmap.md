# Development lifecycle and roadmap

## Agreed strategy

Wareq should be developed through small, complete, testable increments. The project should first stabilize the current vertical slice, then introduce the contract boundary and result identity model, then generalize one check at a time, and finally validate against realistic datasets and release-quality workflows.

## Phases

### Phase 1 — Stabilize the current slice

Status: planned/open until the Phase 1 implementation tickets are completed and verified.

- Add a CI workflow using the locked `uv` environment.
- Add reproducible DuckDB fixtures and a manual QA harness.
- Probe clean, boundary, malformed, and deliberately corrupted data.
- Decide the semantics of empty datasets and result history.
- Improve user-facing errors.

### Phase 2 — Introduce the contract boundary

Add a minimal YAML contract that declares a dataset and its checks. Add contract validation and make the CLI execute the validated contract rather than a hard-coded dataset/check. Define the contract-aware check identity, `run_id`, and provisional result-history semantics here so later checks and persisted results remain stable.

### Phase 3 — Generalize checks

Add one check type at a time, in this order unless later evidence changes it: completeness, row count, schema, freshness, referential integrity, and custom SQL. Each check must have contract examples, passing/failing fixtures, configuration-error coverage, and CLI behavior documented.

### Phase 4 — Realistic data validation

Load small, mapped samples from Kaggle or comparable public datasets into DuckDB. Keep clean and intentionally mutated copies. Every injected defect must have a declared expected result and become a regression test when a bug is found.

### Phase 5 — Release quality

Harden stable JSON output, exit codes, contract versioning, failure details, performance measurement, CI integration documentation, and release/compatibility policy. Revisit result identity here only for compatibility hardening; the first design belongs in Phase 2.

## Working principles

- Make every change small, reviewable, reproducible, and recoverable.
- Run unit tests and CLI integration tests continuously; manual QA is exploratory validation, not a replacement for automated tests.
- Use the highest useful test seam: for the CLI workflow, a DuckDB input and observable JSON/exit-code/result-store output.
- Convert every discovered defect into a regression test.
- Optimize first for proving one complete real workflow, not for maximizing the number of check types.

## Phase 1 questioning scope

Before implementation, resolve the Phase 1 decisions around CI requirements, fixture and QA-data shape, error-injection strategy, empty-dataset behavior, provisional result-history semantics, and the definition of done. These decisions will be used to produce the implementation spec and GitHub ticket.
