"""Native JSON file operations; no network access.

Latest-format compatibility is deliberately isolated in
assumed_snapshot_9_for_synthetic_3_1_2 (owner answer H2).
"""

from __future__ import annotations

import copy
import difflib
import hashlib
import json
import math
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .osc import parse_message


class FileError(ValueError):
    """Unusable or unverified file, identifier, or planted value."""


def _unique(pairs: list[tuple[str, Any]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise FileError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise FileError(f"Non-finite JSON number: {value}")


def _load(path: Path | str) -> dict:
    try:
        data = json.loads(
            Path(path).read_text(encoding="utf-8"),
            object_pairs_hook=_unique,
            parse_constant=_reject_constant,
        )
    except (OSError, ValueError, UnicodeError, RecursionError) as exc:
        raise FileError(f"Cannot read JSON file: {exc}") from exc
    if not isinstance(data, dict):
        raise FileError("Expected a JSON object")
    _finite_values(data)
    return data


def _finite_values(data: Any) -> None:
    pending = [data]
    while pending:
        value = pending.pop()
        if isinstance(value, float) and not math.isfinite(value):
            raise FileError("JSON numbers must be finite")
        if isinstance(value, dict):
            pending.extend(value.values())
        elif isinstance(value, list):
            pending.extend(value)


def _same_decoded(left: dict, right: dict) -> bool:
    # Python equality conflates True/1 and 1/1.0. OSC decoded evidence must
    # preserve the actual JSON types as well as values.
    return _json(left) == _json(right)


def _tokens(pointer: str) -> list[str]:
    if pointer == "":
        return []
    if not pointer.startswith("/") or re.search(r"~(?![01])", pointer):
        raise FileError("Expected an RFC 6901 JSON Pointer")
    return [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]


def _array_index(token: str) -> int:
    if not re.fullmatch(r"0|[1-9][0-9]*", token):
        raise ValueError("Invalid JSON Pointer array index")
    return int(token)


def _walk(data: Any, pointer: str = "") -> dict[str, Any]:
    if isinstance(data, dict):
        leaves: dict[str, Any] = {}
        for key, value in data.items():
            token = key.replace("~", "~0").replace("/", "~1")
            leaves.update(_walk(value, pointer + "/" + token))
        return leaves
    if isinstance(data, list):
        leaves = {}
        for index, value in enumerate(data):
            leaves.update(_walk(value, pointer + "/" + str(index)))
        return leaves
    return {pointer: data}


def _lookup(data: dict, pointer: str) -> tuple[Any, str | int]:
    tokens = _tokens(pointer)
    if not tokens:
        raise FileError("Whole-document replacement is not a scalar plant operation")
    parent: Any = data
    try:
        for token in tokens[:-1]:
            parent = parent[_array_index(token)] if isinstance(parent, list) else parent[token]
        key: str | int = _array_index(tokens[-1]) if isinstance(parent, list) else tokens[-1]
        if isinstance(key, int) and (key < 0 or str(key) != tokens[-1]):
            raise KeyError(key)
        parent[key]
        return parent, key
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        nearest = difflib.get_close_matches(pointer, _walk(data), n=3)
        raise FileError(f"Unknown identifier {pointer}; nearest: {nearest}") from exc


def assumed_snapshot_9_for_synthetic_3_1_2(data: dict) -> None:
    """Approved H2 assumption, not evidence of a real 3.1.2 file schema.

    Refuse real files and every format/model/firmware outside this explicit
    synthetic boundary. Native metadata and arbitrary JSON leaves stay intact.
    """
    _finite_values(data)
    expected = {
        "type": "snapshot.9",
        "creator_fw": "3.1.2",
        "creator_model": "wing-rack",
        "creator_sn": "SYNTHETIC",
    }
    if any(data.get(key) != value for key, value in expected.items()):
        raise FileError("Only assumed synthetic snapshot.9 / wing-rack / 3.1.2 is supported")
    if not isinstance(data.get("creator_name"), str):
        raise FileError("Missing snapshot creator_name")
    for section in ("ae_data", "ce_data", "ae_globals", "ce_globals", "scopes"):
        if not isinstance(data.get(section), dict):
            raise FileError(f"Snapshot section {section} must be an object")


@dataclass(frozen=True)
class Snapshot:
    data: dict
    synthetic: bool = True
    assumed_compatibility: bool = True

    @property
    def identity(self) -> dict[str, str]:
        return {
            "address": "127.0.0.1",
            "name": self.data["creator_name"],
            "model": self.data["creator_model"],
            "serial": self.data["creator_sn"],
            "firmware": self.data["creator_fw"],
        }

    @property
    def identifiers(self) -> tuple[str, ...]:
        return tuple(sorted(_walk(self.data)))

    def get(self, pointer: str) -> Any:
        if pointer == "":
            return copy.deepcopy(self.data)
        parent, key = _lookup(self.data, pointer)
        return copy.deepcopy(parent[key])


def load_snapshot(path: Path | str) -> Snapshot:
    data = _load(path)
    assumed_snapshot_9_for_synthetic_3_1_2(data)
    return Snapshot(data)


@dataclass(frozen=True)
class Capture:
    data: dict
    synthetic: bool = True

    @property
    def identity(self) -> dict[str, str]:
        return dict(self.data["identity"])


def _decoded(packet: bytes) -> dict:
    message = parse_message(packet)
    return {"address": message.address, "tags": message.tags, "arguments": list(message.arguments)}


def _validate_capture(data: dict) -> None:
    try:
        _finite_values(data)
        if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
            raise ValueError("Unknown capture schema_version")
        if data.get("synthetic") is not True:
            raise ValueError("Only synthetic capture fixtures are supported")
        identity = data["identity"]
        for key in ("address", "name", "model", "serial", "firmware"):
            if not isinstance(identity[key], str):
                raise ValueError("Capture identity fields must be strings")
        if (
            identity["address"] != "127.0.0.1"
            or identity["model"] != "wing-rack"
            or identity["firmware"] != "3.1.2"
            or identity["serial"] != "SYNTHETIC"
        ):
            raise ValueError("Capture must identify the synthetic localhost target")
        rate = data["budget"]["requests_per_second"]
        if type(rate) not in (int, float) or not math.isfinite(rate) or rate <= 0:
            raise ValueError("Invalid capture budget")
        if not data["segments"] or not isinstance(data["segments"], list):
            raise ValueError("Capture needs at least one segment")
        segments = set()
        for segment in data["segments"]:
            if type(segment["id"]) is not int or segment["id"] in segments:
                raise ValueError("Invalid or duplicate segment")
            segments.add(segment["id"])
            datetime.fromisoformat(segment["started"].replace("Z", "+00:00"))
        if any(not isinstance(data[key], list) for key in ("exchanges", "skipped", "failures")):
            raise ValueError("Capture collections must be lists")
        for exchange in data["exchanges"]:
            request = bytes.fromhex(exchange["request_hex"])
            if not _same_decoded(_decoded(request), exchange["decoded"]["request"]):
                raise ValueError("Recorded request decoded form disagrees with raw bytes")
            reply_hex = exchange["reply_hex"]
            if reply_hex is not None and not _same_decoded(
                _decoded(bytes.fromhex(reply_hex)), exchange["decoded"]["reply"]
            ):
                raise ValueError("Recorded reply decoded form disagrees with raw bytes")
            if exchange["segment"] not in segments:
                raise ValueError("Exchange references unknown segment")
            elapsed = exchange["elapsed_seconds"]
            if type(elapsed) not in (int, float) or not math.isfinite(elapsed) or elapsed < 0:
                raise ValueError("Invalid exchange timing")
            datetime.fromisoformat(exchange["timestamp"].replace("Z", "+00:00"))
        if not isinstance(data.get("values", {}), dict):
            raise ValueError("Capture values supplement must be an object")
        if any(not isinstance(address, str) for address in data.get("values", {})):
            raise ValueError("Capture value identifiers must be strings")
        if not isinstance(data.get("planted_addresses", []), list):
            raise ValueError("planted_addresses must be a list")
        if any(
            address not in data.get("values", {}) for address in data.get("planted_addresses", [])
        ):
            raise ValueError("Planted address has no replacement value")
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        raise FileError(f"Invalid capture: {exc}") from exc


def load_capture(path: Path | str) -> Capture:
    data = _load(path)
    _validate_capture(data)
    return Capture(data)


def _json(data: Any) -> str:
    try:
        return (
            json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
        )
    except (ValueError, TypeError) as exc:
        raise FileError(f"Invalid JSON value: {exc}") from exc


def plant(source: Path | str, pointer: str, value: Any, output: Path | str) -> Path:
    """Create a new native snapshot plus plant audit; never overwrite any file."""
    source, output = Path(source), Path(output)
    record = output.with_name(output.name + ".plant.json")
    if source.resolve() == output.resolve() or output.exists() or record.exists():
        raise FileError("Source, output and existing plant records must never be overwritten")
    data = _load(source)
    is_capture = "schema_version" in data
    if is_capture:
        _validate_capture(data)
        tokens = _tokens(pointer)
        if len(tokens) != 2 or tokens[0] != "values":
            raise FileError("Capture planting changes scalar /values leaves only")
    else:
        assumed_snapshot_9_for_synthetic_3_1_2(data)
        if pointer == "/creator_sn":
            raise FileError("Plant cannot change the required synthetic provenance marker")
    parent, key = _lookup(data, pointer)
    old = parent[key]
    if isinstance(old, (dict, list)) or type(old) is not type(value):
        raise FileError("Plant requires an existing scalar with exactly the same JSON type")
    if isinstance(value, float) and not math.isfinite(value):
        raise FileError("Plant value must be finite")
    parent[key] = value
    if is_capture:
        data["synthetic"] = True
        data["planted_addresses"] = sorted(set(data.get("planted_addresses", [])) | {tokens[1]})
    else:
        data["creator_sn"] = "SYNTHETIC"
    audit = {
        "schema_version": 1,
        "synthetic": True,
        "source": source.name,
        "output": output.name,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "changes": [{"pointer": pointer, "old": old, "new": value}],
    }
    text, audit_text = _json(data), _json(audit)
    created = False
    try:
        with output.open("x", encoding="utf-8") as handle:
            created = True
            handle.write(text)
        with record.open("x", encoding="utf-8") as handle:
            handle.write(audit_text)
    except OSError as exc:
        if created:
            output.unlink(missing_ok=True)
        raise FileError(f"Cannot create plant output: {exc}") from exc
    return output
