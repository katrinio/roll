from __future__ import annotations

from datetime import date
from pathlib import Path

import typer
from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyCompleter, WordCompleter

from roll.app.archive.normalization import apply_keyword_vocab_fixes
from roll.app.workspace.roll_store import (
    RollMetadata,
    load_roll_metadata,
    save_roll_metadata,
    update_roll_features,
    update_roll_keywords,
    update_roll_status,
)
from roll.app.workspace.stock_store import (
    StockItem,
    add_to_stock,
    load_stock,
    remove_from_stock,
    save_stock,
)
from roll.app.workspace.statuses import VALID_STATUSES
from roll.app.workspace.workspace import workspace_for
from roll.helpers.autocomplete import autocomplete_many_prompt, autocomplete_prompt
from roll.helpers.guards import require_archive, require_config
from roll.helpers.output import echo_lines
from roll.messages import Msg
from roll.app.flows.stock_edit import _choose_roll, _rolls


def add() -> None:
    archive = require_archive(require_config())
    workspace = workspace_for(archive)

    film = autocomplete_prompt(str(Msg.PROMPT_FILM), workspace.dictionary("films"))
    quantity = typer.prompt(str(Msg.PROMPT_QUANTITY), type=int)
    if quantity <= 0:
        typer.echo(str(Msg.INVALID_QUANTITY))
        raise typer.Exit(code=1)

    try:
        items = load_stock(workspace.stock_file)
        save_stock(workspace.stock_file, add_to_stock(items, film, quantity))
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1)


def load(manual: bool) -> None:
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
            typer.echo(str(Msg.STOCK_EMPTY_MANUAL))
            raise typer.Exit(code=1)

    selected = (
        _choose_stock_item(stock) if not manual else _choose_manual_film(workspace)
    )
    camera = autocomplete_prompt(
        str(Msg.PROMPT_CAMERA), workspace.dictionary("cameras")
    )
    loaded_at = _prompt_loaded_at()
    roll_folder = _create_roll_folder(archive, loaded_at)
    roll_file = roll_folder / "roll.toml"

    if roll_file.exists():
        typer.echo(f"{Msg.ROLL_EXISTS} {roll_file}")
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
        features = autocomplete_many_prompt(
            str(Msg.VOCAB_FEATURES), workspace.dictionary("features")
        )
        if features:
            update_roll_features(roll_file, features)

        tags = autocomplete_many_prompt(
            str(Msg.VOCAB_KEYWORDS), workspace.dictionary("keywords")
        )
        if tags:
            update_roll_keywords(roll_file, tags)
            apply_keyword_vocab_fixes(archive, tags)
    except Exception:
        _cleanup_failed_load(roll_folder, roll_file)
        raise

    typer.echo(f"{Msg.LOAD_SUCCESS} {selected.film}")


def process(status: str, label: str) -> None:
    archive = require_archive(require_config())
    loaded_rolls = [
        path
        for path in _rolls(archive)
        if load_roll_metadata(path / "roll.toml").status == "loaded"
    ]
    if not loaded_rolls:
        typer.echo(str(Msg.NO_LOADED_ROLLS))
        raise typer.Exit(code=1)

    selected = _choose_roll(loaded_rolls)
    try:
        metadata = update_roll_status(selected / "roll.toml", status)
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1)

    typer.echo(f"{label}: {metadata.film}")


def list_stock() -> None:
    archive = require_archive(require_config())
    workspace = workspace_for(archive)

    try:
        items = load_stock(workspace.stock_file)
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1)

    if not items:
        typer.echo(str(Msg.STOCK_EMPTY))
        return

    echo_lines([Msg.STOCK_HEADER])
    for item in items:
        typer.echo(f"{item.film:<20} ×{item.quantity}")


def _prompt_loaded_at() -> str:
    value = typer.prompt(str(Msg.PROMPT_LOAD_DATE))
    normalized = value.strip().split("T", 1)[0].split(" ", 1)[0]
    try:
        return date.fromisoformat(normalized).isoformat()
    except ValueError as exc:
        typer.echo(str(Msg.INVALID_DATE))
        raise typer.Exit(code=1) from exc


def _create_roll_folder(archive: Path, loaded_at: str) -> Path:
    loaded_date = date.fromisoformat(loaded_at)
    return archive / loaded_date.strftime("%Y") / loaded_date.strftime("%m-%d")


def _choose_stock_item(items: list[StockItem]) -> StockItem:
    labels = [f"{item.film} ×{item.quantity}" for item in items]
    completer = FuzzyCompleter(
        WordCompleter(labels, ignore_case=True, sentence=True, match_middle=True)
    )

    while True:
        value = prompt(
            str(Msg.PROMPT_MANUAL_FILM),
            completer=completer,
            complete_while_typing=True,
        ).strip()
        if not value:
            continue

        selected = _resolve_stock_choice(items, value)
        if selected is not None:
            return selected

        typer.echo(str(Msg.CHOOSE_STOCK))


def _choose_manual_film(workspace) -> StockItem:
    film = autocomplete_prompt(str(Msg.PROMPT_FILM), workspace.dictionary("films"))
    return StockItem(film=film, quantity=1)


def _resolve_stock_choice(items: list[StockItem], candidate: str) -> StockItem | None:
    normalized = _normalize_choice(candidate)

    exact_film_matches = [
        item for item in items if item.film.casefold() == candidate.casefold()
    ]
    if len(exact_film_matches) == 1:
        return exact_film_matches[0]

    exact_label_matches = [
        item
        for item in items
        if f"{item.film} ×{item.quantity}".casefold() == candidate.casefold()
    ]
    if len(exact_label_matches) == 1:
        return exact_label_matches[0]

    fuzzy_matches = [
        item for item in items if normalized in _normalize_choice(item.film)
    ]
    if len(fuzzy_matches) == 1:
        return fuzzy_matches[0]

    return None


def _normalize_choice(value: str) -> str:
    return "".join(ch for ch in value.casefold() if ch.isalnum())


def _cleanup_failed_load(roll_folder: Path, roll_file: Path) -> None:
    if roll_file.exists():
        roll_file.unlink()
    if roll_folder.exists():
        try:
            roll_folder.rmdir()
        except OSError:
            pass
