from __future__ import annotations

from pathlib import Path

from roll.app.diagnostics.diagnostics import Doctor, DoctorIssue, run_doctor
from roll.app.workspace.config import Config, load_config
from roll.app.archive.normalization import (
    apply_keyword_vocab_fixes,
    apply_normalization_plans,
    build_safe_rename_plan,
    collect_keyword_vocab_fixes,
    print_normalization_plan,
)
from roll.helpers.formatting import highlight_cli_names
from roll.helpers.output import echo_lines
from roll.messages import Msg


DOCTOR_MESSAGE_PREFIXES = (
    Doctor.ARCHIVE_MISSING,
    Doctor.WORKSPACE_CONFIG_MISSING,
    Doctor.WORKSPACE_CONFIG_MISMATCH,
    Doctor.WORKSPACE_STOCK_MISSING,
    Doctor.WORKSPACE_STOCK_INVALID,
    Doctor.WORKSPACE_MISSING,
    Doctor.VOCAB_DIR_MISSING,
    Doctor.VOCAB_FILE_MISSING,
    Doctor.ROLL_UNREADABLE,
    Doctor.ROLL_LOADED_AT_MISMATCH,
    Doctor.REQUIRED_FIELD_MISSING,
    Doctor.FILM_NOT_IN_VOCAB,
    Doctor.CAMERA_NOT_IN_VOCAB,
    Doctor.FEATURE_NOT_IN_VOCAB,
    Doctor.KEYWORD_NOT_IN_VOCAB,
    Doctor.KEYWORD_NOT_NORMALIZED,
    Doctor.SUSPICIOUS_YEAR,
    Doctor.SUSPICIOUS_ROLL,
)


def render_doctor(fix: bool = False, verbose: bool = False) -> int:
    try:
        config = load_config()
    except FileNotFoundError:
        report = run_doctor(Config(archives=[]))
    else:
        report = run_doctor(config)

    if not report.issues and not report.missing_rolls:
        from typer import echo

        echo(Doctor.OK)
        return 0

    global_issues = [issue for issue in report.issues if issue.archive is None]
    workspace_issues = [issue for issue in report.issues if issue.archive is not None]

    sections: list[tuple[str, list[DoctorIssue]]] = []
    if global_issues:
        sections.append(("Global config", global_issues))

    archives: list[Path] = []
    for issue in workspace_issues:
        if issue.archive not in archives:
            archives.append(issue.archive)
    for archive in archives:
        sections.append(
            (
                f"Workspace {archive}",
                [issue for issue in workspace_issues if issue.archive == archive],
            )
        )

    for index, (title, issues) in enumerate(sections):
        if index:
            echo_lines([""])
        _render_section(title, issues)

    if report.missing_rolls:
        if sections:
            echo_lines([""])
        _echo_block(
            Doctor.ERROR_PREFIX,
            [Doctor.ROLL_MISSING],
            {Doctor.ROLL_MISSING: [str(path) for path in report.missing_rolls]},
        )

    if report.fixable:
        echo_lines([""])
        from typer import echo

        echo(highlight_cli_names(f"{Msg.DOCTOR_CAN_FIX} {len(report.fixable)}"))
        items = report.fixable if verbose else report.fixable[:5]
        echo_lines([f"  {item}" for item in items])
        if not verbose and len(report.fixable) > 5:
            echo(f"  {Msg.STATS_MORE.format(count=len(report.fixable) - 5)}")
        if fix:
            plans = [build_safe_rename_plan(archive) for archive in config.archives]
            apply_normalization_plans(plans)
            echo(Msg.DOCTOR_FIXES_APPLIED)
            if verbose:
                for plan in plans:
                    if plan.rules:
                        echo_lines([""])
                        echo_lines(print_normalization_plan(plan))

    if report.keyword_vocab_fixes:
        echo_lines([""])
        from typer import echo

        echo(
            highlight_cli_names(
                f"{Msg.DOCTOR_CAN_ADD} {len(report.keyword_vocab_fixes)}"
            )
        )
        items = (
            report.keyword_vocab_fixes if verbose else report.keyword_vocab_fixes[:5]
        )
        echo_lines([f"  {item}" for item in items])
        if not verbose and len(report.keyword_vocab_fixes) > 5:
            echo(
                f"  {Msg.STATS_MORE.format(count=len(report.keyword_vocab_fixes) - 5)}"
            )
        if fix:
            for archive in config.archives:
                applied = apply_keyword_vocab_fixes(
                    archive, collect_keyword_vocab_fixes(archive)
                )
                if applied and verbose:
                    echo_lines([""])
                    echo(f"  {applied}")
            echo(Msg.DOCTOR_KEYWORDS_APPLIED)
        else:
            echo_lines([""])

            echo(Msg.DOCTOR_FIX_HINT)

    return (
        1
        if any(issue.level == "error" for issue in report.issues)
        or report.missing_rolls
        else 0
    )


def _render_section(title: str, issues: list) -> None:
    from typer import echo

    echo(title)

    error_groups: dict[str, list[str]] = {}
    warning_groups: dict[str, list[str]] = {}
    error_order: list[str] = []
    warning_order: list[str] = []

    for issue in issues:
        group_title, item = _split_message(issue.message)
        if issue.level == "error":
            _append_group(error_groups, error_order, group_title, [item])
        else:
            _append_group(warning_groups, warning_order, group_title, [item])

    if error_order:
        _echo_block(Doctor.ERROR_PREFIX, error_order, error_groups)
    if warning_order:
        if error_order:
            echo_lines([""])
        _echo_block(Doctor.WARN_PREFIX, warning_order, warning_groups)


def _append_group(
    groups: dict[str, list[str]],
    order: list[str],
    title: str,
    items: list[str],
) -> None:
    if title not in groups:
        groups[title] = []
        order.append(title)
    groups[title].extend(items)


def _split_message(message: str) -> tuple[str, str]:
    for prefix in DOCTOR_MESSAGE_PREFIXES:
        if message.startswith(prefix):
            return prefix, message.removeprefix(prefix).strip()
    return message, message


def _echo_block(prefix: str, order: list[str], groups: dict[str, list[str]]) -> None:
    from typer import echo

    total = sum(len(groups[title]) for title in order)
    echo(highlight_cli_names(f"{prefix} {total}"))
    for title in order:
        items = groups[title]
        echo(f"  {_group_title(title)} {len(items)}")
        echo_lines([f"    {item}" for item in items])


def _group_title(title: str) -> str:
    return title if title.endswith(":") else f"{title}:"
