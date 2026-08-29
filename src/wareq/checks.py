"""Pure DuckDB checks and their structured results."""

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

import duckdb

CHECK_NAME = "orders.customer_id_completeness"


@dataclass(frozen=True)
class CheckResult:
    check_name: str
    dataset: str
    missing_count: int
    passed: bool
    run_id: str
    timestamp: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def run_completeness_check(database_path: Path) -> CheckResult:
    """Run the required-customer-id check against a DuckDB database."""
    resolved_path = database_path.expanduser().resolve(strict=True)
    run_id = sha256(f"{resolved_path}\n{CHECK_NAME}".encode()).hexdigest()
    with duckdb.connect(str(resolved_path), read_only=True) as connection:
        row = connection.execute("SELECT COUNT(*) FROM orders WHERE customer_id IS NULL").fetchone()
    if row is None or not isinstance(row[0], int):
        raise RuntimeError("Completeness query returned an invalid result")
    missing_count = row[0]
    return CheckResult(
        check_name=CHECK_NAME,
        dataset="orders",
        missing_count=int(missing_count),
        passed=missing_count == 0,
        run_id=run_id,
        timestamp=datetime.now(UTC).isoformat(),
    )
