from dataclasses import dataclass
from pathlib import Path

import tomllib
import yaml

CONFIG_DIR = Path.home() / ".config" / "roll"
CONFIG_FILE = CONFIG_DIR / "config.toml"

VALID_LANGS = {"RU", "EN"}


@dataclass(frozen=True)
class Config:
    archives: list[Path]
    lang: str = "RU"


def save_config(config: Config) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w", encoding="utf-8") as file:
        file.write(f'lang = "{config.lang}"\n')
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
            raise FileNotFoundError("roll is not initialized.")
        with legacy_file.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Invalid config format in {CONFIG_FILE}")

    return data


def load_config() -> Config:
    data = read_config_data()

    lang = str(data.get("lang", "RU")).upper()
    if lang not in VALID_LANGS:
        lang = "RU"

    archives = data.get("archives") or []
    if not archives and data.get("archive"):
        archives = [data["archive"]]
    if not archives:
        raise FileNotFoundError("roll is not initialized.")

    return Config(archives=[Path(archive) for archive in archives], lang=lang)


def load_lang() -> str:
    try:
        return load_config().lang
    except FileNotFoundError:
        return "RU"


def set_lang(lang: str) -> Config:
    current = load_config()
    updated = Config(archives=current.archives, lang=lang.upper())
    save_config(updated)
    return updated
