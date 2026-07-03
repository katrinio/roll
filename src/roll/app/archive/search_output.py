from typer import echo

from roll.helpers.output import echo_lines


def render_search_results(results) -> None:
    if not results:
        return

    echo_lines(["Найдено:", ""])

    for roll in results:
        echo_lines([f"{roll.loaded_at} — {roll.film}", f"Камера: {roll.camera}"])

        if roll.features:
            echo(f"Особенности: {', '.join(roll.features)}")

        if roll.keywords:
            echo(f"Теги: {', '.join(roll.keywords)}")

        echo_lines([f"Папка: {roll.folder}", ""])
