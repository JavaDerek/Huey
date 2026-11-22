"""Offline comparison of the explicitly guarded synthetic snapshot profile."""

from __future__ import annotations

import copy
from collections.abc import Iterable
from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Any

from .files import (
    FileError,
    Snapshot,
    _finite_values,
    _load,
    _tokens,
    assumed_snapshot_9_for_synthetic_3_1_2,
)

WARNINGS = (
    "Snapshots omit read-only objects; identical means saved settings only.",
    "Synthetic snapshot.9 compatibility is assumed; actual firmware 3.1.2 compatibility "
    "is unverified.",
    "Real console files contain private information and should not be published.",
)


@dataclass(frozen=True)
class Difference:
    identifier: str
    kind: str
    before: Any = None
    after: Any = None

    def to_dict(self) -> dict:
        result = {"identifier": self.identifier, "kind": self.kind}
        if self.kind != "added":
            result["before"] = copy.deepcopy(self.before)
        if self.kind != "removed":
            result["after"] = copy.deepcopy(self.after)
        return result


@dataclass(frozen=True)
class ComparisonResult:
    status: str
    differences: tuple[Difference, ...]
    ignored_identifiers: tuple[str, ...]
    compared_count: int
    before_identity: dict[str, str]
    after_identity: dict[str, str]
    ignore: tuple[str, ...]
    ignore_patterns: tuple[str, ...]
    warnings: tuple[str, ...] = WARNINGS
    reason: str | None = None

    @property
    def ignored_count(self) -> int:
        return len(self.ignored_identifiers)

    @property
    def exit_code(self) -> int:
        return {"identical": 0, "different": 1, "not_comparable": 3}[self.status]

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "reason": self.reason,
            "compared_count": self.compared_count,
            "ignored_count": self.ignored_count,
            "before_identity": dict(self.before_identity),
            "after_identity": dict(self.after_identity),
            "ignore": list(self.ignore),
            "ignore_patterns": list(self.ignore_patterns),
            "ignored_identifiers": list(self.ignored_identifiers),
            "differences": [difference.to_dict() for difference in self.differences],
            "warnings": list(self.warnings),
        }


def _metadata(source: Path | str | Snapshot) -> Snapshot:
    """Inspect known synthetic metadata without claiming profile compatibility."""
    data = copy.deepcopy(source.data) if isinstance(source, Snapshot) else _load(source)
    if not isinstance(data, dict):
        raise FileError("Expected a snapshot object")
    _finite_values(data)
    if data.get("type") != "snapshot.9" or data.get("creator_sn") != "SYNTHETIC":
        raise FileError("Only known synthetic snapshot.9 files may be inspected")
    for key in ("creator_fw", "creator_model", "creator_name"):
        if not isinstance(data.get(key), str):
            raise FileError(f"Snapshot {key} must be a string")
    for key in ("ae_data", "ce_data", "ae_globals", "ce_globals", "scopes"):
        if not isinstance(data.get(key), dict):
            raise FileError(f"Snapshot section {key} must be an object")
    return Snapshot(data)


def _terminals(data: Any, pointer: str = "") -> dict[str, Any]:
    if isinstance(data, dict) and data:
        result = {}
        for key, value in data.items():
            if not isinstance(key, str):
                raise FileError("JSON object keys must be strings")
            token = key.replace("~", "~0").replace("/", "~1")
            result.update(_terminals(value, pointer + "/" + token))
        return result
    if isinstance(data, list) and data:
        result = {}
        for index, value in enumerate(data):
            result.update(_terminals(value, pointer + "/" + str(index)))
        return result
    if type(data) not in (str, int, float, bool, type(None), dict, list):
        raise FileError("Unsupported non-JSON value in snapshot")
    return {pointer: data}


def _strings(values: Iterable[str], label: str) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise FileError(f"{label} must be an iterable of strings, not a string")
    result = tuple(values)
    if any(not isinstance(value, str) for value in result):
        raise FileError(f"{label} must contain strings")
    return result


def _container_changes(left: Any, right: Any, pointer: str = "") -> dict[str, tuple]:
    """Retain object/array distinctions that leaf pointers alone cannot express."""
    if isinstance(left, (dict, list)) and isinstance(right, (dict, list)):
        if type(left) is not type(right):
            return {pointer: (left, right)}
        result = {}
        if isinstance(left, dict):
            for key in left.keys() & right.keys():
                token = key.replace("~", "~0").replace("/", "~1")
                result.update(_container_changes(left[key], right[key], pointer + "/" + token))
        else:
            for index in range(min(len(left), len(right))):
                result.update(
                    _container_changes(left[index], right[index], pointer + "/" + str(index))
                )
        return result
    return {}


def compare_snapshots(
    before: Path | str | Snapshot,
    after: Path | str | Snapshot,
    *,
    ignore: Iterable[str] = (),
    ignore_patterns: Iterable[str] = (),
) -> ComparisonResult:
    """Compare saved terminal identifiers without opening sockets or writing files.

    Exact ignores use JSON Pointers. Glob patterns match complete escaped
    pointers case-sensitively; '*' spans slashes. Compatibility precedes ignores.
    """
    left, right = _metadata(before), _metadata(after)
    exact = _strings(ignore, "ignore")
    patterns = _strings(ignore_patterns, "ignore_patterns")
    for pointer in exact:
        _tokens(pointer)
    warnings = WARNINGS
    if left.identity["name"] != right.identity["name"]:
        warnings += ("Snapshot creator names differ; verify the intended sources.",)
    identity = {
        "before_identity": left.identity,
        "after_identity": right.identity,
        "ignore": exact,
        "ignore_patterns": patterns,
        "warnings": warnings,
    }
    incompatible = [
        key for key in ("model", "firmware") if left.identity[key] != right.identity[key]
    ]
    if incompatible:
        return ComparisonResult(
            status="not_comparable", differences=(), ignored_identifiers=(), compared_count=0,
            reason="Files may not be comparable: different " + ", ".join(incompatible),
            **identity,
        )
    for snapshot in (left, right):
        assumed_snapshot_9_for_synthetic_3_1_2(snapshot.data)
    previous, current = _terminals(left.data), _terminals(right.data)
    for pointer, (old, new) in _container_changes(left.data, right.data).items():
        for terminals, value in ((previous, old), (current, new)):
            for descendant in list(terminals):
                if descendant.startswith(pointer + "/"):
                    del terminals[descendant]
            terminals[pointer] = value
    identifiers = sorted(previous.keys() | current.keys())
    ignored = tuple(
        pointer for pointer in identifiers
        if pointer in exact or any(fnmatchcase(pointer, pattern) for pattern in patterns)
    )
    remaining = sorted(set(identifiers) - set(ignored))
    if not remaining:
        raise FileError("Nothing left to compare after ignores")
    differences = []
    for pointer in remaining:
        if pointer not in previous:
            differences.append(Difference(pointer, "added", after=current[pointer]))
        elif pointer not in current:
            differences.append(Difference(pointer, "removed", before=previous[pointer]))
        else:
            old, new = previous[pointer], current[pointer]
            if type(old) is not type(new) or old != new:
                differences.append(Difference(pointer, "changed", old, new))
    return ComparisonResult(
        status="different" if differences else "identical",
        differences=tuple(differences), ignored_identifiers=ignored,
        compared_count=len(remaining), **identity,
    )
