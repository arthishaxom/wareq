"""End-to-end tests for the CLI entry point."""

import json
import sqlite3
from pathlib import Path

import duckdb
from typer.testing import CliRunner

from wareq import __version__
from wareq.cli import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert f"wareq {__version__}" in result.stdout


def make_database(path: Path, rows: list[tuple[object]]) -> None:
    with duckdb.connect(str(path)) as connection:
        connection.execute("CREATE TABLE orders (customer_id INTEGER)")
        if rows:
            connection.executemany("INSERT INTO orders VALUES (?)", rows)


def test_check_passes_and_prints_structured_result(tmp_path: Path) -> None:
    database = tmp_path / "orders.duckdb"
    make_database(database, [(1,), (2,)])

    result = runner.invoke(
        app, ["check", "--db", str(database), "--results-db", str(tmp_path / "results.db")]
    )

    assert result.exit_code == 0
    output = json.loads(result.stdout)
    assert output["check_name"] == "orders.customer_id_completeness"
    assert output["dataset"] == "orders"
    assert output["missing_count"] == 0
    assert output["passed"] is True
    assert output["run_id"]
    assert output["timestamp"]


def test_check_fails_when_customer_id_is_null(tmp_path: Path) -> None:
    database = tmp_path / "orders.duckdb"
    make_database(database, [(1,), (None,), (None,)])

    result = runner.invoke(
        app, ["check", "--db", str(database), "--results-db", str(tmp_path / "results.db")]
    )

    assert result.exit_code == 1
    output = json.loads(result.stdout)
    assert output["missing_count"] == 2
    assert output["passed"] is False


def test_check_empty_orders_passes(tmp_path: Path) -> None:
    database = tmp_path / "orders.duckdb"
    make_database(database, [])

    result = runner.invoke(
        app, ["check", "--db", str(database), "--results-db", str(tmp_path / "results.db")]
    )

    assert result.exit_code == 0
    assert json.loads(result.stdout)["missing_count"] == 0


def test_check_configuration_error_returns_two(tmp_path: Path) -> None:
    result = runner.invoke(app, ["check", "--db", str(tmp_path / "missing.duckdb")])

    assert result.exit_code == 2
    assert "error" in result.stderr.lower()


def test_check_missing_table_returns_two(tmp_path: Path) -> None:
    database = tmp_path / "orders.duckdb"
    duckdb.connect(str(database)).close()

    result = runner.invoke(
        app, ["check", "--db", str(database), "--results-db", str(tmp_path / "results.db")]
    )

    assert result.exit_code == 2
    assert "error" in result.stderr.lower()


def test_check_missing_customer_id_column_returns_two(tmp_path: Path) -> None:
    database = tmp_path / "orders.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.execute("CREATE TABLE orders (order_id INTEGER)")

    result = runner.invoke(
        app, ["check", "--db", str(database), "--results-db", str(tmp_path / "results.db")]
    )

    assert result.exit_code == 2
    assert "error" in result.stderr.lower()


def test_check_upserts_one_result_on_rerun(tmp_path: Path) -> None:
    database = tmp_path / "orders.duckdb"
    results_db = tmp_path / "results.db"
    make_database(database, [(1,)])
    args = ["check", "--db", str(database), "--results-db", str(results_db)]

    first = runner.invoke(app, args)
    second = runner.invoke(app, args)

    assert first.exit_code == second.exit_code == 0
    with sqlite3.connect(results_db) as connection:
        assert connection.execute("SELECT COUNT(*) FROM results").fetchone() == (1,)


def test_failed_check_is_persisted_idempotently(tmp_path: Path) -> None:
    database = tmp_path / "orders.duckdb"
    results_db = tmp_path / "results.db"
    make_database(database, [(None,)])
    args = ["check", "--db", str(database), "--results-db", str(results_db)]

    first = runner.invoke(app, args)
    second = runner.invoke(app, args)

    assert first.exit_code == second.exit_code == 1
    with sqlite3.connect(results_db) as connection:
        assert connection.execute("SELECT COUNT(*) FROM results").fetchone() == (1,)
        assert connection.execute("SELECT missing_count, passed FROM results").fetchone() == (1, 0)


def test_run_id_is_stable_for_equivalent_paths(tmp_path: Path, monkeypatch) -> None:
    database = tmp_path / "orders.duckdb"
    make_database(database, [(1,)])
    results_db = tmp_path / "results.db"

    absolute = runner.invoke(app, ["check", "--db", str(database), "--results-db", str(results_db)])
    monkeypatch.chdir(tmp_path)
    relative = runner.invoke(app, ["check", "--db", database.name, "--results-db", str(results_db)])

    assert json.loads(absolute.stdout)["run_id"] == json.loads(relative.stdout)["run_id"]


def test_check_without_db_returns_two() -> None:
    result = runner.invoke(app, ["check"])

    assert result.exit_code == 2
