# Agent instructions

## Toolchain

- Use `uv` for all Python environment and dependency management.
- Do not use `pip`, `pyenv`, Poetry, `venv`, or `virtualenv` directly.
- Use `uv add`, `uv run`, and commit `uv.lock`.

## Agent skills

### Issue tracker

Issues and specs live as GitHub issues in this repo; use the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Domain docs

Single-context: one `CONTEXT.md` at the repo root plus `docs/adr/` for decisions. See `docs/agents/domain.md`.