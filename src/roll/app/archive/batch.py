from dataclasses import replace
from pathlib import Path

import typer

from roll.app.workspace.roll_store import (
    RollMetadata,
    load_roll_metadata,
    save_roll_metadata,
)
from roll.app.archive.search import find_rolls
from roll.helpers.output import echo_list
from roll.messages import Msg


def process_archives(archives: list[Path]) -> int:
    return batch_rolls(archives, statuses=["loaded"], status="processed")


def batch_rolls(
    archives: list[Path],
    *,
    year: str | None = None,
    films: list[str] | None = None,
    cameras: list[str] | None = None,
    statuses: list[str] | None = None,
    status: str | None = None,
    set_camera: str | None = None,
    add_features: list[str] | None = None,
    add_tags: list[str] | None = None,
) -> int:
    rolls = _select_rolls(
        archives,
        year=year,
        films=films,
        cameras=cameras,
        statuses=statuses,
    )

    if not rolls:
        typer.echo(str(Msg.NO_RESULTS))
        return 0

    preview = [str(roll.folder) for roll in rolls]
    typer.echo(f"{Msg.BATCH_WILL_PROCESS} {len(preview)}")
    echo_list(preview)

    if not typer.confirm(Msg.BATCH_CONFIRM, default=False):
        return 0

    changed = 0
    for roll in rolls:
        updated = _apply_changes(
            roll,
            status=status,
            set_camera=set_camera,
            add_features=add_features,
            add_tags=add_tags,
        )
        save_roll_metadata(roll.folder / "roll.toml", updated)
        changed += 1

    typer.echo(f"{Msg.BATCH_PROCESSED} {changed}")
    return changed


def _select_rolls(
    archives: list[Path],
    *,
    year: str | None,
    films: list[str] | None,
    cameras: list[str] | None,
    statuses: list[str] | None,
) -> list:
    selected = []
    film_set = _normalize_set(films)
    camera_set = _normalize_set(cameras)
    status_set = _normalize_set(statuses)

    for archive in archives:
        for roll in find_rolls(archive):
            if year is not None and roll.loaded_at[:4] != year:
                continue
            if film_set and roll.film.casefold() not in film_set:
                continue
            if camera_set and roll.camera.casefold() not in camera_set:
                continue
            if status_set and roll.status.casefold() not in status_set:
                continue
            selected.append(roll)

    return selected


def _apply_changes(
    roll,
    *,
    status: str | None,
    set_camera: str | None,
    add_features: list[str] | None,
    add_tags: list[str] | None,
) -> RollMetadata:
    metadata = load_roll_metadata(roll.folder / "roll.toml")
    updated = metadata
    if status is not None:
        updated = replace(updated, status=status)
    if set_camera is not None:
        updated = replace(updated, camera=set_camera)
    if add_features:
        updated = replace(
            updated,
            features=_merge_unique(updated.features, add_features),
        )
    if add_tags:
        updated = replace(
            updated,
            keywords=_merge_unique(
                updated.keywords, [item.upper() for item in add_tags]
            ),
        )
    return updated


def _normalize_set(values: list[str] | None) -> set[str]:
    return {value.casefold() for value in values or [] if value}


def _merge_unique(existing: list[str], new_values: list[str]) -> list[str]:
    merged = list(existing)
    for value in new_values:
        if value not in merged:
            merged.append(value)
    return merged
