import json
from pathlib import Path

import pytest

from refestramus_huey.osc import encode_read, encode_reply
from refestramus_huey.safety import Refused, _Transport, check_request

INDEPENDENT = json.loads((Path(__file__).parent / "independent-operations.json").read_text())
DESTINATION = ("127.0.0.1", 24000)


class Sender:
    def __init__(self):
        self.sent = []

    def sendto(self, packet, destination):
        self.sent.append((packet, destination))
        return len(packet)


def refused_packets():
    for address in INDEPENDENT["subscription_addresses"]:
        yield encode_read(address)
        yield encode_read(address) + b",\0\0\0"
        yield encode_reply(address, "i", (1,))
        yield encode_read("/%24000" + address)
    for argument in "*?#":
        yield encode_reply("/ch/1/name", "s", (argument,))
    yield b"#bundle\0" + bytes(16)
    yield encode_reply("/ch/1/mute", "i", (-1,))
    yield encode_read("/ch//1/mute")
    yield encode_read("/ch/01/mute")
    yield encode_read("/ch/1/mute/")
    yield encode_read("/CH/1/mute")
    yield encode_read("/#f50f69f8")
    yield encode_read("/%24000/ch/1/mute")
    yield encode_read("/unknown")
    yield b"/ch/1/mute\0\0\0\0\0\0"
    yield b"WING?\0"


@pytest.mark.parametrize("packet", list(refused_packets()))
def test_gate_refuses_all_unsafe_forms_even_with_permissive_extra_restriction(packet):
    sock = Sender()
    transport = _Transport({}, restriction=lambda *args: True)
    with pytest.raises(Refused):
        transport.send_read(sock, packet, DESTINATION, configured=DESTINATION)
    assert sock.sent == []
    assert transport.audit[-1]["packet_hex"] == packet.hex()
    assert transport.audit[-1]["status"] == "refused"


@pytest.mark.parametrize(
    "destination",
    [("192.0.2.1", 24000), ("localhost", 24000), ("0.0.0.0", 24000), ("127.0.0.1", 24001)],
)
def test_wrong_destination_or_non_numeric_loopback_refused(destination):
    with pytest.raises(Refused):
        check_request(encode_read("/ch/1/mute"), destination, configured=DESTINATION)


def test_builtin_gate_cannot_be_widened_and_extra_rule_can_only_narrow():
    packet = encode_read("/ch/1/mute")
    sock = Sender()
    transport = _Transport({}, restriction=lambda *args: False)
    with pytest.raises(Refused):
        transport.send_read(sock, packet, DESTINATION, configured=DESTINATION)
    assert not sock.sent
    allowed = _Transport({})
    allowed.send_read(sock, packet, DESTINATION, configured=DESTINATION)
    assert sock.sent == [(packet, DESTINATION)]


def test_reply_has_separate_rule_but_exact_source_destination_and_payload():
    request = encode_read("/ch/1/mute")
    reply = encode_reply("/ch/1/mute", "sfi", ("1", 1.0, 1))
    transport = _Transport({request: reply})
    sock = Sender()
    transport.send_reply(sock, request, reply, DESTINATION, origin=DESTINATION)
    assert sock.sent == [(reply, DESTINATION)]
    for data, destination in [
        (reply, ("127.0.0.1", 24001)),
        (encode_reply("/ch/1/mute", "i", (0,)), DESTINATION),
    ]:
        with pytest.raises(Refused):
            transport.send_reply(sock, request, data, destination, origin=DESTINATION)
    assert len(sock.sent) == 1


def test_runtime_real_allow_list_is_empty():
    policy = json.loads(
        (Path(__file__).parents[1] / "refestramus_huey/allow-list.json").read_text()
    )
    assert policy["real_operations"] == INDEPENDENT["real_operations"] == []
    assert set(
        op["address"] for op in policy["localhost_operations"] if op["operation"] != "discovery"
    ) == set(INDEPENDENT["request_addresses"])


@pytest.mark.parametrize(
    "address,tags,arguments",
    [
        ("/ch/1/mute", "s", ("1",)),
        ("/ch/1/fdr", "sfi", ("0.0", 0.75, 0)),
        ("/ch/1/name", "sff", ("Synthetic", 0.0, 0.0)),
    ],
)
def test_reply_must_match_documented_shape_even_if_recorded_bytes_are_approved(
    address, tags, arguments
):
    request = encode_read(address)
    reply = encode_reply(address, tags, arguments)
    transport = _Transport({request: reply})
    sock = Sender()
    with pytest.raises(Refused, match="reply|Reply"):
        transport.send_reply(sock, request, reply, DESTINATION, origin=DESTINATION)
    assert not sock.sent


def test_discovery_is_not_a_policy_bypass(monkeypatch):
    import refestramus_huey.safety as safety

    monkeypatch.setattr(safety, "_ADDRESSES", frozenset())
    with pytest.raises(Refused):
        safety.check_request(b"WING?", DESTINATION, configured=DESTINATION)
