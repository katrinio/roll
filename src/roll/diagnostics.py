from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import tomllib

from roll.archive import find_roll_folders, find_unindexed_folders, get_index_file
from roll.config import Config
from roll.vocabulary import archive_vocabulary
from roll.workspace import workspace_for


@dataclass(frozen=True)
class DoctorIssue:
    level: str
    message: str


@dataclass(frozen=True)
class DoctorReport:
    issues: list[DoctorIssue]

    @property
    def has_errors(self) -> bool:
        return any(issue.level == "error" for issue in self.issues)


def run_doctor(config: Config) -> DoctorReport:
    issues: list[DoctorIssue] = []

    if not config.archives:
        issues.append(DoctorIssue("error", "Global config does not contain any archives."))
        return DoctorReport(issues=issues)

    for archive in config.archives:
        issues.extend(_check_archive(archive))

    return DoctorReport(issues=issues)


def _check_archive(archive: Path) -> list[DoctorIssue]:
    issues: list[DoctorIssue] = []

    if not archive.exists():
        return [DoctorIssue("error", f"Archive does not exist: {archive}")]

    workspace = workspace_for(archive)
    issues.extend(_check_workspace(workspace))
    issues.extend(_check_rolls(archive, workspace))
    issues.extend(_check_unindexed(archive))
    issues.extend(_check_naming(archive))

    return issues


def _check_workspace(workspace) -> list[DoctorIssue]:
    issues: list[DoctorIssue] = []

    if not workspace.root.exists():
        issues.append(DoctorIssue("error", f"Missing workspace directory: {workspace.root}"))
        return issues

    if not workspace.vocabulary_dir.exists():
        issues.append(DoctorIssue("error", f"Missing vocabulary directory: {workspace.vocabulary_dir}"))
        return issues

    for name in ("films", "cameras", "features", "keywords"):
        if not workspace.vocabulary_file(name).exists():
            issues.append(DoctorIssue("error", f"Missing vocabulary file: {workspace.vocabulary_file(name)}"))

    return issues


def _check_rolls(archive: Path, workspace) -> list[DoctorIssue]:
    issues: list[DoctorIssue] = []
    vocab = archive_vocabulary(archive)

    allowed = {key: set(dictionary.read()) for key, dictionary in vocab.items()}
    mandatory = ("film", "camera", "loaded_at")

    for folder in find_roll_folders(archive):
        index_file = get_index_file(folder)
        if not index_file.exists():
            issues.append(DoctorIssue("error", f"Missing roll.toml: {index_file}. Not indexed?"))
            continue

        try:
            data = tomllib.loads(index_file.read_text(encoding="utf-8"))
        except Exception as exc:
            issues.append(DoctorIssue("error", f"Unreadable roll.toml: {index_file} ({exc})"))
            continue

        for key in mandatory:
            if not data.get(key):
                issues.append(DoctorIssue("error", f"Missing required field '{key}' in {index_file}"))

        film = data.get("film", "")
        camera = data.get("camera", "")
        features = data.get("features", [])
        keywords = data.get("keywords", [])

        if film and film not in allowed["films"]:
            issues.append(DoctorIssue("warning", f"Film is not in vocabulary: {film} ({index_file})"))

        if camera and camera not in allowed["cameras"]:
            issues.append(DoctorIssue("warning", f"Camera is not in vocabulary: {camera} ({index_file})"))

        for value in features or []:
            if value not in allowed["features"]:
                issues.append(DoctorIssue("warning", f"Feature is not in vocabulary: {value} ({index_file})"))

        for value in keywords or []:
            if value not in allowed["keywords"]:
                issues.append(DoctorIssue("warning", f"Keyword is not in vocabulary: {value} ({index_file})"))

    return issues


def _check_unindexed(archive: Path) -> list[DoctorIssue]:
    unindexed = find_unindexed_folders(archive)
    if not unindexed:
        return []
    return [DoctorIssue("warning", f"Unindexed folders: {len(unindexed)}")]


def _check_naming(archive: Path) -> list[DoctorIssue]:
    issues: list[DoctorIssue] = []
    year_pattern = re.compile(r"^\d{4}$")
    roll_pattern = re.compile(r"^e\d+$", re.IGNORECASE)

    for year_dir in archive.iterdir():
        if not year_dir.is_dir():
            continue
        if not year_pattern.match(year_dir.name):
            issues.append(DoctorIssue("warning", f"Suspicious year folder name: {year_dir.name}"))
        for roll_dir in year_dir.iterdir():
            if roll_dir.is_dir() and not roll_pattern.match(roll_dir.name):
                issues.append(DoctorIssue("warning", f"Suspicious roll folder name: {roll_dir.name}"))

    return issues
