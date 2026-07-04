from roll.helpers.output import echo_lines, echo_list

from roll.app.archive.normalization import print_normalization_plan
from roll.messages import Msg, Normalize


def render_normalization_plans(plans) -> tuple[int, bool]:
    total_rules = sum(len(plan.rules) for plan in plans)
    has_changes = any(plan.has_changes for plan in plans)

    for plan in plans:
        echo_lines(
            [
                f"{Msg.ARCHIVE_HEADER} {plan.archive}",
                *print_normalization_plan(plan),
                "",
            ]
        )

    if not has_changes:
        return total_rules, has_changes

    all_conflicts = [conflict for plan in plans for conflict in plan.conflicts]
    if all_conflicts:
        echo_lines([Normalize.CONFLICTS_HEADER])
        echo_list(all_conflicts)

    return total_rules, has_changes
