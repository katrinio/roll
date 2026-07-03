# Development

A working guide for local development. Architecture and commands — see [model.md](model.md), terms — see [glossary.md](glossary.md).

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

If `.venv` already exists, this is usually enough:

```bash
pip install -e '.[dev]'
```

## Pre-commit

```bash
pre-commit install
pre-commit run --all-files
```

`pre-commit` uses the same `ruff` as CI.

## Checks

```bash
ruff check .
python -m unittest discover -s tests
```

## CLI

```bash
rl --help
rl init /path/to/archive
rl doctor
rl doctor --fix
rl normalize --tags
rl batch process
rl stats 2026
rl stats -v
```

`rl load` works off `stock.toml`, while `rl load --manual` lets you create a roll from the film dictionary without touching stock.

For `rl features add` and `rl tags add` you can enter several values separated by commas. Autocomplete works per value, duplicates aren't written, `_` is allowed inside a value.

## CI

GitHub Actions runs:
- `ruff check .`
- `python -m unittest discover -s tests`

The workflow triggers on pull requests and pushes to `main`.
