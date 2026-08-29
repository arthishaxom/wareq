"""SQLite persistence for check results."""

import sqlite3
from pathlib import Path

from wareq.checks import CheckResult


def save_result(database_path: Path, result: CheckResult) -> None:
    """Create the result store and idempotently save one result."""
    database_path.expanduser().parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path.expanduser()) as connection:
        _ = connection.execute(
            """
            CREATE TABLE IF NOT EXISTS results (
                run_id TEXT PRIMARY KEY,
                check_name TEXT NOT NULL,
                dataset TEXT NOT NULL,
                missing_count INTEGER NOT NULL,
                passed INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )
        _ = connection.execute(
            """
            INSERT INTO results (run_id, check_name, dataset, missing_count, passed, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(run_id) DO UPDATE SET
                check_name = excluded.check_name,
                dataset = excluded.dataset,
                missing_count = excluded.missing_count,
                passed = excluded.passed,
                timestamp = excluded.timestamp
            """,
            (
                result.run_id,
                result.check_name,
                result.dataset,
                result.missing_count,
                result.passed,
                result.timestamp,
            ),
        )
