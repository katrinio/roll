import tomllib
from dataclasses import dataclass
from pathlib import Path

from roll.app.archive.selection import normalize_text, select_rolls
from roll.filesystem import find_roll_folders, get_index_file


@dataclass(frozen=True)
class RollIndex:
    folder: Path
    status: str
    film: str
    camera: str
    loaded_at: str
    features: list[str]
    keywords: list[str]


def load_roll_index(folder: Path) -> RollIndex | None:
    index_file = get_index_file(folder)

    if not index_file.exists():
        return None

    data = tomllib.loads(index_file.read_text(encoding="utf-8"))

    return RollIndex(
        folder=folder,
        status=data.get("status", ""),
        film=data.get("film", ""),
        camera=data.get("camera", ""),
        loaded_at=data.get("loaded_at", ""),
        features=data.get("features", []),
        keywords=data.get("keywords", []),
    )


def find_rolls(archive: Path) -> list[RollIndex]:
    rolls: list[RollIndex] = []

    for folder in find_roll_folders(archive):
        roll = load_roll_index(folder)
        if roll is not None:
            rolls.append(roll)

    return rolls


def search_rolls(archive: Path, query: str | None) -> list[RollIndex]:
    if not query:
        return []

    return _filter_by_query(find_rolls(archive), query)


def search_rolls_by_filters(
    archives: list[Path],
    *,
    year: str | None = None,
    films: list[str] | None = None,
    cameras: list[str] | None = None,
    statuses: list[str] | None = None,
    query: str | None = None,
) -> list[RollIndex]:
    rolls = select_rolls(
        archives, year=year, films=films, cameras=cameras, statuses=statuses
    )
    return rolls if not query else _filter_by_query(rolls, query)


def _filter_by_query(rolls: list[RollIndex], query: str) -> list[RollIndex]:
    normalized_query = normalize_text(query)
    return [roll for roll in rolls if normalized_query in _searchable_text(roll)]


def _searchable_text(roll: RollIndex) -> str:
    return normalize_text(
        " ".join(
            [
                roll.film,
                roll.camera,
                roll.loaded_at,
                *roll.features,
                *roll.keywords,
            ]
        )
    )
