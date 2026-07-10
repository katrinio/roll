# Development

A working guide for local development. Architecture and command effects — see [docs/architecture.md](architecture.md), terms and exact rules — see [docs/reference.md](reference.md), quick start — see [docs/getting-started.md](getting-started.md).

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
PYTHONPATH=src python -m unittest discover -s tests
```

## CLI Map

| Flow | Command | Reads | Writes | Auto-fix |
|---|---|---|---|---|
| Setup | `rl init /path/to/archive` | filesystem | global config, workspace | no |
| Config | `rl config`, `rl config lang`, `rl config lang EN`, `rl config lang RU` | global config | global config | yes, via `rl doctor --fix` |
| Stock | `rl stock add`, `rl stock list` | config, vocab, stock | stock | no |
| Roll creation | `rl load`, `rl load --manual` | stock, vocab | roll, stock | no |
| Roll status | `rl stock process`, `rl stock failed`, `rl batch process` | roll | roll | no |
| Metadata | `rl features add`, `rl tags add`, `rl batch` | roll, vocab | roll, vocab | no |
| Read-only | `rl search`, `rl scan`, `rl status`, `rl stats`, `rl vocab` | global config, workspace, roll, vocab | no | no |
| Integrity | `rl doctor`, `rl doctor --fix` | global config, workspace, stock, roll, vocab | no | yes |
| Normalization | `rl normalize --tags` | workspace, roll, vocab | roll, vocab | yes |

`rl load --manual` creates a roll from the film dictionary without changing stock.
For `rl features add` and `rl tags add` you can enter several values separated by commas. Autocomplete works per value, duplicates aren't written, `_` is allowed inside a value.
`rl config lang` applies immediately in the current process because user-facing messages resolve the language at render time.
`rl doctor` checks the global config, workspace config, stock, roll metadata, and vocabularies. Its diagnostics stay in English; only the user-facing UI is localized.
Package version comes from git tags at build time. In a source checkout, `rl --version` falls back to the latest git tag if package metadata is not installed.
`rl update` prints package manager update guidance. It does not reinstall the package.

## CI

GitHub Actions runs:
- `ruff check .`
- `python -m unittest discover -s tests`

The workflow triggers on pull requests and pushes to `main`.
