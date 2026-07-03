import tomllib
from dataclasses import dataclass
from pathlib import Path

from roll.archive import find_roll_folders, get_index_file


@dataclass(frozen=True)
class RollIndex:
    folder: Path
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


def search_rolls(archive: Path, query: str) -> list[RollIndex]:
    normalized_query = query.lower()
    results: list[RollIndex] = []

    for roll in find_rolls(archive):
        searchable_text = " ".join(
            [
                roll.film,
                roll.camera,
                roll.loaded_at,
                *roll.features,
                *roll.keywords,
            ]
        ).lower()

        if normalized_query in searchable_text:
            results.append(roll)

    return results
