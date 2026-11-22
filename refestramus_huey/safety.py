"""Mandatory final send boundary, with separate request/reply rules (H1).

Only exact configured numeric localhost endpoints are reachable. No runtime
real-console entries exist. Caller predicates can only narrow this policy.
"""

from __future__ import annotations

import json
import logging
import re
from importlib.resources import files
from types import MappingProxyType

from .osc import MessageError, encode_read, parse_message

logger = logging.getLogger(__name__)
_POLICY = json.loads(files("refestramus_huey").joinpath("allow-list.json").read_text())
_ADDRESSES = frozenset(op["address"] for op in _POLICY["localhost_operations"])
_REPLY_TAGS = MappingProxyType(
    {
        op["address"]: op["reply_tags"]
        for op in _POLICY["localhost_operations"]
        if "reply_tags" in op
    }
)


class Refused(ValueError):
    """The mandatory transport gate refused a datagram."""


def _endpoint(endpoint: tuple[str, int]) -> None:
    if (
        len(endpoint) != 2
        or endpoint[0] != "127.0.0.1"
        or type(endpoint[1]) is not int
        or not 0 < endpoint[1] <= 65535
    ):
        raise Refused("Only numeric 127.0.0.1 endpoints are allowed")


def check_request(
    packet: bytes,
    destination: tuple[str, int],
    *,
    configured: tuple[str, int],
) -> str:
    """Validate encoded bytes and destination, never caller intent."""
    _endpoint(destination)
    if destination != configured:
        raise Refused("Destination differs from configured localhost endpoint")
    if packet == b"WING?":
        if "WING?" not in _ADDRESSES:
            raise Refused("Discovery has no allow-list entry")
        return "WING?"
    try:
        message = parse_message(packet)
    except MessageError as exc:
        raise Refused(str(exc)) from exc
    address = message.address
    canonical = address == "/?" or re.fullmatch(r"/[A-Za-z0-9]+(?:/[A-Za-z0-9]+)*", address)
    if (
        not canonical
        or address not in _ADDRESSES
        or message.tags is not None
        or message.arguments
        or packet != encode_read(address)
    ):
        raise Refused("Not an exact allow-listed canonical read")
    return address


class _Transport:
    """Internal sender. Approved responses are frozen before sockets start."""

    def __init__(self, approved: dict[bytes, bytes], restriction=None):
        self._approved = MappingProxyType(dict(approved))
        self._restriction = restriction
        self.audit: list[dict] = []

    def send_read(self, sock, packet, destination, *, configured):
        self._send(sock, packet, destination, direction="request", configured=configured)

    def send_reply(self, sock, request, packet, destination, *, origin):
        self._send(
            sock,
            packet,
            destination,
            direction="reply",
            request=request,
            origin=origin,
        )

    def _send(
        self, sock, packet, destination, *, direction, configured=None, request=None, origin=None
    ):
        audit = {"packet_hex": packet.hex(), "destination": destination, "direction": direction}
        try:
            # This block is the last code before the one socket send call.
            if direction == "request":
                check_request(packet, destination, configured=configured)
            else:
                check_request(request, origin, configured=origin)
                if destination != origin or self._approved.get(request) != packet:
                    raise Refused("Reply must match approved bytes and its originating client")
                if request == b"WING?":
                    if not packet.startswith(b"WING,"):
                        raise Refused("Malformed discovery reply")
                else:
                    reply = parse_message(packet)
                    if (
                        reply.address != parse_message(request).address
                        or not reply.arguments
                        or reply.tags != _REPLY_TAGS.get(reply.address)
                    ):
                        raise Refused("Reply address/arguments do not match an approved read")
            if self._restriction is not None and not self._restriction(packet, destination):
                raise Refused("Caller's narrower rule refused the datagram")
        except (Refused, MessageError) as exc:
            audit.update(status="refused", reason=str(exc))
            self.audit.append(audit)
            logger.warning("Refused datagram %s to %s: %s", packet.hex(), destination, exc)
            raise Refused(str(exc)) from exc
        sock.sendto(packet, destination)
        self.audit.append({**audit, "status": "sent"})
