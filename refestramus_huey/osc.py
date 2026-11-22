"""Small strict OSC codec; wire examples pinned to the WING 3.1 manual.

No networking. Reads omit the type tag entirely, as the manual pp20–21 shows.
Only string/int32/float32 reply forms needed for released fixtures are supported.
"""

from __future__ import annotations

import math
import struct
from dataclasses import dataclass


class MessageError(ValueError):
    """Malformed or unsupported OSC message."""


@dataclass(frozen=True)
class Message:
    address: str
    tags: str | None
    arguments: tuple[str | int | float, ...]


def _string(value: str) -> bytes:
    try:
        raw = value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise MessageError("The documented WING wire strings are ASCII") from exc
    if b"\0" in raw:
        raise MessageError("Embedded NULL in OSC string")
    return raw + b"\0" * (4 - len(raw) % 4)


def _read_string(data: bytes, offset: int) -> tuple[str, int]:
    end = data.find(b"\0", offset)
    if end < 0:
        raise MessageError("Unterminated OSC string")
    next_offset = (end + 4) // 4 * 4
    if next_offset > len(data) or any(data[end:next_offset]):
        raise MessageError("Nonzero or missing OSC padding")
    try:
        return data[offset:end].decode("ascii"), next_offset
    except UnicodeDecodeError as exc:
        raise MessageError("Non-ASCII OSC string") from exc


def encode_read(address: str) -> bytes:
    if not address.startswith("/"):
        raise MessageError("OSC address must start with /")
    return _string(address)


def encode_reply(address: str, tags: str, arguments: tuple) -> bytes:
    if len(tags) != len(arguments):
        raise MessageError("Type tag and argument lengths differ")
    data = encode_read(address) + _string("," + tags)
    try:
        for tag, value in zip(tags, arguments, strict=True):
            if tag == "s" and isinstance(value, str):
                data += _string(value)
            elif tag == "i" and type(value) is int:
                data += struct.pack(">i", value)
            elif tag == "f" and type(value) in (int, float) and math.isfinite(value):
                data += struct.pack(">f", value)
            else:
                raise MessageError("Unsupported OSC argument or type")
    except (struct.error, OverflowError) as exc:
        raise MessageError("OSC argument out of range") from exc
    return data


def parse_message(data: bytes) -> Message:
    if not data or len(data) % 4 or len(data) > 32768 or data.startswith(b"#bundle"):
        raise MessageError("Invalid OSC packet size or bundle")
    address, offset = _read_string(data, 0)
    if not address.startswith("/"):
        raise MessageError("Invalid OSC address")
    if offset == len(data):
        return Message(address, None, ())
    tags, offset = _read_string(data, offset)
    if not tags.startswith(","):
        raise MessageError("Missing OSC type tag")
    arguments: list[str | int | float] = []
    for tag in tags[1:]:
        if tag == "s":
            value, offset = _read_string(data, offset)
        elif tag in ("i", "f"):
            if offset + 4 > len(data):
                raise MessageError("Truncated OSC number")
            value = struct.unpack(">" + tag, data[offset : offset + 4])[0]
            if isinstance(value, float) and not math.isfinite(value):
                raise MessageError("Non-finite OSC number")
            offset += 4
        else:
            raise MessageError("Unsupported OSC type tag")
        arguments.append(value)
    if offset != len(data):
        raise MessageError("Trailing OSC data")
    return Message(address, tags[1:], tuple(arguments))
