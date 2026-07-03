from pathlib import Path

INDEX_FILE_NAME = "roll.toml"


def get_index_file(folder: Path) -> Path:
    return folder / INDEX_FILE_NAME


def is_indexed(folder: Path) -> bool:
    return (folder / INDEX_FILE_NAME).exists()


def find_unindexed_folders(archive: Path) -> list[Path]:
    return [folder for folder in find_roll_folders(archive) if not is_indexed(folder)]


def find_roll_folders(archive: Path) -> list[Path]:
    year_dirs = sorted(
        path for path in archive.iterdir() if path.is_dir() and path.name.isdigit() and len(path.name) == 4
    )

    roll_folders: list[Path] = []

    for year_dir in year_dirs:
        roll_folders.extend(sorted(path for path in year_dir.iterdir() if path.is_dir() and path.name != ".roll"))

    return roll_folders
