"""Command-line interface for wareq."""

import typer

from wareq import __version__

app = typer.Typer(help="wareq: CLI-first, DuckDB-first data-quality engine.", no_args_is_help=True)


@app.callback()
def main() -> None:
    """wareq: CLI-first, DuckDB-first data-quality engine."""


@app.command()
def version() -> None:
    """Print the installed version."""
    typer.echo(f"wareq {__version__}")


if __name__ == "__main__":
    app()
