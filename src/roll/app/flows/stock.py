from __future__ import annotations

from datetime import date
from pathlib import Path
import textwrap

import typer
from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyCompleter, WordCompleter

from roll.filesystem import find_roll_folders
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
from roll.app.archive.normalization import apply_keyword_vocab_fixes
from roll.helpers.autocomplete import autocomplete_many_prompt, autocomplete_prompt
from roll.helpers.guards import require_archive, require_config
from roll.helpers.output import echo_lines
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
    rolls = _rolls(archive)
    if not rolls:
        typer.echo(str(Msg.NO_LOADED_ROLLS))
        raise typer.Exit(code=1)

    roll = _choose_roll(rolls)
    metadata = load_roll_metadata(roll / "roll.toml")
    updated = _prompt_roll_metadata(archive, roll / "roll.toml", metadata)
    save_roll_metadata(roll / "roll.toml", updated)
    typer.echo(f"{Msg.ROLL_EDIT_UPDATED} {updated.loaded_at}")


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


def _choose_roll(rolls: list[Path]) -> Path:
    labels = [_format_roll_label(path) for path in rolls]
    selected_label = _prompt_choice(str(Msg.ROLL_EDIT_SELECT), labels)
    for path in rolls:
        if _format_roll_label(path) == selected_label:
            return path
    raise ValueError(Msg.NO_CHOICE)


def _rolls(archive: Path) -> list[Path]:
    rolls: list[Path] = []
    for folder in find_roll_folders(archive):
        try:
            load_roll_metadata(folder / "roll.toml")
        except ValueError:
            continue
        rolls.append(folder)
    return rolls


def _finish_roll(status: str, label: str) -> None:
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
    selected = _prompt_choice_panel(str(label), values, current)
    return selected if selected is not None else current


def _prompt_roll_metadata(
    archive: Path, roll_file: Path, metadata: RollMetadata
) -> RollMetadata:
    workspace = workspace_for(archive)
    film = _prompt_optional_autocomplete(
        Msg.ROLL_EDIT_FILM, workspace.dictionary("films"), metadata.film
    )
    camera = _prompt_optional_autocomplete(
        Msg.ROLL_EDIT_CAMERA, workspace.dictionary("cameras"), metadata.camera
    )
    status = _prompt_enum(Msg.ROLL_EDIT_STATUS, list(VALID_STATUSES), metadata.status)
    features = _prompt_optional_many(
        Msg.ROLL_EDIT_FEATURES, workspace.dictionary("features"), metadata.features
    )
    keywords = _prompt_optional_many(
        Msg.ROLL_EDIT_KEYWORDS, workspace.dictionary("keywords"), metadata.keywords
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
    return RollMetadata(
        status=status,
        film=film,
        camera=camera,
        loaded_at=metadata.loaded_at,
        features=features,
        keywords=[value.upper() for value in keywords],
        original_source=original_source,
        digital_copy=digital_copy,
        original_status=original_status,
    )


def _prompt_optional_autocomplete(label: Msg, dictionary, current: str) -> str:
    value = prompt(f"{label} [{current}]: ", complete_while_typing=True).strip()
    if not value:
        return current

    choices = dictionary.read()
    for existing in choices:
        if existing.casefold() == value.casefold():
            return existing

    return dictionary.add(value)


def _prompt_optional_many(label: Msg, dictionary, current: list[str]) -> list[str]:
    choices = dictionary.read()
    value = prompt(
        f"{label} [{', '.join(current)}]: ",
        completer=FuzzyCompleter(
            WordCompleter(choices, ignore_case=True, sentence=True, match_middle=True)
        ),
        complete_while_typing=True,
    ).strip()
    if not value:
        return current

    selected: list[str] = []
    for token in [item.strip() for item in value.split(",") if item.strip()]:
        for existing in dictionary.read():
            if existing.casefold() == token.casefold():
                token = existing
                break
        else:
            token = dictionary.add(token)
        if token not in selected:
            selected.append(token)
    merged = list(current)
    for token in selected:
        if token not in merged:
            merged.append(token)
    return merged


def _prompt_choice(title: str, choices: list[str]) -> str:
    selected = _prompt_choice_panel(title, choices, choices[0] if choices else "")
    if selected is None:
        raise ValueError(Msg.NO_CHOICE)
    return selected


def _prompt_choice_panel(
    title: str, choices: list[str], current: str | None = None
) -> str | None:
    content_width = max(
        len(title),
        len(f"Current: {current}") if current is not None else 0,
        *(len(f"{index + 1}. {choice}") for index, choice in enumerate(choices)),
        24,
    )
    width = min(content_width + 4, 88)
    border = "┌" + "─" * (width - 2) + "┐"
    footer = "└" + "─" * (width - 2) + "┘"
    prompt_lines = [border, f"│ {title.ljust(width - 4)} │"]
    if current is not None:
        prompt_lines.append(
            f"│ {textwrap.shorten(f'Current: {current}', width=width - 4, placeholder='…').ljust(width - 4)} │"
        )
    prompt_lines.append("├" + "─" * (width - 2) + "┤")
    prompt_lines.extend(
        f"│ {textwrap.shorten(f'{index + 1}. {choice}', width=width - 4, placeholder='…').ljust(width - 4)} │"
        for index, choice in enumerate(choices)
    )
    prompt_lines.append(footer)
    echo_lines(prompt_lines)

    while True:
        value = prompt(f"{Msg.ROLL_EDIT_SELECT_HINT}: ").strip()
        if not value:
            return current
        if value.isdigit():
            index = int(value) - 1
            if 0 <= index < len(choices):
                return choices[index]
        if value in choices:
            return value


def _cleanup_failed_load(roll_folder: Path, roll_file: Path) -> None:
    if roll_file.exists():
        roll_file.unlink()
    if roll_folder.exists():
        try:
            roll_folder.rmdir()
        except OSError:
            pass
