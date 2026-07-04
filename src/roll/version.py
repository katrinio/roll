from __future__ import annotations

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


def _git_tag() -> str:
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0", "--match", "v*"],
            check=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).resolve().parents[2],
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return result.stdout.strip().removeprefix("v")
