from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from roll.app.diagnostics.diagnostics import (
    Doctor,
    DoctorIssue,
    DoctorReport,
    run_doctor,
)
from roll.app.workspace.config import Config, load_config, set_lang
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


@dataclass(frozen=True)
class DoctorSection:
    title: str
    issues: list[DoctorIssue]


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

    sections: list[DoctorSection] = []
    if global_issues:
        sections.append(DoctorSection("Global config", global_issues))
    sections.extend(_workspace_sections(workspace_issues))

    _render_sections(sections)

    if report.missing_rolls:
        if sections:
            echo_lines([""])
        _echo_block(
            Doctor.ERROR_PREFIX,
            [Doctor.ROLL_MISSING],
            {Doctor.ROLL_MISSING: [str(path) for path in report.missing_rolls]},
        )

    _render_fix_summaries(report, config.archives, fix, verbose)

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


def _workspace_sections(issues: list[DoctorIssue]) -> list[DoctorSection]:
    archives: list[Path] = []
    for issue in issues:
        if issue.archive not in archives:
            archives.append(issue.archive)
    return [
        DoctorSection(
            f"Workspace {archive}",
            [issue for issue in issues if issue.archive == archive],
        )
        for archive in archives
    ]


def _render_sections(sections: list[DoctorSection]) -> None:
    for index, section in enumerate(sections):
        if index:
            echo_lines([""])
        _render_section(section.title, section.issues)


def _render_fix_summaries(
    report: DoctorReport, archives: list[Path], fix: bool, verbose: bool
) -> None:
    if report.fixable:
        _render_fix_summary(
            Msg.DOCTOR_CAN_FIX,
            report.fixable,
            verbose,
            fix,
            _apply_normalization_fixes,
            archives,
        )

    if report.keyword_vocab_fixes:
        _render_fix_summary(
            Msg.DOCTOR_CAN_ADD,
            report.keyword_vocab_fixes,
            verbose,
            fix,
            _apply_keyword_fixes,
            archives,
            hint=Msg.DOCTOR_FIX_HINT,
        )

    if fix and any(
        issue.message.startswith(str(Doctor.LANGUAGE_INVALID))
        for issue in report.issues
    ):
        set_lang("EN")
        from typer import echo

        echo(Msg.DOCTOR_FIXES_APPLIED)


def _render_fix_summary(
    title: str,
    items: list[str],
    verbose: bool,
    fix: bool,
    fixer,
    archives: list[Path],
    hint: str | None = None,
) -> None:
    echo_lines([""])
    from typer import echo

    echo(highlight_cli_names(f"{title} {len(items)}"))
    visible = items if verbose else items[:5]
    echo_lines([f"  {item}" for item in visible])
    if not verbose and len(items) > 5:
        echo(f"  {Msg.STATS_MORE.format(count=len(items) - 5)}")
    if fix:
        fixer(archives, verbose)
    elif hint is not None:
        echo_lines([""])
        echo(hint)


def _apply_normalization_fixes(archives: list[Path], verbose: bool) -> None:
    from typer import echo

    plans = [build_safe_rename_plan(archive) for archive in archives]
    apply_normalization_plans(plans)
    echo(Msg.DOCTOR_FIXES_APPLIED)
    if verbose:
        for plan in plans:
            if plan.rules:
                echo_lines([""])
                echo_lines(print_normalization_plan(plan))


def _apply_keyword_fixes(archives: list[Path], verbose: bool) -> None:
    from typer import echo

    for archive in archives:
        applied = apply_keyword_vocab_fixes(
            archive, collect_keyword_vocab_fixes(archive)
        )
        if applied and verbose:
            echo_lines([""])
            echo(f"  {applied}")
    echo(Msg.DOCTOR_KEYWORDS_APPLIED)


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
    return "", message


def _echo_block(prefix: str, order: list[str], groups: dict[str, list[str]]) -> None:
    from typer import echo

    total = sum(len(groups[title]) for title in order)
    echo(highlight_cli_names(f"{prefix} {total}"))
    for title in order:
        items = groups[title]
        if len(items) == 1 and title:
            echo(f"  {_group_title(title)} {items[0]}")
        elif title:
            echo(f"  {_group_title(title)} {len(items)}")
        else:
            echo(f"  {items[0]}")
        echo_lines([f"    {item}" for item in items])


def _group_title(title: str) -> str:
    return title if title.endswith(":") else f"{title}:"
