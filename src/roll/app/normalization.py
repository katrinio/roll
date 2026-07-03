from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import re
import tomllib

from roll.archive import find_roll_folders, get_index_file
from roll.messages import Normalize


@dataclass(frozen=True)
class RenameRule:
    folder: Path
    target: Path


@dataclass(frozen=True)
class NormalizationPlan:
    archive: Path
    rules: list[RenameRule]
    conflicts: list[str]

    @property
    def has_changes(self) -> bool:
        return bool(self.rules)

    @property
    def is_safe(self) -> bool:
        return not self.conflicts


class NamingStrategy:
    @staticmethod
    def build_folder_name(loaded_at: str, lab_id: str = "") -> str:
        date_part = _date_part(loaded_at)
        lab_part = _normalize_lab_id(lab_id)
        return f"{date_part}-{lab_part}" if lab_part else date_part

    @staticmethod
    def is_normalized(folder: Path, loaded_at: str, lab_id: str = "") -> bool:
        return folder.name == NamingStrategy.build_folder_name(loaded_at, lab_id)


def build_normalization_plan(archive: Path) -> NormalizationPlan:
    rules: list[RenameRule] = []
    conflicts: list[str] = []

    for folder in find_roll_folders(archive):
        index_file = get_index_file(folder)
        if not index_file.exists():
            continue

        try:
            data = tomllib.loads(index_file.read_text(encoding="utf-8"))
        except Exception:
            continue

        loaded_at = str(data.get("loaded_at", ""))
        lab_id = str(data.get("lab_id", ""))
        if not loaded_at:
            continue

        target_name = NamingStrategy.build_folder_name(loaded_at, lab_id)
        if folder.name == target_name:
            continue

        target = folder.with_name(target_name)
        rules.append(RenameRule(folder=folder, target=target))

    conflicts.extend(_detect_conflicts(rules))
    return NormalizationPlan(archive=archive, rules=rules, conflicts=conflicts)


def print_normalization_plan(plan: NormalizationPlan) -> list[str]:
    lines = [Normalize.HEADER]
    if not plan.rules:
        lines.append(Normalize.ALREADY_NORMALIZED)
        return lines

    for rule in plan.rules:
        lines.append(f"⚠ {rule.folder.relative_to(plan.archive)}")
        lines.append(f"  → {rule.target.relative_to(plan.archive)}")

    return lines


def apply_normalization_plan(plan: NormalizationPlan) -> None:
    apply_normalization_plans([plan])


def apply_normalization_plans(plans: list[NormalizationPlan]) -> None:
    if any(not plan.is_safe for plan in plans):
        raise ValueError("Normalization plan has conflicts.")

    all_rules: list[tuple[Path, Path, Path]] = []
    for plan in plans:
        for index, rule in enumerate(plan.rules):
            temp_path = rule.folder.with_name(f".normalize-{index}-{rule.folder.name}")
            all_rules.append((rule.folder, temp_path, rule.target))

    if not all_rules:
        return

    renamed_to_temp: list[tuple[Path, Path, Path]] = []
    try:
        for source, temp_path, target in sorted(all_rules, key=lambda item: len(item[0].parts), reverse=True):
            os.replace(source, temp_path)
            renamed_to_temp.append((source, temp_path, target))
        for _, temp_path, target in all_rules:
            os.replace(temp_path, target)
    except Exception:
        for source, temp_path, _ in reversed(renamed_to_temp):
            if temp_path.exists() and not source.exists():
                os.replace(temp_path, source)
        raise


def _detect_conflicts(rules: list[RenameRule]) -> list[str]:
    conflicts: list[str] = []
    targets: dict[Path, Path] = {}
    sources = {rule.folder for rule in rules}

    for rule in rules:
        if rule.target.exists() and rule.target != rule.folder:
            conflicts.append(f"Target already exists: {rule.target}")
        if rule.target in sources and rule.target != rule.folder:
            conflicts.append(f"Target collides with source: {rule.target}")
        if rule.target in targets and targets[rule.target] != rule.folder:
            conflicts.append(f"Duplicate target: {rule.target}")
        targets[rule.target] = rule.folder

    return conflicts


def _date_part(loaded_at: str) -> str:
    value = loaded_at.strip()
    if "T" in value:
        value = value.split("T", 1)[0]
    if " " in value:
        value = value.split(" ", 1)[0]

    match = re.search(r"(\d{4})[-/.](\d{2})[-/.](\d{2})", value)
    if match:
        return f"{match.group(2)}-{match.group(3)}"

    match = re.search(r"(\d{2})[-/.](\d{2})", value)
    if match:
        return f"{match.group(1)}-{match.group(2)}"

    return value.replace(".", "-").replace("/", "-")


def _normalize_lab_id(lab_id: str) -> str:
    value = lab_id.strip()
    if not value:
        return ""
    return value if value.startswith("e") else f"e{value}"

