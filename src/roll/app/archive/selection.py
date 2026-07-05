from __future__ import annotations

from pathlib import Path

from roll.app.archive.search import RollIndex


def split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def normalize_set(values: list[str] | None) -> set[str]:
    return {normalize_text(value) for value in values or [] if value}


def normalize_text(value: str) -> str:
    return value.casefold().strip()


def matches_year(loaded_at: str, year: str | None) -> bool:
    return year is None or loaded_at[:4] == year


def matches_any(value: str, candidates: set[str]) -> bool:
    return not candidates or normalize_text(value) in candidates


def select_rolls(
    archives: list[Path],
    *,
    year: str | None = None,
    films: list[str] | None = None,
    cameras: list[str] | None = None,
    statuses: list[str] | None = None,
) -> list[RollIndex]:
    from roll.app.archive.search import find_rolls

    selected: list[RollIndex] = []
    film_set = normalize_set(films)
    camera_set = normalize_set(cameras)
    status_set = normalize_set(statuses)

    for archive in archives:
        for roll in find_rolls(archive):
            if not matches_year(roll.loaded_at, year):
                continue
            if not matches_any(roll.film, film_set):
                continue
            if not matches_any(roll.camera, camera_set):
                continue
            if not matches_any(roll.status, status_set):
                continue
            selected.append(roll)

    return selected


def roll_choice_label(path: Path, status: str) -> str:
    return f"{str(path.relative_to(path.parents[1]))} ({status})"
