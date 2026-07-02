from pathlib import Path


def save_roll_index(
    folder: Path,
    film: str,
    features: list[str],
    camera: str,
    loaded_at: str,
    keywords: list[str],
) -> None:
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