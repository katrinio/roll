from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from roll.app.search import find_rolls


@dataclass(frozen=True)
class StatsReport:
    year: str | None
    roll_count: int
    film_count: int
    tag_count: int
    status_counts: Counter[str]
    year_counts: Counter[str]
    film_counts: Counter[str]
    tag_counts: Counter[str]
    camera_counts: Counter[str]


def build_stats_report(archive: Path, year: str | None = None) -> StatsReport:
    rolls = find_rolls(archive)
    if year:
        rolls = [roll for roll in rolls if roll.loaded_at.startswith(f"{year}-")]

    film_counts = Counter(roll.film for roll in rolls)
    tag_counts = Counter(tag for roll in rolls for tag in roll.keywords)
    camera_counts = Counter(roll.camera for roll in rolls)
    year_counts = Counter(roll.loaded_at[:4] for roll in rolls if roll.loaded_at)
    status_counts = _count_statuses(rolls)

    return StatsReport(
        year=year,
        roll_count=len(rolls),
        film_count=len(film_counts),
        tag_count=len(tag_counts),
        status_counts=status_counts,
        year_counts=year_counts,
        film_counts=film_counts,
        tag_counts=tag_counts,
        camera_counts=camera_counts,
    )


def _count_statuses(rolls) -> Counter[str]:
    counts = Counter({"loaded": 0, "processed": 0, "failed": 0})
    for roll in rolls:
        if roll.status in counts:
            counts[roll.status] += 1
    return counts
