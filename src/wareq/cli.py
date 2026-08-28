"""Command-line interface for wareq."""

import json
import sqlite3
from pathlib import Path

import duckdb
import typer

from wareq import __version__
from wareq.checks import run_completeness_check
from wareq.results import save_result

app = typer.Typer(help="wareq: CLI-first, DuckDB-first data-quality engine.", no_args_is_help=True)
DB_OPTION = typer.Option(..., "--db", exists=False, dir_okay=False)
RESULTS_DB_OPTION = typer.Option(Path(".wareq/results.db"), "--results-db", dir_okay=False)


@app.callback()
def main() -> None:
    """wareq: CLI-first, DuckDB-first data-quality engine."""


@app.command()
def version() -> None:
    """Print the installed version."""
    typer.echo(f"wareq {__version__}")


@app.command()
def check(
    db: Path = DB_OPTION,
    results_db: Path = RESULTS_DB_OPTION,
) -> None:
    """Run the orders.customer_id completeness check."""
    try:
        result = run_completeness_check(db)
        save_result(results_db, result)
    except (OSError, duckdb.Error, sqlite3.Error) as error:
        typer.echo(f"error: {error}", err=True)
        raise typer.Exit(code=2) from error
    typer.echo(json.dumps(result.as_dict(), sort_keys=True))
    if not result.passed:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
