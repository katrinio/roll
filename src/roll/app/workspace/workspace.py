from dataclasses import dataclass
from pathlib import Path

from roll.app.workspace.config import Config
from roll.dictionaries import Dictionary

WORKSPACE_DIR_NAME = ".roll"
WORKSPACE_CONFIG_NAME = "config.toml"
WORKSPACE_VOCABULARY_DIR_NAME = "vocabulary"
WORKSPACE_STOCK_FILE_NAME = "stock.toml"


@dataclass(frozen=True)
class Workspace:
    archive: Path

    @property
    def root(self) -> Path:
        return self.archive / WORKSPACE_DIR_NAME

    @property
    def config_file(self) -> Path:
        return self.root / WORKSPACE_CONFIG_NAME

    @property
    def vocabulary_dir(self) -> Path:
        return self.root / WORKSPACE_VOCABULARY_DIR_NAME

    @property
    def stock_file(self) -> Path:
        return self.root / WORKSPACE_STOCK_FILE_NAME

    def vocabulary_file(self, name: str) -> Path:
        return self.vocabulary_dir / f"{name}.txt"

    def dictionary(self, name: str) -> Dictionary:
        return Dictionary(name=name, path=self.vocabulary_file(name))

    def ensure_structure(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.vocabulary_dir.mkdir(parents=True, exist_ok=True)
        self.stock_file.touch(exist_ok=True)
        if not self.config_file.exists():
            self.config_file.write_text(
                f'archive = "{self.archive}"\n',
                encoding="utf-8",
            )
        for name in ("films", "cameras", "features", "keywords"):
            self.vocabulary_file(name).touch(exist_ok=True)


def workspace_for(archive: Path) -> Workspace:
    return Workspace(archive=archive)


def primary_archive(config: Config) -> Path:
    if not config.archives:
        raise FileNotFoundError("No archives configured")
    return config.archives[0]
