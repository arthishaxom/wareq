"""Smoke tests for the CLI entry point."""

from typer.testing import CliRunner

from wareq import __version__
from wareq.cli import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert f"wareq {__version__}" in result.stdout
