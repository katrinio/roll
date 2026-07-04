import re

import click

_ROLL_PATTERN = re.compile(r"(?<!\w)(roll|rl)(?!\w)")


def highlight_cli_names(message: str) -> str:
    highlighted = message.replace(
        "ERROR:", click.style("ERROR:", fg="red", bold=True)
    ).replace("WARN:", click.style("WARN:", fg="yellow", bold=True))
    return _ROLL_PATTERN.sub(
        lambda match: click.style(match.group(0), fg="green"), highlighted
    )
