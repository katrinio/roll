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
        path
        for path in archive.iterdir()
        if path.is_dir() and path.name.isdigit() and len(path.name) == 4
    )

    roll_folders: list[Path] = []

    for year_dir in year_dirs:
        roll_folders.extend(
            sorted(
                path
                for path in year_dir.iterdir()
                if path.is_dir() and path.name != ".roll"
            )
        )

    return roll_folders


def count_photo_files(folder: Path) -> int:
    if not folder.exists():
        return 0

    return sum(
        1
        for path in folder.rglob("*")
        if path.is_file()
        and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".heic", ".tif", ".tiff"}
    )


def build_archive_tree(archive: Path) -> list[str]:
    lines: list[str] = []
    year_dirs = sorted(
        path
        for path in archive.iterdir()
        if path.is_dir() and path.name.isdigit() and len(path.name) == 4
    )

    for year_dir in year_dirs:
        lines.append(year_dir.name)
        roll_folders = sorted(
            path
            for path in year_dir.iterdir()
            if path.is_dir() and path.name != ".roll"
        )
        for index, roll_dir in enumerate(roll_folders):
            connector = "└──" if index == len(roll_folders) - 1 else "├──"
            lines.append(f"  {connector} {roll_dir.name}")

    return lines
