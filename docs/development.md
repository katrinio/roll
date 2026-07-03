# Development

Короткая рабочая инструкция для локальной разработки.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

Если `.venv` уже есть, обычно достаточно:

```bash
pip install -e '.[dev]'
```

## Pre-commit

```bash
pre-commit install
pre-commit run --all-files
```

`pre-commit` использует тот же `ruff`, что и CI.

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
```

`rl load` работает от `stock.toml`, а `rl load --manual` позволяет создать roll по словарю пленок, не уменьшая stock.

Для `rl features add` и `rl tags add` можно вводить несколько значений через запятую. Автокомплит работает по каждому значению, дубликаты не записываются. Внутри значения допустим `_`.

## CI

GitHub Actions запускает:
- `ruff check .`
- `python -m unittest discover -s tests`

Workflow срабатывает на pull request и push в `main`.
