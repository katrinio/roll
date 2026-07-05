from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class PhotoDateGuess:
    year: int
    month: int
    confidence: int

    @property
    def month_key(self) -> str:
        return f"{self.year:04d}-{self.month:02d}"


def guess_archive_month(folder: Path) -> PhotoDateGuess | None:
    counts = _month_counts(folder)
    if not counts:
        return None

    month_key, confidence = counts.most_common(1)[0]
    year, month = month_key.split("-", 1)
    return PhotoDateGuess(year=int(year), month=int(month), confidence=confidence)


def guess_archive_year(folder: Path) -> int | None:
    counts = _month_counts(folder)
    if not counts:
        return None

    year_counter = Counter(
        month_key.split("-", 1)[0] for month_key in counts.elements()
    )
    year, _ = year_counter.most_common(1)[0]
    return int(year)


def _photo_files(folder: Path) -> list[Path]:
    if not folder.exists():
        return []

    return [
        path
        for path in folder.rglob("*")
        if path.is_file()
        and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".heic", ".tif", ".tiff"}
    ]


def _month_counts(folder: Path) -> Counter[str]:
    timestamps = [photo.stat().st_mtime for photo in _photo_files(folder)]
    return Counter(_month_key(timestamp) for timestamp in timestamps)


def _month_key(timestamp: float) -> str:
    dt = datetime.fromtimestamp(timestamp)
    return f"{dt.year:04d}-{dt.month:02d}"
