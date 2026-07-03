from pathlib import Path

from roll.app.workspace import workspace_for
from roll.helpers.autocomplete import autocomplete_many_prompt, autocomplete_prompt


def save_roll_index(
    folder: Path,
    archive: Path | None = None,
    film: str | None = None,
    features: list[str] | None = None,
    camera: str | None = None,
    loaded_at: str | None = None,
    keywords: list[str] | None = None,
) -> None:
    workspace = workspace_for(archive or folder.parents[1])

    if not film:
        film = autocomplete_prompt("Пленка", workspace.dictionary("films"))

    if not camera:
        camera = autocomplete_prompt("Камера", workspace.dictionary("cameras"))

    if not features:
        features = autocomplete_many_prompt("Особенности", workspace.dictionary("features"))

    if not keywords:
        keywords = autocomplete_many_prompt("Ключевые слова", workspace.dictionary("keywords"))

    def format_array(values: list[str] | None) -> str:
        items = values or []
        return "[" + ", ".join(f'"{item}"' for item in items) + "]"

    content = "\n".join(
        [
            f'film = "{film}"',
            f"features = {format_array(features)}",
            f'camera = "{camera}"',
            f'loaded_at = "{loaded_at}"',
            f"keywords = {format_array(keywords)}",
            "",
        ]
    )

    (folder / "roll.toml").write_text(content, encoding="utf-8")
