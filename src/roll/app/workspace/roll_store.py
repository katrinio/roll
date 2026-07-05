from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib
import os
from roll.messages import Msg

from roll.app.workspace.statuses import VALID_STATUSES


@dataclass(frozen=True)
class RollMetadata:
    status: str
    film: str
    camera: str
    loaded_at: str
    features: list[str]
    keywords: list[str]
    original_source: str = "unknown"
    digital_copy: str = "unknown"
    original_status: str = "unknown"


def load_roll_metadata(path: Path) -> RollMetadata:
    data = _load_toml(path)
    return _validate_metadata(data, path)


def save_roll_metadata(path: Path, metadata: RollMetadata) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.tmp")
    temp_path.write_text(
        "\n".join(
            [
                f'status = "{metadata.status}"',
                f'film = "{metadata.film}"',
                f'camera = "{metadata.camera}"',
                f'loaded_at = "{metadata.loaded_at}"',
                f'original_source = "{metadata.original_source}"',
                f'digital_copy = "{metadata.digital_copy}"',
                f'original_status = "{metadata.original_status}"',
                f"features = {_format_array(metadata.features)}",
                f"keywords = {_format_array(metadata.keywords)}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    os.replace(temp_path, path)


def update_roll_status(path: Path, status: str) -> RollMetadata:
    metadata = load_roll_metadata(path)
    updated = RollMetadata(
        status=status,
        film=metadata.film,
        camera=metadata.camera,
        loaded_at=metadata.loaded_at,
        features=metadata.features,
        keywords=metadata.keywords,
        original_source=metadata.original_source,
        digital_copy=metadata.digital_copy,
        original_status=metadata.original_status,
    )
    save_roll_metadata(path, updated)
    return updated


def update_roll_keywords(path: Path, keywords: list[str]) -> RollMetadata:
    metadata = load_roll_metadata(path)
    updated = RollMetadata(
        status=metadata.status,
        film=metadata.film,
        camera=metadata.camera,
        loaded_at=metadata.loaded_at,
        features=metadata.features,
        keywords=_merge_unique(metadata.keywords, keywords, normalize=str.upper),
        original_source=metadata.original_source,
        digital_copy=metadata.digital_copy,
        original_status=metadata.original_status,
    )
    save_roll_metadata(path, updated)
    return updated


def update_roll_features(path: Path, features: list[str]) -> RollMetadata:
    metadata = load_roll_metadata(path)
    updated = RollMetadata(
        status=metadata.status,
        film=metadata.film,
        camera=metadata.camera,
        loaded_at=metadata.loaded_at,
        features=_merge_unique(metadata.features, features),
        keywords=metadata.keywords,
        original_source=metadata.original_source,
        digital_copy=metadata.digital_copy,
        original_status=metadata.original_status,
    )
    save_roll_metadata(path, updated)
    return updated


def update_roll_origin(
    path: Path,
    original_source: str,
    digital_copy: str,
    original_status: str,
) -> RollMetadata:
    metadata = load_roll_metadata(path)
    updated = RollMetadata(
        status=metadata.status,
        film=metadata.film,
        camera=metadata.camera,
        loaded_at=metadata.loaded_at,
        features=metadata.features,
        keywords=metadata.keywords,
        original_source=original_source,
        digital_copy=digital_copy,
        original_status=original_status,
    )
    save_roll_metadata(path, updated)
    return updated


def _load_toml(path: Path) -> dict:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"{Msg.ROLL_READ_ERROR} {path}") from exc


def _validate_metadata(data: dict, path: Path) -> RollMetadata:
    status = str(data.get("status", ""))
    film = str(data.get("film", ""))
    camera = str(data.get("camera", ""))
    loaded_at = str(data.get("loaded_at", ""))
    original_source = str(data.get("original_source", "unknown"))
    digital_copy = str(data.get("digital_copy", "unknown"))
    original_status = str(data.get("original_status", "unknown"))
    features = data.get("features", [])
    keywords = data.get("keywords", [])

    if status not in VALID_STATUSES:
        raise ValueError(f"{Msg.ROLL_STATUS_INVALID} {path}")
    if not film or not camera or not loaded_at:
        raise ValueError(f"{Msg.ROLL_FORMAT_ERROR} {path}")
    if not isinstance(features, list) or not isinstance(keywords, list):
        raise ValueError(f"{Msg.ROLL_FORMAT_ERROR} {path}")

    return RollMetadata(
        status=status,
        film=film,
        camera=camera,
        loaded_at=loaded_at,
        features=[str(item) for item in features],
        keywords=[str(item) for item in keywords],
        original_source=original_source,
        digital_copy=digital_copy,
        original_status=original_status,
    )


def _format_array(values: list[str]) -> str:
    return "[" + ", ".join(f'"{item}"' for item in values) + "]"


def _merge_unique(
    existing: list[str], new_values: list[str], normalize=lambda value: value
) -> list[str]:
    merged: list[str] = []
    for value in [*existing, *new_values]:
        normalized = normalize(value)
        if normalized not in [normalize(item) for item in merged]:
            merged.append(normalized)
    return merged
