from __future__ import annotations

from datetime import date
from pathlib import Path

import typer
from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyCompleter, WordCompleter

from roll.archive import find_roll_folders
from roll.app.roll_store import (
    RollMetadata,
    load_roll_metadata,
    save_roll_metadata,
    update_roll_keywords,
    update_roll_status,
)
from roll.app.stock_store import StockItem, add_to_stock, load_stock, remove_from_stock, save_stock
from roll.app.statuses import VALID_STATUSES
from roll.app.workspace import workspace_for
from roll.helpers.autocomplete import autocomplete_many_prompt, autocomplete_prompt, choice_prompt
from roll.helpers.guards import require_archive, require_config
from roll.helpers.output import echo_lines

app = typer.Typer(help="Запас пленки.")


@app.command("add")
def add() -> None:
    archive = require_archive(require_config())
    workspace = workspace_for(archive)

    film = autocomplete_prompt("Пленка", workspace.dictionary("films"))
    quantity = typer.prompt("Количество:", type=int)
    if quantity <= 0:
        typer.echo("Количество должно быть положительным.")
        raise typer.Exit(code=1)

    try:
        items = load_stock(workspace.stock_file)
        save_stock(workspace.stock_file, add_to_stock(items, film, quantity))
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1)


@app.command("load")
def load(manual: bool = typer.Option(False, "--manual", help="Вводить пленку вручную через справочник.")) -> None:
    archive = require_archive(require_config())
    workspace = workspace_for(archive)

    stock: list[StockItem] = []
    if not manual:
        try:
            stock = load_stock(workspace.stock_file)
        except ValueError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1)

        if not stock:
            typer.echo("Запас пуст. Используй --manual для ручного ввода.")
            raise typer.Exit(code=1)

    selected = _choose_stock_item(stock) if not manual else _choose_manual_film(workspace)
    camera = autocomplete_prompt("Камера", workspace.dictionary("cameras"))
    loaded_at = _prompt_loaded_at()
    roll_folder = _create_roll_folder(archive, loaded_at)
    roll_file = roll_folder / "roll.toml"

    if roll_file.exists():
        typer.echo(f"Roll уже существует: {roll_file}")
        raise typer.Exit(code=1)

    try:
        roll_folder.mkdir(parents=True, exist_ok=True)
        save_roll_metadata(
            roll_file,
            RollMetadata(
                status=VALID_STATUSES[0],
                film=selected.film,
                camera=camera,
                loaded_at=loaded_at,
                features=[],
                keywords=[],
            ),
        )
        if not manual:
            save_stock(workspace.stock_file, remove_from_stock(stock, selected.film, 1))
        tags = autocomplete_many_prompt("Теги", workspace.dictionary("keywords"))
        if tags:
            update_roll_keywords(roll_file, tags)
    except Exception:
        _cleanup_failed_load(roll_folder, roll_file)
        raise

    typer.echo(f"Заряжено: {selected.film}")


@app.command("process")
def process() -> None:
    _finish_roll("processed", "Обработана")


@app.command("failed")
def failed() -> None:
    _finish_roll("failed", "Помечена как испорченная")


@app.command("list")
def list_stock() -> None:
    archive = require_archive(require_config())
    workspace = workspace_for(archive)

    try:
        items = load_stock(workspace.stock_file)
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1)

    if not items:
        typer.echo("Запас пуст.")
        return

    echo_lines(["Запас пленки"])
    for item in items:
        typer.echo(f"{item.film:<20} ×{item.quantity}")


def _prompt_loaded_at() -> str:
    value = typer.prompt("Дата загрузки")
    normalized = value.strip().split("T", 1)[0].split(" ", 1)[0]
    try:
        return date.fromisoformat(normalized).isoformat()
    except ValueError as exc:
        typer.echo("Неверная дата.")
        raise typer.Exit(code=1) from exc


def _create_roll_folder(archive: Path, loaded_at: str) -> Path:
    loaded_date = date.fromisoformat(loaded_at)
    return archive / loaded_date.strftime("%Y") / loaded_date.strftime("%m-%d")


def _choose_stock_item(items: list[StockItem]) -> StockItem:
    labels = [f"{item.film} ×{item.quantity}" for item in items]
    completer = FuzzyCompleter(WordCompleter(labels, ignore_case=True, sentence=True, match_middle=True))

    while True:
        value = prompt("Пленка: ", completer=completer, complete_while_typing=True).strip()
        if not value:
            continue

        selected = _resolve_stock_choice(items, value)
        if selected is not None:
            return selected

        typer.echo("Выбери пленку из запаса.")


def _choose_manual_film(workspace) -> StockItem:
    film = autocomplete_prompt("Пленка", workspace.dictionary("films"))
    return StockItem(film=film, quantity=1)


def _resolve_stock_choice(items: list[StockItem], candidate: str) -> StockItem | None:
    normalized = _normalize_choice(candidate)

    exact_film_matches = [item for item in items if item.film.casefold() == candidate.casefold()]
    if len(exact_film_matches) == 1:
        return exact_film_matches[0]

    exact_label_matches = [item for item in items if f"{item.film} ×{item.quantity}".casefold() == candidate.casefold()]
    if len(exact_label_matches) == 1:
        return exact_label_matches[0]

    fuzzy_matches = [item for item in items if normalized in _normalize_choice(item.film)]
    if len(fuzzy_matches) == 1:
        return fuzzy_matches[0]

    return None


def _normalize_choice(value: str) -> str:
    return "".join(ch for ch in value.casefold() if ch.isalnum())


def _loaded_rolls(archive: Path) -> list[Path]:
    rolls: list[Path] = []
    for folder in find_roll_folders(archive):
        try:
            metadata = load_roll_metadata(folder / "roll.toml")
        except ValueError:
            continue
        if metadata.status == "loaded":
            rolls.append(folder)
    return rolls


def _finish_roll(status: str, label: str) -> None:
    archive = require_archive(require_config())
    loaded_rolls = _loaded_rolls(archive)
    if not loaded_rolls:
        typer.echo("Нет загруженных пленок.")
        raise typer.Exit(code=1)

    selected = _choose_roll(loaded_rolls)
    try:
        metadata = update_roll_status(selected / "roll.toml", status)
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1)

    typer.echo(f"{label}: {metadata.film}")


def _choose_roll(rolls: list[Path]) -> Path:
    labels = [str(path.relative_to(path.parents[1])) for path in rolls]
    selected_label = choice_prompt("Roll", labels)
    for path in rolls:
        if selected_label == str(path.relative_to(path.parents[1])):
            return path
    raise ValueError("Не удалось выбрать roll.")


def _cleanup_failed_load(roll_folder: Path, roll_file: Path) -> None:
    if roll_file.exists():
        roll_file.unlink()
    if roll_folder.exists():
        try:
            roll_folder.rmdir()
        except OSError:
            pass
