from __future__ import annotations

from pathlib import Path

import typer

from roll.app.archive.normalization import NormalizationPlan, RenameRule
from roll.app.archive.photo_dates import guess_archive_year, guess_archive_month
from roll.messages import Msg


def build_photo_normalization_plans(archive: Path) -> list[NormalizationPlan]:
    folders = _photo_folders(archive)
    year = guess_archive_year(archive)
    if year is None:
        typer.echo(str(Msg.CLI_UNINITIALIZED))
        raise typer.Exit(code=1)

    if not typer.confirm(
        str(Msg.NORMALIZE_PHOTOS_CONFIRM_YEAR).format(year=year), default=True
    ):
        typed_year = typer.prompt(
            str(Msg.NORMALIZE_PHOTOS_YEAR).format(folder=archive.name)
        )
        year = _parse_year(typed_year)

    manual_months = len(folders) > 1 and typer.confirm(
        str(Msg.NORMALIZE_PHOTOS_MANUAL), default=False
    )
    return [
        _build_photo_plan_for_folder(folder, archive, year, manual_months)
        for folder in folders
    ]


def echo_photo_plan_preview(plans: list[NormalizationPlan]) -> None:
    lines = []
    for plan in plans:
        for rule in plan.rules:
            lines.append(
                f"{rule.folder.name} -> {rule.target.relative_to(plan.archive)}"
            )

    if lines:
        typer.echo(str(Msg.NORMALIZE_PHOTOS_PREVIEW))
        for line in lines:
            typer.echo(f"  {line}")


def _build_photo_plan_for_folder(
    folder: Path, archive: Path, year: int, manual_months: bool
) -> NormalizationPlan:
    month = _prompt_month(folder) if manual_months else _guess_month(folder)

    if month is None:
        return NormalizationPlan(archive=archive, rules=[], conflicts=[])

    target = archive / f"{year:04d}" / f"{month:02d}-01"
    if target.exists():
        return NormalizationPlan(
            archive=archive,
            rules=[],
            conflicts=[f"{Msg.NORMALIZE_PHOTOS_MONTH} {target}"],
        )

    return NormalizationPlan(
        archive=archive, rules=[RenameRule(folder=folder, target=target)], conflicts=[]
    )


def _photo_folders(archive: Path) -> list[Path]:
    return [
        path for path in archive.iterdir() if path.is_dir() and path.name != ".roll"
    ]


def _prompt_month(folder: Path) -> int:
    while True:
        value = typer.prompt(
            str(Msg.NORMALIZE_PHOTOS_MONTH).format(folder=folder.name)
        ).strip()
        month = _parse_month(value)
        if month is not None:
            return month


def _guess_month(folder: Path) -> int | None:
    guess = guess_archive_month(folder)
    return guess.month if guess is not None else None


def _parse_year(value: str) -> int:
    year = value.strip()
    if len(year) == 4 and year.isdigit():
        return int(year)
    raise typer.Exit(code=1)


def _parse_month(value: str) -> int | None:
    month = value.strip()
    if len(month) == 2 and month.isdigit() and 1 <= int(month) <= 12:
        return int(month)
    return None
