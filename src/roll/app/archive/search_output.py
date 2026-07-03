from roll.helpers.output import echo_lines


def render_search_results(results) -> None:
    if not results:
        return

    echo_lines(["Найдено:", ""])

    for roll in results:
        echo_lines([f"{roll.loaded_at} — {roll.film}", f"Камера: {roll.camera}"])

        if roll.features:
            from typer import echo

            echo(f"Особенности: {', '.join(roll.features)}")

        if roll.keywords:
            from typer import echo

            echo(f"Теги: {', '.join(roll.keywords)}")

        echo_lines([f"Папка: {roll.folder}", ""])
