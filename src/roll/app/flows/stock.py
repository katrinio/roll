from __future__ import annotations

from datetime import date
from pathlib import Path

import typer
from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyCompleter, WordCompleter
from prompt_toolkit.shortcuts import radiolist_dialog

from roll.filesystem import find_roll_folders
from roll.app.workspace.roll_store import (
    RollMetadata,
    load_roll_metadata,
    save_roll_metadata,
    update_roll_origin,
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
from roll.app.archive.normalization import apply_keyword_vocab_fixes
from roll.helpers.autocomplete import autocomplete_many_prompt, autocomplete_prompt
from roll.helpers.guards import require_archive, require_config
from roll.helpers.output import echo_lines, echo_section
from roll.messages import Msg

app = typer.Typer(help=Msg.STOCK_HEADER)


@app.command("add")
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


@app.command("load")
def load(
    manual: bool = typer.Option(
        False, "--manual", help="Enter film manually from dictionary."
    ),
) -> None:
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


@app.command("process")
def process() -> None:
    _finish_roll("processed", "Processed")


@app.command("failed")
def failed() -> None:
    _finish_roll("failed", "Marked as failed")


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
        typer.echo(str(Msg.STOCK_EMPTY))
        return

    echo_lines([Msg.STOCK_HEADER])
    for item in items:
        typer.echo(f"{item.film:<20} ×{item.quantity}")


@app.command("edit")
def edit() -> None:
    archive = require_archive(require_config())
    loaded_rolls = _loaded_rolls(archive)
    if not loaded_rolls:
        typer.echo(str(Msg.NO_LOADED_ROLLS))
        raise typer.Exit(code=1)

    echo_section(
        str(Msg.ROLL_EDIT_AVAILABLE),
        [f"- {_format_roll_label(path)}" for path in loaded_rolls],
    )
    roll = _choose_loaded_roll(loaded_rolls)
    metadata = load_roll_metadata(roll / "roll.toml")
    echo_lines(
        [
            f"{Msg.ROLL_EDIT_ORIGINAL_SOURCE}: {metadata.original_source}",
            f"{Msg.ROLL_EDIT_DIGITAL_COPY}: {metadata.digital_copy}",
            f"{Msg.ROLL_EDIT_ORIGINAL_STATUS}: {metadata.original_status}",
        ]
    )

    original_source = _prompt_enum(
        Msg.ROLL_EDIT_ORIGINAL_SOURCE,
        ["negative", "slide", "print", "digital", "unknown"],
        metadata.original_source,
    )
    digital_copy = _prompt_enum(
        Msg.ROLL_EDIT_DIGITAL_COPY,
        ["scan", "photo", "none", "unknown"],
        metadata.digital_copy,
    )
    original_status = _prompt_enum(
        Msg.ROLL_EDIT_ORIGINAL_STATUS,
        ["present", "lost", "unknown"],
        metadata.original_status,
    )

    update_roll_origin(
        roll / "roll.toml", original_source, digital_copy, original_status
    )
    typer.echo(f"{Msg.ROLL_EDIT_UPDATED} {metadata.loaded_at}")


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


def _choose_loaded_roll(rolls: list[Path]) -> Path:
    labels = [_format_roll_label(path) for path in rolls]
    selected_label = _prompt_choice(str(Msg.ROLL_EDIT_SELECT), labels)
    for path in rolls:
        if _format_roll_label(path) == selected_label:
            return path
    raise ValueError(Msg.NO_CHOICE)


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
        typer.echo(str(Msg.NO_LOADED_ROLLS))
        raise typer.Exit(code=1)

    selected = _choose_roll(loaded_rolls)
    try:
        metadata = update_roll_status(selected / "roll.toml", status)
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1)

    typer.echo(f"{label}: {metadata.film}")


def _choose_roll(rolls: list[Path]) -> Path:
    labels = [_format_roll_label(path) for path in rolls]
    selected_label = _prompt_choice(str(Msg.ROLL_EDIT_SELECT), labels)
    for path in rolls:
        if selected_label == _format_roll_label(path):
            return path
    raise ValueError(Msg.NO_CHOICE)


def _format_roll_label(path: Path) -> str:
    metadata = load_roll_metadata(path / "roll.toml")
    return str(Msg.ROLL_EDIT_ROLL_LABEL).format(
        path=str(path.relative_to(path.parents[1])),
        film=metadata.film,
        camera=metadata.camera,
        status=metadata.status,
    )


def _prompt_enum(label: Msg, values: list[str], current: str) -> str:
    dialog = radiolist_dialog(
        title=str(Msg.ROLL_EDIT_HEADER),
        text=f"{label}:",
        values=[(value, value) for value in values],
        default=current if current in values else values[-1],
    )
    result = dialog.run()
    return result if result is not None else current


def _prompt_choice(title: str, choices: list[str]) -> str:
    dialog = radiolist_dialog(
        title=title,
        text="",
        values=[(value, value) for value in choices],
        default=choices[0] if choices else None,
    )
    result = dialog.run()
    if result is None:
        raise ValueError(Msg.NO_CHOICE)
    return result


def _cleanup_failed_load(roll_folder: Path, roll_file: Path) -> None:
    if roll_file.exists():
        roll_file.unlink()
    if roll_folder.exists():
        try:
            roll_folder.rmdir()
        except OSError:
            pass
