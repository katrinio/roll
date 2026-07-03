# Contributing

`roll` — небольшой личный проект, но PR и issues приветствуются.

## Перед началом

- Архитектура и команды — [docs/model.md](docs/model.md)
- Термины — [docs/glossary.md](docs/glossary.md)
- Границы MVP — [docs/mvp.md](docs/mvp.md): если фича не помогает быстрее найти пленку по памяти, обсудим ее отдельно перед PR

## Setup

Полная инструкция — [docs/development.md](docs/development.md). Коротко:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pre-commit install
```

## Перед PR

```bash
ruff check .
python -m unittest discover -s tests
```

Оба шага гоняются в CI на каждый PR — красный CI не смержится.

## Стиль

- новую логику — в соответствующую зону (`app/workspace/`, `app/flows/`, `app/archive/`, `app/diagnostics/`), не в `cli.py`;
- user-facing строки — в `messages/`, не хардкодом в коде;
- деструктивные операции над архивом (переименования, запись) — сначала план, потом подтверждение;
- тесты обязательны для новой логики хранения/нормализации.

## PR

- маленький и по одной теме;
- если меняется поведение CLI или формат `roll.toml` — обнови `docs/model.md`/`docs/glossary.md` в том же PR.
