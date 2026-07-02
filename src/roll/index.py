from pathlib import Path

from roll.helpers.prompts import choose_many, choose_or_create
from roll.vocabulary import FILMS, CAMERAS, FEATURES, KEYWORDS


def save_roll_index(
    folder: Path,
    film: str | None = None,
    features: list[str] | None = None,
    camera: str | None = None,
    loaded_at: str | None = None,
    keywords: list[str] | None = None,
) -> None:
    if not film:
        film = choose_or_create(FILMS, "Пленка:")

    if not camera:
        camera = choose_or_create(CAMERAS, "Камера:")

    if not features:
        features = choose_many(FEATURES, "Features", "Введите номера или новые слова через запятую.")

    if not keywords:
        keywords = choose_many(KEYWORDS, "Keywords", "Введите номера или новые слова через запятую.")

    content = "\n".join(
        [
            f'film = "{film}"',
            f'features = "{features or "-"}"',
            f'camera = "{camera}"',
            f'loaded_at = "{loaded_at}"',
            f'keywords = {keywords!r}',
            "",
        ]
    )

    (folder / "roll.toml").write_text(content, encoding="utf-8")
