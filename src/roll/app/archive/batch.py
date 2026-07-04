from pathlib import Path

import typer

from roll.app.workspace.roll_store import update_roll_status
from roll.app.archive.search import find_rolls
from roll.helpers.output import echo_list
from roll.messages.cli import detect_locale


def process_archives(archives: list[Path]) -> int:
    loaded_rolls: list[Path] = []

    for archive in archives:
        for roll in find_rolls(archive):
            if roll.status == "loaded":
                loaded_rolls.append(roll.folder)

    if not loaded_rolls:
        typer.echo("No loaded rolls." if detect_locale() == "en" else "Нет loaded-роллов.")
        return 0

    typer.echo(f"{'Will process' if detect_locale() == 'en' else 'Будет обработано'}: {len(loaded_rolls)}")
    echo_list((str(path) for path in loaded_rolls))

    if not typer.confirm("Mark all as processed?" if detect_locale() == "en" else "Пометить все как processed?", default=False):
        return 0

    changed = 0
    for folder in loaded_rolls:
        update_roll_status(folder / "roll.toml", "processed")
        changed += 1

    typer.echo(f"{'Processed' if detect_locale() == 'en' else 'Обработано'}: {changed}")
    return changed
