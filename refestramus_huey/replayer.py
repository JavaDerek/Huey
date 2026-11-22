"""Synthetic localhost stand-in; no console client or state-changing operation."""

from __future__ import annotations

import copy
import heapq
import logging
import math
import random
import select
import socket
import threading
import time
from pathlib import Path

from .files import (
    Capture,
    FileError,
    Snapshot,
    _validate_capture,
    assumed_snapshot_9_for_synthetic_3_1_2,
    load_capture,
    load_snapshot,
)
from .osc import MessageError, encode_read, encode_reply
from .safety import Refused, _Transport, check_request

logger = logging.getLogger(__name__)


def _regenerate_documented_value(address: str, value) -> bytes | None:
    """Only complete conversions pinned by manual examples; H3 remains open.

    No general fader normalisation is guessed. Arbitrary JSON numeric leaves
    are not evidence for a console display/raw/value triple.
    """
    if address == "/ch/1/name" and isinstance(value, str):
        return encode_reply(address, "s", (value,))
    if address == "/ch/1/mute" and type(value) is int and value in (0, 1):
        return encode_reply(address, "sfi", (str(value), float(value), value))
    if address == "/ch/1/fdr" and type(value) in (int, float):
        # Only this exact address's printed examples, manual pp21 and24.
        # The 0.0/-2.0/-3.0 examples are channel 2; do not relabel them.
        documented = {
            -144.0: ("-oo", 0.0),
            -1.0: ("-1.0", 0.725),
            3.0: ("3.0", 0.825),
            4.0: ("4.0", 0.85),
        }
        if value in documented:
            display, raw = documented[value]
            return encode_reply(address, "sff", (display, raw, float(value)))
    return None


def _responses(source: Snapshot | Capture) -> tuple[dict[bytes, bytes], dict[bytes, str]]:
    # Public dataclass construction and later caller mutation cannot bypass
    # the same guard that file loading applies.
    if isinstance(source, Snapshot):
        source = Snapshot(copy.deepcopy(source.data))
        assumed_snapshot_9_for_synthetic_3_1_2(source.data)
    else:
        source = Capture(copy.deepcopy(source.data))
        _validate_capture(source.data)
        if len(source.data["segments"]) != 1:
            raise FileError("Replay requires a single capture segment; never combine sittings")
    identity = source.identity
    if any("," in value or any(char in value for char in "\r\n\0") for value in identity.values()):
        raise FileError("Ambiguous discovery identity field; no escaping rule is established")
    identity_string = "WING," + ",".join(
        identity[key] for key in ("address", "name", "model", "serial", "firmware")
    )
    try:
        discovery = identity_string.encode("ascii")
        replies = {
            b"WING?": discovery,
            encode_read("/?"): encode_reply("/?", "s", (identity_string,)),
        }
        modes = dict.fromkeys(replies, "regenerated")
        if isinstance(source, Snapshot):
            channel = source.data["ae_data"].get("ch", {}).get("1", {})
            if not isinstance(channel, dict):
                raise FileError("Synthetic channel node must be an object")
            values = {"/ch/1/" + key: value for key, value in channel.items()}
            exchanges, planted = [], set()
        else:
            values = source.data.get("values", {})
            exchanges = source.data["exchanges"]
            planted = set(source.data.get("planted_addresses", []))
        for address, value in values.items():
            reply = _regenerate_documented_value(address, value)
            if reply is not None:
                request = encode_read(address)
                replies[request], modes[request] = reply, "regenerated"
        recorded: dict[bytes, bytes] = {}
        for exchange in exchanges:
            request = bytes.fromhex(exchange["request_hex"])
            try:
                address = check_request(
                    request, ("127.0.0.1", 2223), configured=("127.0.0.1", 2223)
                )
            except Refused:
                continue
            if address in planted:
                # A planted value without a complete documented conversion must
                # never fall back to the stale recorded reply.
                if _regenerate_documented_value(address, values[address]) is None:
                    replies.pop(request, None)
                    modes.pop(request, None)
                continue
            if exchange["reply_hex"] is not None:
                reply = bytes.fromhex(exchange["reply_hex"])
                if request in recorded and recorded[request] != reply:
                    raise FileError("Ambiguous recorded replies; choose a single coherent segment")
                recorded[request] = reply
        replies.update(recorded)
        modes.update(dict.fromkeys(recorded, "recorded"))
        return replies, modes
    except (UnicodeError, MessageError) as exc:
        raise FileError(f"Unsupported synthetic wire value: {exc}") from exc


class Replayer:
    """Context-managed read-only UDP server, constrained to numeric localhost.

    late_every=N delays the first reply in each N-reply group by late_delay,
    enabling later requests to receive their replies first. No reply matching
    client or actual-device acceptance is claimed by these stand-in tests.
    """

    def __init__(
        self,
        source: Snapshot | Capture | Path | str,
        *,
        host="127.0.0.1",
        port=0,
        discovery_port=0,
        delay=0.0,
        drop_rate=0.0,
        late_every=0,
        late_delay=0.0,
        seed=0,
        restriction=None,
    ):
        if host != "127.0.0.1":
            raise ValueError("Replayer binds numeric 127.0.0.1 only")
        if any(type(v) is not int or not 0 <= v <= 65535 for v in (port, discovery_port)):
            raise ValueError("Invalid UDP port")
        if (
            any(not math.isfinite(v) or v < 0 for v in (delay, drop_rate, late_delay))
            or drop_rate > 1
        ):
            raise ValueError("Invalid delay/drop/late parameters")
        if type(late_every) is not int or late_every < 0:
            raise ValueError("late_every must be a nonnegative integer")
        if not isinstance(source, (Snapshot, Capture)):
            source = (
                load_snapshot(source) if Path(source).suffix == ".snap" else load_capture(source)
            )
        self._replies, self._modes = _responses(source)
        self._transport = _Transport(self._replies, restriction=restriction)
        self._host, self._ports = host, (port, discovery_port)
        self._delay, self._drop, self._late_every, self._late_delay = (
            delay,
            drop_rate,
            late_every,
            late_delay,
        )
        self._random = random.Random(seed)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._sockets: list[socket.socket] = []
        self._queue: list[tuple] = []
        self._sequence = 0
        self._accepted = 0
        self._failure: BaseException | None = None
        self.counters = dict.fromkeys(
            (
                "received",
                "sent",
                "refused",
                "missed",
                "dropped",
                "regenerated",
                "recorded",
                "send_refused",
            ),
            0,
        )
        self.events: list[dict] = []
        self.address: tuple[str, int] | None = None
        self.discovery_address: tuple[str, int] | None = None

    @property
    def audit(self) -> tuple[dict, ...]:
        return tuple(dict(entry) for entry in self._transport.audit)

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> Replayer:
        if self.running:
            raise ValueError("Replayer is already running")
        self._stop.clear()
        try:
            for port in self._ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self._sockets.append(sock)
                sock.bind((self._host, port))
            self.address, self.discovery_address = (sock.getsockname() for sock in self._sockets)
        except OSError:
            for sock in self._sockets:
                sock.close()
            self._sockets.clear()
            raise
        self._thread = threading.Thread(
            target=self._run, name="synthetic-wing-replayer", daemon=True
        )
        self._thread.start()
        return self

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2)
            if self._thread.is_alive():
                raise RuntimeError("Replayer did not stop")
        if self._failure is not None:
            raise RuntimeError("Replayer worker failed") from self._failure

    def __enter__(self) -> Replayer:
        return self.start()

    def __exit__(self, *args) -> None:
        self.stop()

    def _event(self, event: str, packet: bytes, **values) -> None:
        record = {"event": event, "packet_hex": packet.hex(), **values}
        self.events.append(record)
        logger.info("Replayer %s", record)

    def _receive(self, sock: socket.socket) -> None:
        packet, origin = sock.recvfrom(65535)
        self.counters["received"] += 1
        try:
            if origin[0] != "127.0.0.1":
                raise Refused("Non-local source")
            if (sock is self._sockets[1]) != (packet == b"WING?"):
                raise Refused("Request sent to the wrong configured protocol port")
            check_request(packet, sock.getsockname(), configured=sock.getsockname())
        except Refused as exc:
            self.counters["refused"] += 1
            self._event("refused", packet, origin=origin, reason=str(exc))
            return
        reply = self._replies.get(packet)
        if reply is None:
            self.counters["missed"] += 1
            self._event(
                "missed",
                packet,
                origin=origin,
                reason="No recorded or documented regenerable value",
            )
            return
        self._accepted += 1
        if self._random.random() < self._drop:
            self.counters["dropped"] += 1
            self._event("dropped", packet, origin=origin)
            return
        delay = self._delay
        if self._late_every and (self._accepted - 1) % self._late_every == 0:
            delay += self._late_delay
        self._sequence += 1
        heapq.heappush(
            self._queue, (time.monotonic() + delay, self._sequence, sock, origin, packet, reply)
        )
        mode = self._modes[packet]
        self.counters[mode] += 1
        self._event(
            "scheduled", packet, origin=origin, mode=mode, reply_hex=reply.hex(), delay=delay
        )

    def _run(self) -> None:
        try:
            while not self._stop.is_set():
                now = time.monotonic()
                while self._queue and self._queue[0][0] <= now:
                    _, _, sock, origin, request, reply = heapq.heappop(self._queue)
                    try:
                        self._transport.send_reply(sock, request, reply, origin, origin=origin)
                        self.counters["sent"] += 1
                    except Refused:
                        self.counters["send_refused"] += 1
                timeout = min(0.02, max(0, self._queue[0][0] - now)) if self._queue else 0.02
                ready, _, _ = select.select(self._sockets, [], [], timeout)
                for sock in ready:
                    self._receive(sock)
        except Exception as exc:
            self._failure = exc
        finally:
            for sock in self._sockets:
                sock.close()
            self._sockets.clear()
            self._queue.clear()
