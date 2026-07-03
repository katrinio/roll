from dataclasses import dataclass
from pathlib import Path

import yaml
import tomllib

from roll.messages import Msg

CONFIG_DIR = Path.home() / ".config" / "roll"
CONFIG_FILE = CONFIG_DIR / "config.toml"
@dataclass(frozen=True)
class Config:
    archives: list[Path]


def save_config(config: Config) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w", encoding="utf-8") as file:
        file.write("archives = [\n")
        for archive in config.archives:
            file.write(f'  "{archive}",\n')
        file.write("]\n")


def read_config_data() -> dict:
    if CONFIG_FILE.exists():
        with CONFIG_FILE.open("rb") as file:
            data = tomllib.load(file)
    else:
        legacy_file = CONFIG_DIR / "config.yaml"
        if not legacy_file.exists():
            raise FileNotFoundError(Msg.UNINITIALIZED_MESSAGE)
        with legacy_file.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Invalid config format in {CONFIG_FILE}")

    return data


def load_config() -> Config:
    data = read_config_data()

    archives = data.get("archives") or []
    if not archives and data.get("archive"):
        archives = [data["archive"]]
    if not archives:
        raise FileNotFoundError(Msg.UNINITIALIZED_MESSAGE)

    return Config(archives=[Path(archive) for archive in archives])
