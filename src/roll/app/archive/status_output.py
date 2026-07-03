from roll.helpers.output import echo_lines, echo_list


def render_status_report(archive, roll_folders, unindexed_folders, status_counts) -> None:
    echo_lines(
        [
            "Состояние индекса",
            "",
            f"Папок в архиве: {len(roll_folders)}",
            f"Проиндексировано: {len(roll_folders) - len(unindexed_folders)}",
            f"Не проиндексировано: {len(unindexed_folders)}",
            "",
            "Пленки по статусам:",
            f"loaded: {status_counts.get('loaded', 0)}",
            f"processed: {status_counts.get('processed', 0)}",
            f"failed: {status_counts.get('failed', 0)}",
            f"без roll.toml: {len(unindexed_folders)}",
        ]
    )

    if unindexed_folders:
        echo_lines(["", "Не проиндексированные папки:"])
        echo_list((folder.relative_to(archive) for folder in unindexed_folders))
