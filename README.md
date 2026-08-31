# wareq

CLI-first, DuckDB-first data-quality and data-contract engine.

Validate data against contracts expressed as checks, get stable exit codes, and persist results idempotently.

## Status

Early development. The first vertical slice (a local DuckDB completeness check exposed via a Python CLI) is being specced and ticketed.

## Development

Requires Python >=3.11 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run pytest
uv run ruff format --check .
uv run ruff check .
uv run pyright
```

For the manual installed-CLI smoke test, see
[Manual CLI smoke QA](docs/manual-cli-smoke-qa.md).

## License

Apache-2.0
