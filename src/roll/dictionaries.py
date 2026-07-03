from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Dictionary:
    name: str
    path: Path

    def read(self) -> list[str]:
        if not self.path.exists():
            return []

        values = [
            line.strip()
            for line in self.path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        return _sort_unique(values)

    def write(self, values: list[str]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        normalized = _sort_unique(values)
        self.path.write_text("\n".join(normalized) + ("\n" if normalized else ""), encoding="utf-8")

    def add(self, value: str) -> str:
        values = self.read()
        normalized_value = value.strip()
        if not normalized_value:
            return normalized_value

        if _contains(values, normalized_value):
            return _existing_value(values, normalized_value)

        values.append(normalized_value)
        self.write(values)
        return normalized_value


def _sort_unique(values: list[str]) -> list[str]:
    seen: dict[str, str] = {}
    for value in values:
        key = value.casefold()
        if key not in seen:
            seen[key] = value

    return sorted(seen.values(), key=str.casefold)


def _contains(values: list[str], candidate: str) -> bool:
    return any(value.casefold() == candidate.casefold() for value in values)


def _existing_value(values: list[str], candidate: str) -> str:
    for value in values:
        if value.casefold() == candidate.casefold():
            return value
    return candidate
