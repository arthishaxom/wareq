# Production data-quality development lifecycle

**Date:** 2026-08-29
**Scope:** How to move wareq from its first vertical slice toward realistic local and CI validation.

## Findings from primary sources

### 1. Delivery is an iterative loop, not a single manual-QA phase

Production teams normally move a small change through a loop of local development, automated checks, review, an isolated environment, controlled release, and feedback. The useful operational metrics are deployment frequency, lead time for changes, change failure rate, and time to restore service. These are the four DORA metrics described by Google Cloud's documentation of the DORA research: [Four Keys metrics](https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance).

For wareq, the equivalent loop is: implement one check/configuration capability, run unit and CLI integration tests, review the contract and output semantics, run it on representative datasets, then wire the same command into CI.

### 2. CI and deployment gates should be explicit and reproducible

GitHub environments can restrict which branches trigger a job, require approval, apply protection rules, and limit secret access. See [GitHub deployment environments](https://docs.github.com/en/actions/concepts/workflows-and-actions/deployment-environments).

Wareq is a CLI rather than a deployed service, so the analogous gate is a repository CI job: install from the lockfile, run static checks and tests, create a known DuckDB fixture, run the CLI, and fail the job on exit code 1 or 2. A later release workflow can publish a package only after the same checks pass.

### 3. Realistic local data should be loaded in bulk and kept reproducible

DuckDB recommends bulk import from formats such as Parquet or CSV when a source can export them, and cautions against row-by-row insertion for larger data. See [DuckDB data import](https://duckdb.org/docs/guides/import/overview). DuckDB can create a persistent table from a CSV with `CREATE TABLE ... AS SELECT * FROM 'file.csv'`; see [DuckDB CSV import](https://duckdb.org/docs/current/data/csv/overview).

Therefore, a manual-QA harness should copy or reference a versioned sample, load it into a disposable DuckDB database, and apply deterministic mutations. The mutation step should record the mutation name and seed so a failure can be reproduced.

### 4. Small fixture files in the test tree are standard practice

The pytest documentation explicitly describes fixed fixtures as a way to make tests reliable and repeatable. It also recommends loading data files through fixtures and identifies adding data files under the `tests` folder as a good approach: [pytest fixtures and sharing test data](https://docs.pytest.org/en/6.2.x/fixture.html).

This does not mean committing arbitrary datasets. A repository fixture should be small, synthetic or legally redistributable, non-sensitive, deterministic, and relevant to a test. Large Kaggle downloads, production extracts, credentials, and personally identifiable information belong outside Git. If a public dataset is needed, record its source, license, download instructions, and a checksum; commit only a small derived sample when its license permits it.

### 5. Scripted QA and exploratory QA serve different purposes

Scripted checks are valuable because they are repeatable and can be run by anyone. They should exercise the same public interface that users rely on. However, exploratory testing intentionally goes beyond pre-written cases to discover unexpected behavior. Martin Fowler describes exploratory testing as a complementary activity that probes the boundaries of scripted coverage: [Exploratory Testing](https://martinfowler.com/bliki/ExploratoryTesting.html) and [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html).

For wareq, a small Phase 1 helper script is appropriate as a convenience wrapper around the real CLI. It should create disposable data, run named scenarios, and print observations. It should not become a second implementation of check logic or pretend to replace pytest. After a manual discovery, the expected behavior should be captured in an automated test where practical.

## Practical lifecycle for this repository

1. **Define the behavior.** Write the contract shape, check semantics, result fields, and exit-code behavior before broadening implementation.
2. **Build the smallest vertical slice.** Add one capability end to end: parsing, validation, execution, output, persistence, and tests.
3. **Automate the stable path.** Keep unit tests for pure logic and CLI integration tests for exit codes, output, and result-store behavior.
4. **Review and manually probe.** Use a disposable DuckDB database containing clean, boundary, and deliberately corrupted data. Manual testing is exploratory validation, not a replacement for repeatable tests.
5. **Run in CI.** Use the checked-in `uv.lock`, the same commands developers run locally, and small deterministic fixtures. Add larger Kaggle data as a separate opt-in or scheduled job if it makes CI slow.
6. **Release deliberately.** Tag a version only after the CI gate and a short release checklist pass. Record known limitations and examples.
7. **Learn from failures.** Turn every discovered bug into a regression test; track false positives, false negatives, runtime, and the kinds of data failures users actually encounter.

## Implications for wareq

- Manual QA can start now for the existing slice, because the CLI already has a usable seam: a DuckDB file in and JSON result plus exit code out.
- Phase 1 should commit only tiny synthetic fixtures (or generate them in tests); it should not commit Kaggle or production data.
- Phase 1 may include a lightweight helper script for repeatable scenarios, paired with exploratory sessions where the tester tries inputs outside the script.
- The next implementation should introduce a minimal contract-driven command before adding many check types. Otherwise the project will accumulate hard-coded behavior that is difficult to generalize.
- Kaggle data should be treated as a compatibility and scale corpus, not as the first correctness oracle. Its schema must be mapped into a contract, and expected outcomes must be stated explicitly.
- Error injection is valuable only when each injected defect has a known expected result. Keep clean and mutated inputs separate so a passing check cannot be confused with a missing fixture defect.
