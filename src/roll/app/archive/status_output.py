from roll.messages import Msg
from roll.helpers.output import echo_lines, echo_list


def render_status_report(
    archive, roll_folders, unindexed_folders, status_counts
) -> None:
    echo_lines(
        [
            Msg.STATUS_HEADER,
            "",
            f"{Msg.STATUS_ARCHIVE_FOLDERS} {len(roll_folders)}",
            f"{Msg.STATUS_INDEXED} {len(roll_folders) - len(unindexed_folders)}",
            f"{Msg.STATUS_UNINDEXED} {len(unindexed_folders)}",
            "",
            Msg.STATUS_ROLLS,
            f"loaded {status_counts.get('loaded', 0)}",
            f"processed {status_counts.get('processed', 0)}",
            f"failed {status_counts.get('failed', 0)}",
            f"{Msg.STATUS_NO_ROLL_TOML} {len(unindexed_folders)}",
        ]
    )

    if unindexed_folders:
        echo_lines(["", Msg.STATUS_UNINDEXED_FOLDERS])
        echo_list((folder.relative_to(archive) for folder in unindexed_folders))
