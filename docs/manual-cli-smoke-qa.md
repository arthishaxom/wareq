# Manual CLI smoke QA

This runbook verifies the installed `wareq` command against a disposable local
DuckDB database. It is an exploratory release/changeset check; repeatable
expected behavior belongs in the automated CLI tests.

## Prepare a clean environment

From a clean checkout, install the locked project environment with [uv]:

```bash
uv sync --locked
```

Confirm that the installed command is available:

```bash
uv run wareq version
```

The command should print `wareq 0.1.0` (or the version in the checkout).

Create a disposable workspace. The commands below assume a POSIX shell and
keep all smoke-test files outside the repository:

```bash
QA_DIR="$(mktemp -d)"
export QA_DIR
```

## Create the smoke-test database

Create a database containing a clean table, a table with missing IDs, and an
empty table. The CLI always checks `orders.customer_id`.

```bash
uv run python - <<'PY'
import os
import duckdb

database = os.path.join(os.environ["QA_DIR"], "orders.duckdb")
with duckdb.connect(database) as connection:
    connection.execute("CREATE TABLE orders (customer_id INTEGER)")
    connection.execute("INSERT INTO orders VALUES (1), (2), (3)")
    connection.execute("CREATE TABLE orders_with_nulls (customer_id INTEGER)")
    connection.execute("INSERT INTO orders_with_nulls VALUES (1), (NULL), (NULL)")
    connection.execute("CREATE TABLE empty_orders (customer_id INTEGER)")
PY
```

## Run the checks

Use a result-store path inside the disposable workspace so the smoke test does
not modify a developer's default `.wareq/results.db`.

```bash
RESULTS_DB="$QA_DIR/results.db"
uv run wareq check --db "$QA_DIR/orders.duckdb" --results-db "$RESULTS_DB"
echo "exit code: $?"
```

Expected observation: exit code `0` and JSON containing these fields:

```json
{
  "check_name": "orders.customer_id_completeness",
  "dataset": "orders",
  "missing_count": 0,
  "passed": true,
  "run_id": "<stable non-empty value>",
  "timestamp": "<non-empty value>"
}
```

To exercise the failing path, create a disposable database whose
`orders.customer_id` contains nulls, then run the check:

```bash
uv run python - <<'PY'
import os
import duckdb

database = os.path.join(os.environ["QA_DIR"], "null-orders.duckdb")
with duckdb.connect(database) as connection:
    connection.execute("CREATE TABLE orders (customer_id INTEGER)")
    connection.execute("INSERT INTO orders VALUES (1), (NULL), (NULL)")
PY
uv run wareq check --db "$QA_DIR/null-orders.duckdb" --results-db "$QA_DIR/failing-results.db"
echo "exit code: $?"
```

The expected result is exit code `1`, `"passed": false`, and
`"missing_count": 2`.

An empty `orders` table is expected to pass with exit code `0` and
`"missing_count": 0`: completeness checks missing values, not row volume.

## Check configuration errors

Each of these should print an error on stderr and exit with code `2`:

```bash
uv run wareq check --db "$QA_DIR/does-not-exist.duckdb"

uv run python - <<'PY'
import os
import duckdb

database = os.path.join(os.environ["QA_DIR"], "missing-table.duckdb")
with duckdb.connect(database):
    pass
PY
uv run wareq check --db "$QA_DIR/missing-table.duckdb" --results-db "$QA_DIR/errors.db"
```

Create an `orders` table without `customer_id` and run the check against it:

```bash
uv run python - <<'PY'
import os
import duckdb

database = os.path.join(os.environ["QA_DIR"], "missing-column.duckdb")
with duckdb.connect(database) as connection:
    connection.execute("CREATE TABLE orders (order_id INTEGER)")
PY
uv run wareq check --db "$QA_DIR/missing-column.duckdb" --results-db "$QA_DIR/column-errors.db"
echo "exit code: $?"
```

This missing-column case must return `2`, as must invocation errors such as
omitting `--db`.

## Inspect persistence and rerun behavior

Run the clean check twice with the same database and result-store paths:

```bash
uv run wareq check --db "$QA_DIR/orders.duckdb" --results-db "$RESULTS_DB"
uv run wareq check --db "$QA_DIR/orders.duckdb" --results-db "$RESULTS_DB"
```

Inspect the SQLite store:

```bash
uv run python - "$RESULTS_DB" <<'PY'
import sqlite3
import sys

with sqlite3.connect(sys.argv[1]) as connection:
    print(connection.execute("SELECT COUNT(*) FROM results").fetchone()[0])
    print(connection.execute(
        "SELECT run_id, check_name, dataset, missing_count, passed, timestamp FROM results"
    ).fetchall())
PY
```

The count should be `1`. The repeated run upserts the same deterministic
`run_id`; it does not append a duplicate result. This result-history behavior
is provisional for Phase 1 and may be replaced by content-aware history later.

When finished, remove the disposable workspace:

```bash
rm -rf "$QA_DIR"
```

Do not use production data or download large Kaggle datasets for this check.
Phase 1 smoke QA uses only tiny, disposable synthetic data. Larger or
real-world compatibility data is outside this workflow.

[uv]: https://docs.astral.sh/uv/
