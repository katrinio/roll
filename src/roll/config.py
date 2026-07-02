from dataclasses import dataclass
from pathlib import Path

import yaml

CONFIG_DIR = Path.home() / ".config" / "roll"
CONFIG_FILE = CONFIG_DIR / "config.yaml"


UNINITIALIZED_MESSAGE = "roll is not initialized.\nRun: rl init ~/your/archive/path"


@dataclass
class Config:
    archive: Path


def read_config_data() -> dict:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(UNINITIALIZED_MESSAGE)

    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def load_config() -> Config:
    data = read_config_data()

    archive = data.get("archive")
    if not archive:
        raise FileNotFoundError(UNINITIALIZED_MESSAGE)

    return Config(archive=Path(archive))
