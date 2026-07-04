from pathlib import Path

import typer

from roll.app.workspace.roll_store import update_roll_status
from roll.app.archive.search import find_rolls
from roll.helpers.output import echo_list
from roll.messages import Msg
from roll.messages.cli import detect_locale


def process_archives(archives: list[Path]) -> int:
    loaded_rolls: list[Path] = []

    for archive in archives:
        for roll in find_rolls(archive):
            if roll.status == "loaded":
                loaded_rolls.append(roll.folder)

    if not loaded_rolls:
        typer.echo(Msg.BATCH_NO_LOADED)
        return 0

    typer.echo(f"{Msg.BATCH_WILL_PROCESS} {len(loaded_rolls)}")
    echo_list((str(path) for path in loaded_rolls))

    if not typer.confirm(Msg.BATCH_CONFIRM, default=False):
        return 0

    changed = 0
    for folder in loaded_rolls:
        update_roll_status(folder / "roll.toml", "processed")
        changed += 1

    typer.echo(f"{Msg.BATCH_PROCESSED} {changed}")
    return changed
