from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict
from pathlib import Path
import re
import tomllib

from roll.archive import find_roll_folders, get_index_file, find_unindexed_folders
from roll.app.config import Config
from roll.app.normalization import build_normalization_plan, build_safe_rename_plan
from roll.messages import Doctor
from roll.app.vocabulary import archive_vocabulary
from roll.app.workspace import workspace_for


class DoctorText:
    ERROR = "error"
    WARNING = "warning"
    VOCAB_FILES = ("films", "cameras", "features", "keywords")
    MANDATORY_FIELDS = ("status", "film", "camera", "loaded_at")


@dataclass(frozen=True)
class DoctorIssue:
    level: str
    message: str


@dataclass(frozen=True)
class DoctorReport:
    issues: list[DoctorIssue]
    fixable: list[str]
    missing_rolls: list[Path]
    missing_roll_count: int
    unindexed_folders: list[Path]

    @property
    def has_errors(self) -> bool:
        return any(issue.level == DoctorText.ERROR for issue in self.issues)


def run_doctor(config: Config) -> DoctorReport:
    issues: list[DoctorIssue] = []
    fixable: list[str] = []
    missing_rolls: list[Path] = []
    unindexed_folders: list[Path] = []
    missing_roll_count = 0

    if not config.archives:
        issues.append(DoctorIssue(DoctorText.ERROR, Doctor.NO_ARCHIVES))
        return DoctorReport(
            issues=issues,
            fixable=fixable,
            missing_rolls=missing_rolls,
            missing_roll_count=missing_roll_count,
            unindexed_folders=unindexed_folders,
        )

    for archive in config.archives:
        archive_issues, archive_missing_rolls, archive_unindexed = _check_archive(archive)
        issues.extend(archive_issues)
        missing_rolls.extend(archive_missing_rolls)
        unindexed_folders.extend(archive_unindexed)
        missing_roll_count += len(archive_missing_rolls)
        plan = build_safe_rename_plan(archive)
        fixable.extend(
            f"{rule.folder.relative_to(archive)} -> {rule.target.relative_to(archive)}"
            for rule in plan.rules
        )

    return DoctorReport(
        issues=issues,
        fixable=fixable,
        missing_rolls=missing_rolls,
        missing_roll_count=missing_roll_count,
        unindexed_folders=unindexed_folders,
    )


def _check_archive(archive: Path) -> tuple[list[DoctorIssue], list[Path], list[Path]]:
    issues: list[DoctorIssue] = []
    missing_rolls: list[Path] = []
    unindexed_folders: list[Path] = []

    if not archive.exists():
        return [DoctorIssue(DoctorText.ERROR, f"{Doctor.ARCHIVE_MISSING} {archive}")], missing_rolls, unindexed_folders

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
        issues.append(DoctorIssue(DoctorText.ERROR, f"{Doctor.WORKSPACE_MISSING} {workspace.root}"))
        return issues

    if not workspace.vocabulary_dir.exists():
        issues.append(DoctorIssue(DoctorText.ERROR, f"{Doctor.VOCAB_DIR_MISSING} {workspace.vocabulary_dir}"))
        return issues

    for name in DoctorText.VOCAB_FILES:
        if not workspace.vocabulary_file(name).exists():
            issues.append(DoctorIssue(DoctorText.ERROR, f"{Doctor.VOCAB_FILE_MISSING} {workspace.vocabulary_file(name)}"))

    return issues


def _check_rolls(archive: Path, workspace) -> tuple[list[DoctorIssue], list[Path]]:
    issues: list[DoctorIssue] = []
    missing_rolls: list[Path] = []
    vocab = archive_vocabulary(archive)

    allowed = {key: set(dictionary.read()) for key, dictionary in vocab.items()}
    mandatory = DoctorText.MANDATORY_FIELDS

    for folder in find_roll_folders(archive):
        index_file = get_index_file(folder)
        if not index_file.exists():
            missing_rolls.append(folder.relative_to(archive))
            continue

        try:
            data = tomllib.loads(index_file.read_text(encoding="utf-8"))
        except Exception as exc:
            issues.append(DoctorIssue(DoctorText.ERROR, f"{Doctor.ROLL_UNREADABLE} {index_file} ({exc})"))
            continue

        for key in mandatory:
            if not data.get(key):
                issues.append(DoctorIssue(DoctorText.ERROR, f"{Doctor.REQUIRED_FIELD_MISSING} '{key}' in {index_file}"))

        film = data.get("film", "")
        camera = data.get("camera", "")
        features = data.get("features", [])
        keywords = data.get("keywords", [])

        if film and film not in allowed["films"]:
            issues.append(DoctorIssue(DoctorText.WARNING, f"{Doctor.FILM_NOT_IN_VOCAB} {film} ({index_file})"))

        if camera and camera not in allowed["cameras"]:
            issues.append(DoctorIssue(DoctorText.WARNING, f"{Doctor.CAMERA_NOT_IN_VOCAB} {camera} ({index_file})"))

        for value in features or []:
            if value not in allowed["features"]:
                issues.append(DoctorIssue(DoctorText.WARNING, f"{Doctor.FEATURE_NOT_IN_VOCAB} {value} ({index_file})"))

        for value in keywords or []:
            if value not in allowed["keywords"]:
                issues.append(DoctorIssue(DoctorText.WARNING, f"{Doctor.KEYWORD_NOT_IN_VOCAB} {value} ({index_file})"))

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
                issues.append(DoctorIssue(DoctorText.WARNING, f"{Doctor.SUSPICIOUS_ROLL} {roll_dir.name}"))

    return issues
