from __future__ import annotations

from pathlib import Path
import textwrap

import typer
from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyCompleter, WordCompleter

from roll.app.archive.batch import batch_rolls
from roll.app.archive.normalization import apply_keyword_vocab_fixes
from roll.app.archive.selection import roll_choice_label, split_csv
from roll.app.workspace.roll_store import (
    RollMetadata,
    load_roll_metadata,
    save_roll_metadata,
    update_roll_features,
    update_roll_keywords,
)
from roll.app.workspace.workspace import workspace_for
from roll.app.workspace.statuses import VALID_STATUSES
from roll.filesystem import find_roll_folders
from roll.helpers.autocomplete import autocomplete_many_prompt
from roll.helpers.output import echo_lines
from roll.helpers.guards import require_archive, require_config
from roll.messages import Msg


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


def edit_list_field(
    prompt_title: str, dictionary_name: str, success_label: str
) -> None:
    archive = require_archive(require_config())
    rolls = _rolls(archive)
    if not rolls:
        typer.echo(str(Msg.NO_ROLLS))
        raise typer.Exit(code=1)

    selected = _choose_roll_folder(rolls)
    workspace = workspace_for(archive)
    values = autocomplete_many_prompt(
        prompt_title, workspace.dictionary(dictionary_name)
    )
    try:
        metadata = (
            update_roll_keywords(selected / "roll.toml", values)
            if dictionary_name == "keywords"
            else update_roll_features(selected / "roll.toml", values)
        )
        if dictionary_name == "keywords":
            apply_keyword_vocab_fixes(archive, metadata.keywords)
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1)

    typer.echo(f"{success_label}: {metadata.film}")


def edit_batch(
    year: str | None,
    film: str | None,
    camera: str | None,
    status: str | None,
    set_status: str | None,
    set_camera: str | None,
    add_feature: str | None,
    add_tag: str | None,
) -> None:
    config = require_config()
    filters = {"year": year, "film": film, "camera": camera, "status": status}
    changes = {
        "set_status": set_status,
        "set_camera": set_camera,
        "add_feature": add_feature,
        "add_tag": add_tag,
    }
    if not any(filters.values()) or not any(changes.values()):
        typer.echo(str(Msg.BATCH_NEEDS_FILTERS))
        raise typer.Exit(code=1)

    batch_rolls(
        config.archives,
        year=year,
        films=split_csv(film),
        cameras=split_csv(camera),
        statuses=split_csv(status),
        status=set_status,
        set_camera=set_camera,
        add_features=split_csv(add_feature),
        add_tags=split_csv(add_tag),
    )


def _choose_roll(rolls: list[Path]) -> Path:
    labels = [_format_roll_label(path) for path in rolls]
    selected_label = _prompt_choice(str(Msg.ROLL_EDIT_SELECT), labels)
    label_to_roll = dict(zip(labels, rolls, strict=True))
    return label_to_roll[selected_label]


def _choose_roll_folder(rolls: list[Path]) -> Path:
    labels = [roll_choice_label(path, _roll_status(path)) for path in rolls]
    selected_label = _prompt_choice(str(Msg.ROLL_EDIT_SELECT), labels)
    label_to_roll = dict(zip(labels, rolls, strict=True))
    return label_to_roll[selected_label]


def _rolls(archive: Path) -> list[Path]:
    rolls: list[Path] = []
    for folder in find_roll_folders(archive):
        try:
            load_roll_metadata(folder / "roll.toml")
        except ValueError:
            continue
        rolls.append(folder)
    return rolls


def _roll_status(path: Path) -> str:
    try:
        return load_roll_metadata(path / "roll.toml").status
    except ValueError:
        return "unknown"


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
        for existing in choices:
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
