# Contributing

`roll` is a small personal project, but PRs and issues are welcome.

## Before you start

- Architecture and commands — [docs/model.md](docs/model.md)
- Terms — [docs/glossary.md](docs/glossary.md)
- MVP scope — [docs/mvp.md](docs/mvp.md): if a feature doesn't help find a roll from memory faster, let's discuss it separately before a PR

## Setup

Full instructions — [docs/development.md](docs/development.md). Short version:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pre-commit install
```

## Before a PR

```bash
ruff check .
python -m unittest discover -s tests
```

Both run in CI on every PR — a red CI won't get merged.

## Style

- put new logic in the right area (`app/workspace/`, `app/flows/`, `app/archive/`, `app/diagnostics/`), not in `cli.py`;
- user-facing strings go in `messages/`, not hardcoded in the code;
- destructive operations on the archive (renames, writes) always build a plan first, then ask for confirmation;
- tests are required for new storage/normalization logic.

## PR

- keep it small and focused on one thing;
- if it changes CLI behavior or the `roll.toml` format — update `docs/model.md`/`docs/glossary.md` in the same PR.
