from roll.messages import Msg
from typer import echo

from roll.helpers.output import echo_lines


def render_search_results(results) -> None:
    if not results:
        return

    echo_lines([Msg.SEARCH_HEADER, ""])

    for roll in results:
        echo_lines(
            [f"{roll.loaded_at} — {roll.film}", f"{Msg.SEARCH_CAMERA} {roll.camera}"]
        )

        if roll.features:
            echo(f"{Msg.SEARCH_FEATURES} {', '.join(roll.features)}")

        if roll.keywords:
            echo(f"{Msg.SEARCH_TAGS} {', '.join(roll.keywords)}")

        echo_lines([f"{Msg.SEARCH_FOLDER} {roll.folder}", ""])
