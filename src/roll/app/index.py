from pathlib import Path

from roll.app.workspace import workspace_for
from roll.helpers.autocomplete import autocomplete_prompt
from roll.helpers.prompts import choose_many, choose_or_create


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
        camera = choose_or_create(workspace.dictionary("cameras"), "Камера:")

    if not features:
        features = choose_many(workspace.dictionary("features"), "Features", "Введите номера или новые слова через запятую.")

    if not keywords:
        keywords = choose_many(workspace.dictionary("keywords"), "Keywords", "Введите номера или новые слова через запятую.")

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
