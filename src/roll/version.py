from __future__ import annotations

import re
from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path
import subprocess


@lru_cache(maxsize=1)
def get_version() -> str:
    git_version = _git_tag()
    if git_version:
        return git_version

    try:
        return package_version("roll")
    except PackageNotFoundError:
        pass
    return "0.0.0"


def get_latest_version() -> str:
    return _git_tag()


def is_outdated(current: str | None = None, latest: str | None = None) -> bool:
    current_version = _version_tuple(current or get_version())
    latest_version = _version_tuple(latest or get_latest_version())
    if not latest_version:
        return False
    return current_version < latest_version


def _git_tag() -> str:
    repo = _find_git_root(Path.cwd())
    if repo is None:
        repo = Path(__file__).resolve().parents[2]
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0", "--match", "v*"],
            check=True,
            capture_output=True,
            text=True,
            cwd=repo,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return result.stdout.strip().removeprefix("v")


def _find_git_root(path: Path) -> Path | None:
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def _version_tuple(value: str) -> tuple[int, ...]:
    match = re.match(r"^v?(\d+(?:\.\d+)*)", value.strip())
    if not match:
        return ()
    return tuple(int(part) for part in match.group(1).split("."))
