from __future__ import annotations

import typer

from roll.app.archive.normalize_cli import (
    build_photo_normalization_plans,
    echo_photo_plan_preview,
)
from roll.app.archive.normalization import (
    apply_normalization_plans,
    build_normalization_plan,
    normalize_keywords_in_archive,
)
from roll.app.archive.normalization_output import render_normalization_plans
from roll.helpers.guards import require_config, require_current_archive
from roll.messages import Msg, Normalize


def normalize(tags: bool, photos: bool) -> None:
    config = require_config()
    archive = require_current_archive(config)

    if tags:
        touched = normalize_keywords_in_archive(archive)
        if touched:
            typer.echo(str(Msg.TAGS_NORMALIZED))
            for path in touched:
                typer.echo(f"  {path}")
        else:
            typer.echo(str(Msg.TAGS_ALREADY_NORMALIZED))
        return

    if photos:
        plans = build_photo_normalization_plans(archive)
        total_rules, has_changes = render_normalization_plans(plans)
        if not has_changes:
            return

        all_conflicts = [conflict for plan in plans for conflict in plan.conflicts]
        if all_conflicts:
            raise typer.Exit(code=1)

        echo_photo_plan_preview(plans)
        if not typer.confirm(
            str(Normalize.QUESTION).format(count=total_rules), default=False
        ):
            return

        apply_normalization_plans(plans)
        return

    plans = [build_normalization_plan(archive)]
    total_rules, has_changes = render_normalization_plans(plans)
    if not has_changes:
        return

    all_conflicts = [conflict for plan in plans for conflict in plan.conflicts]
    if all_conflicts:
        raise typer.Exit(code=1)

    if not typer.confirm(
        str(Normalize.QUESTION).format(count=total_rules), default=False
    ):
        return

    apply_normalization_plans(plans)
