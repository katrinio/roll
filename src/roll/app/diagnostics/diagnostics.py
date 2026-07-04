from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import tomllib

from roll.filesystem import find_roll_folders, get_index_file, find_unindexed_folders
from roll.app.workspace.config import CONFIG_FILE, Config
from roll.app.archive.normalization import (
    build_safe_rename_plan,
    collect_keyword_vocab_fixes,
)
from roll.messages import Doctor
from roll.app.workspace.stock_store import load_stock
from roll.app.workspace.vocabulary import archive_vocabulary
from roll.app.workspace.workspace import workspace_for


class DoctorText:
    ERROR = "error"
    WARNING = "warning"
    VOCAB_FILES = ("films", "cameras", "features", "keywords")
    MANDATORY_FIELDS = ("status", "film", "camera", "loaded_at")


@dataclass(frozen=True)
class DoctorIssue:
    level: str
    message: str
    archive: Path | None = None


@dataclass(frozen=True)
class DoctorReport:
    issues: list[DoctorIssue]
    fixable: list[str]
    keyword_vocab_fixes: list[str]
    missing_rolls: list[Path]
    missing_roll_count: int
    unindexed_folders: list[Path]

    @property
    def has_errors(self) -> bool:
        return any(issue.level == DoctorText.ERROR for issue in self.issues)


def run_doctor(config: Config) -> DoctorReport:
    issues: list[DoctorIssue] = []
    fixable: list[str] = []
    keyword_vocab_fixes: list[str] = []
    missing_rolls: list[Path] = []
    unindexed_folders: list[Path] = []
    missing_roll_count = 0

    global_issues = _check_global_config()
    issues.extend(global_issues)
    global_config_missing = any(
        issue.message.startswith(str(Doctor.GLOBAL_CONFIG_MISSING))
        for issue in global_issues
    )

    if not config.archives and not global_config_missing:
        issues.append(DoctorIssue(DoctorText.ERROR, Doctor.NO_ARCHIVES))
        return DoctorReport(
            issues=issues,
            fixable=fixable,
            keyword_vocab_fixes=keyword_vocab_fixes,
            missing_rolls=missing_rolls,
            missing_roll_count=missing_roll_count,
            unindexed_folders=unindexed_folders,
        )

    for archive in config.archives:
        archive_issues, archive_missing_rolls, archive_unindexed = _check_archive(
            archive
        )
        issues.extend(archive_issues)
        missing_rolls.extend(archive_missing_rolls)
        unindexed_folders.extend(archive_unindexed)
        missing_roll_count += len(archive_missing_rolls)
        plan = build_safe_rename_plan(archive)
        fixable.extend(
            f"{rule.folder.relative_to(archive)} -> {rule.target.relative_to(archive)}"
            for rule in plan.rules
        )
        keyword_vocab_fixes.extend(collect_keyword_vocab_fixes(archive))

    return DoctorReport(
        issues=issues,
        fixable=fixable,
        keyword_vocab_fixes=keyword_vocab_fixes,
        missing_rolls=missing_rolls,
        missing_roll_count=missing_roll_count,
        unindexed_folders=unindexed_folders,
    )


def _check_global_config() -> list[DoctorIssue]:
    if not CONFIG_FILE.exists():
        return [
            DoctorIssue(
                DoctorText.ERROR, f"{Doctor.GLOBAL_CONFIG_MISSING} {CONFIG_FILE}"
            )
        ]

    try:
        data = tomllib.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception as exc:
        return [
            DoctorIssue(
                DoctorText.ERROR,
                f"{Doctor.GLOBAL_CONFIG_INVALID} {CONFIG_FILE} ({exc})",
            )
        ]

    issues: list[DoctorIssue] = []
    if "lang" not in data:
        issues.append(
            DoctorIssue(DoctorText.WARNING, str(Doctor.LANGUAGE_NOT_EXPLICIT))
        )
    else:
        lang = str(data.get("lang", "")).upper()
        if lang not in {"EN", "RU"}:
            issues.append(DoctorIssue(DoctorText.WARNING, str(Doctor.LANGUAGE_INVALID)))

    return issues


def _check_archive(archive: Path) -> tuple[list[DoctorIssue], list[Path], list[Path]]:
    issues: list[DoctorIssue] = []
    missing_rolls: list[Path] = []
    unindexed_folders: list[Path] = []

    if not archive.exists():
        return (
            [
                DoctorIssue(
                    DoctorText.ERROR, f"{Doctor.ARCHIVE_MISSING} {archive}", archive
                )
            ],
            missing_rolls,
            unindexed_folders,
        )

    workspace = workspace_for(archive)
    issues.extend(_check_workspace(workspace))
    roll_issues, archive_missing_rolls = _check_rolls(archive, workspace)
    issues.extend(roll_issues)
    missing_rolls.extend(archive_missing_rolls)
    unindexed_folders.extend(_check_unindexed(archive))
    issues.extend(_check_naming(archive))

    return issues, missing_rolls, unindexed_folders


def _check_workspace(workspace) -> list[DoctorIssue]:
    issues: list[DoctorIssue] = []

    if not workspace.root.exists():
        issues.append(
            DoctorIssue(
                DoctorText.ERROR,
                f"{Doctor.WORKSPACE_MISSING} {workspace.root}",
                workspace.archive,
            )
        )
        return issues

    if not workspace.config_file.exists():
        issues.append(
            DoctorIssue(
                DoctorText.ERROR,
                f"{Doctor.WORKSPACE_CONFIG_MISSING} {workspace.config_file}",
                workspace.archive,
            )
        )
    else:
        try:
            data = tomllib.loads(workspace.config_file.read_text(encoding="utf-8"))
        except Exception as exc:
            issues.append(
                DoctorIssue(
                    DoctorText.ERROR,
                    f"{Doctor.WORKSPACE_CONFIG_INVALID} {workspace.config_file} ({exc})",
                    workspace.archive,
                )
            )
        else:
            archive_value = str(data.get("archive", "")).strip()
            if not archive_value:
                issues.append(
                    DoctorIssue(
                        DoctorText.WARNING,
                        str(Doctor.WORKSPACE_CONFIG_ARCHIVE_MISSING),
                        workspace.archive,
                    )
                )
            elif Path(archive_value) != workspace.archive:
                issues.append(
                    DoctorIssue(
                        DoctorText.WARNING,
                        f"{Doctor.WORKSPACE_CONFIG_MISMATCH} {workspace.config_file} -> {archive_value}",
                        workspace.archive,
                    )
                )

    if not workspace.stock_file.exists():
        issues.append(
            DoctorIssue(
                DoctorText.ERROR,
                f"{Doctor.WORKSPACE_STOCK_MISSING} {workspace.stock_file}",
                workspace.archive,
            )
        )
    else:
        try:
            load_stock(workspace.stock_file)
        except ValueError as exc:
            issues.append(
                DoctorIssue(
                    DoctorText.ERROR,
                    f"{Doctor.WORKSPACE_STOCK_INVALID} {workspace.stock_file} ({exc})",
                    workspace.archive,
                )
            )

    if not workspace.vocabulary_dir.exists():
        issues.append(
            DoctorIssue(
                DoctorText.ERROR,
                f"{Doctor.VOCAB_DIR_MISSING} {workspace.vocabulary_dir}",
                workspace.archive,
            )
        )
        return issues

    for name in DoctorText.VOCAB_FILES:
        vocab_file = workspace.vocabulary_file(name)
        if not vocab_file.exists():
            issues.append(
                DoctorIssue(
                    DoctorText.ERROR,
                    f"{Doctor.VOCAB_FILE_MISSING} {vocab_file}",
                    workspace.archive,
                )
            )
            continue

        if name == "keywords":
            try:
                values = [
                    line.strip()
                    for line in vocab_file.read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ]
            except Exception as exc:
                issues.append(
                    DoctorIssue(
                        DoctorText.ERROR,
                        f"{Doctor.VOCAB_FILE_MISSING} {vocab_file} ({exc})",
                        workspace.archive,
                    )
                )
                continue

            for value in values:
                if value != value.upper():
                    issues.append(
                        DoctorIssue(
                            DoctorText.WARNING,
                            f"{Doctor.KEYWORD_NOT_NORMALIZED} {value} ({vocab_file})",
                            workspace.archive,
                        )
                    )

    return issues


def _check_rolls(archive: Path, workspace) -> tuple[list[DoctorIssue], list[Path]]:
    issues: list[DoctorIssue] = []
    missing_rolls: list[Path] = []
    vocab = archive_vocabulary(archive)

    allowed = {
        key: {value.casefold() for value in dictionary.read()}
        for key, dictionary in vocab.items()
    }
    mandatory = DoctorText.MANDATORY_FIELDS

    for folder in find_roll_folders(archive):
        index_file = get_index_file(folder)
        if not index_file.exists():
            missing_rolls.append(folder.relative_to(archive))
            continue

        try:
            data = tomllib.loads(index_file.read_text(encoding="utf-8"))
        except Exception as exc:
            issues.append(
                DoctorIssue(
                    DoctorText.ERROR,
                    f"{Doctor.ROLL_UNREADABLE} {index_file} ({exc})",
                    archive,
                )
            )
            continue

        for key in mandatory:
            if not data.get(key):
                issues.append(
                    DoctorIssue(
                        DoctorText.ERROR,
                        f"{Doctor.REQUIRED_FIELD_MISSING} '{key}' in {index_file}",
                        archive,
                    )
                )

        film = data.get("film", "")
        camera = data.get("camera", "")
        features = data.get("features", [])
        keywords = data.get("keywords", [])

        if film and film.casefold() not in allowed["films"]:
            issues.append(
                DoctorIssue(
                    DoctorText.WARNING,
                    f"{Doctor.FILM_NOT_IN_VOCAB} {film} ({index_file})",
                    archive,
                )
            )

        if camera and camera.casefold() not in allowed["cameras"]:
            issues.append(
                DoctorIssue(
                    DoctorText.WARNING,
                    f"{Doctor.CAMERA_NOT_IN_VOCAB} {camera} ({index_file})",
                    archive,
                )
            )

        for value in features or []:
            if value.casefold() not in allowed["features"]:
                issues.append(
                    DoctorIssue(
                        DoctorText.WARNING,
                        f"{Doctor.FEATURE_NOT_IN_VOCAB} {value} ({index_file})",
                        archive,
                    )
                )

        for value in keywords or []:
            if value != value.upper():
                issues.append(
                    DoctorIssue(
                        DoctorText.WARNING,
                        f"{Doctor.KEYWORD_NOT_NORMALIZED} {value} ({index_file})",
                        archive,
                    )
                )
            if value.casefold() not in allowed["keywords"]:
                issues.append(
                    DoctorIssue(
                        DoctorText.WARNING,
                        f"{Doctor.KEYWORD_NOT_IN_VOCAB} {value} ({index_file})",
                        archive,
                    )
                )

    return issues, missing_rolls


def _check_unindexed(archive: Path) -> list[Path]:
    unindexed = find_unindexed_folders(archive)
    return [folder.relative_to(archive) for folder in unindexed]


def _check_naming(archive: Path) -> list[DoctorIssue]:
    issues: list[DoctorIssue] = []
    year_pattern = re.compile(r"^\d{4}$")
    roll_pattern = re.compile(r"^\d{2}-\d{2}$")

    for year_dir in archive.iterdir():
        if not year_dir.is_dir() or not year_pattern.match(year_dir.name):
            continue
        for roll_dir in year_dir.iterdir():
            if roll_dir.is_dir() and not roll_pattern.match(roll_dir.name):
                issues.append(
                    DoctorIssue(
                        DoctorText.WARNING,
                        f"{Doctor.SUSPICIOUS_ROLL} {roll_dir.name}",
                        archive,
                    )
                )

    return issues
