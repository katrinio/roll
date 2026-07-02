from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from roll.messages import Msg

CONFIG_DIR = Path.home() / ".config" / "roll"
CONFIG_FILE = CONFIG_DIR / "config.yaml"



@dataclass(frozen=True)
class Config:
    archive: Path


def save_config(config: Config) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w", encoding="utf-8") as file:
        yaml.safe_dump(
            {"archive": str(config.archive)},
            file,
            allow_unicode=True,
            sort_keys=False,
        )


def read_config_data() -> dict[str, Any]:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(Msg.UNINITIALIZED_MESSAGE)

    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Invalid config format in {CONFIG_FILE}")

    return data


def load_config() -> Config:
    data = read_config_data()

    archive = data.get("archive")
    if not archive:
        raise FileNotFoundError(Msg.UNINITIALIZED_MESSAGE)

    return Config(archive=Path(archive))
