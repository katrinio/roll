from pathlib import Path

from roll.dictionaries import Dictionary
from roll.app.workspace.workspace import workspace_for


def archive_vocabulary(archive: Path) -> dict[str, Dictionary]:
    workspace = workspace_for(archive)
    return {
        "films": workspace.dictionary("films"),
        "cameras": workspace.dictionary("cameras"),
        "features": workspace.dictionary("features"),
        "keywords": workspace.dictionary("keywords"),
    }
