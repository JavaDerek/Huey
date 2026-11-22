import json
import socket
import time
from pathlib import Path

import pytest

from refestramus_huey.files import FileError, load_capture, plant
from refestramus_huey.osc import encode_read, parse_message
from refestramus_huey.replayer import Replayer
from tests.test_safety import refused_packets

FIXTURES = Path(__file__).parent / "fixtures"
VENDOR = json.loads((FIXTURES / "vendor-exchanges.json").read_text())["exchanges"]
CAPTURE = FIXTURES / "synthetic-capture.json"


def exchange(client, endpoint, request):
    client.sendto(request, endpoint)
    return client.recvfrom(32768)[0]


@pytest.fixture
def client():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.settimeout(0.15)
        yield sock


def test_exact_recorded_replies_against_independent_plain_socket_client(
    client, localhost_and_independent_sender_audit
):
    with Replayer(CAPTURE) as server:
        for row in VENDOR:
            assert exchange(client, server.address, bytes.fromhex(row["request"])) == bytes.fromhex(
                row["reply"]
            )
        identity = exchange(client, server.discovery_address, b"WING?")
        assert identity == b"WING,127.0.0.1,Synthetic,wing-rack,SYNTHETIC,3.1.2"
    assert len(localhost_and_independent_sender_audit) == 4
    assert server.counters["recorded"] == 3
    assert len(server.audit) == 4
    assert not server.running


def test_assumed_snapshot_regenerates_documented_mute_fader_and_string_reads(client):
    with Replayer(FIXTURES / "synthetic.snap") as server:
        assert exchange(
            client, server.address, bytes.fromhex(VENDOR[1]["request"])
        ) == bytes.fromhex(VENDOR[1]["reply"])
        assert exchange(
            client, server.address, bytes.fromhex(VENDOR[2]["request"])
        ) == bytes.fromhex(VENDOR[2]["reply"])
        name = exchange(client, server.address, encode_read("/ch/1/name"))
        assert parse_message(name).arguments == ("Synthetic channel",)
        assert server.counters["regenerated"] == 3
        assert all(e["mode"] == "regenerated" for e in server.events if e["event"] == "scheduled")


def test_capture_plant_invalidates_recorded_value_and_regenerates_reply(client, tmp_path):
    output = tmp_path / "planted-capture.json"
    plant(CAPTURE, "/values/~1ch~11~1mute", 0, output)
    assert load_capture(output).data["values"]["/ch/1/mute"] == 0
    with Replayer(output) as server:
        reply = exchange(client, server.address, bytes.fromhex(VENDOR[2]["request"]))
        assert parse_message(reply).arguments == ("0", 0.0, 0)
        assert reply != bytes.fromhex(VENDOR[2]["reply"])
        assert server.counters["regenerated"] == 1


def test_replayer_refuses_every_unsafe_packet_without_reply_or_state_change(client):
    with Replayer(CAPTURE) as server:
        for packet in refused_packets():
            client.sendto(packet, server.address)
        with pytest.raises(socket.timeout):
            client.recvfrom(32768)
        assert server.counters["refused"] == len(list(refused_packets()))
        assert server.counters["sent"] == 0
        assert len([e for e in server.events if e["event"] == "refused"]) == len(
            list(refused_packets())
        )
        assert exchange(
            client, server.address, bytes.fromhex(VENDOR[2]["request"])
        ) == bytes.fromhex(VENDOR[2]["reply"])


def test_known_allow_listed_but_missing_snapshot_value_is_silent_and_logged(client, tmp_path):
    data = json.loads((FIXTURES / "synthetic.snap").read_text())
    del data["ae_data"]["ch"]["1"]["name"]
    file = tmp_path / "missing.snap"
    file.write_text(json.dumps(data))
    with Replayer(file) as server:
        client.sendto(encode_read("/ch/1/name"), server.address)
        with pytest.raises(socket.timeout):
            client.recvfrom(32768)
        assert server.counters["missed"] == 1


@pytest.mark.parametrize("value", [-20.5, 0.0, -2.0, -3.0])
def test_unverified_float_regeneration_stays_silent_instead_of_guessing(client, tmp_path, value):
    output = tmp_path / "fader.snap"
    plant(FIXTURES / "synthetic.snap", "/ae_data/ch/1/fdr", value, output)
    with Replayer(output) as server:
        client.sendto(encode_read("/ch/1/fdr"), server.address)
        with pytest.raises(socket.timeout):
            client.recvfrom(32768)
        assert server.counters["missed"] == 1


@pytest.mark.parametrize(
    "example",
    [
        row
        for row in json.loads((FIXTURES / "vendor-values.json").read_text())["examples"]
        if row["address"] == "/ch/1/fdr"
    ],
)
def test_numeric_reply_matches_exact_address_vendor_example(example, client, tmp_path):
    output = tmp_path / "documented-fader.snap"
    plant(FIXTURES / "synthetic.snap", "/ae_data/ch/1/fdr", example["value"], output)
    with Replayer(output) as server:
        reply = exchange(client, server.address, bytes.fromhex(VENDOR[1]["request"]))
        result = parse_message(reply)
        assert result.address == example["address"]
        assert result.tags == example["tags"]
        assert result.arguments[0] == example["display"]
        assert result.arguments[1] == pytest.approx(example["raw"], abs=1e-7)
        assert result.arguments[2] == example["value"]
        if example["exact_reply_hex"] is not None:
            assert reply.hex() == example["exact_reply_hex"]


def test_reply_delay_and_total_drop(client):
    with Replayer(CAPTURE, delay=0.04) as server:
        start = time.monotonic()
        exchange(client, server.address, bytes.fromhex(VENDOR[2]["request"]))
        assert time.monotonic() - start >= 0.035
    with Replayer(CAPTURE, drop_rate=1) as server:
        client.sendto(bytes.fromhex(VENDOR[2]["request"]), server.address)
        with pytest.raises(socket.timeout):
            client.recvfrom(32768)
        assert server.counters["dropped"] == 1
        assert server.counters["sent"] == 0


def test_first_same_address_reply_can_arrive_after_second_request(client):
    with Replayer(CAPTURE, late_every=2, late_delay=0.06) as server:
        packet = bytes.fromhex(VENDOR[2]["request"])
        start = time.monotonic()
        client.sendto(packet, server.address)
        client.sendto(packet, server.address)
        assert client.recvfrom(32768)[0] == bytes.fromhex(VENDOR[2]["reply"])
        assert time.monotonic() - start < 0.05
        assert client.recvfrom(32768)[0] == bytes.fromhex(VENDOR[2]["reply"])
        assert time.monotonic() - start >= 0.05
        assert server.counters["sent"] == 2


def test_caller_restriction_narrows_replies(client):
    with Replayer(CAPTURE, restriction=lambda *args: False) as server:
        client.sendto(bytes.fromhex(VENDOR[2]["request"]), server.address)
        with pytest.raises(socket.timeout):
            client.recvfrom(32768)
        assert server.counters["send_refused"] == 1
        assert server.audit[0]["status"] == "refused"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"host": "0.0.0.0"},
        {"host": "localhost"},
        {"delay": -1},
        {"drop_rate": 1.1},
        {"late_delay": float("nan")},
    ],
)
def test_unsafe_bind_and_invalid_options_refused_before_sockets(kwargs):
    with pytest.raises(ValueError):
        Replayer(CAPTURE, **kwargs)


@pytest.mark.parametrize(
    "key,value",
    [
        ("schema_version", 2),
        ("synthetic", False),
        ("segments", []),
        ("budget", {}),
        ("exchanges", [{}]),
    ],
)
def test_capture_schema_refused_before_serving(key, value, tmp_path):
    data = json.loads(CAPTURE.read_text())
    data[key] = value
    file = tmp_path / "bad.json"
    file.write_text(json.dumps(data))
    with pytest.raises(FileError):
        Replayer(file)


def test_no_unrecorded_assumptions_marked_as_hardware_evidence():
    capture = load_capture(CAPTURE)
    assert capture.synthetic
    assert "illustrative" in capture.data["provenance"]


def test_no_other_package_network_send_path():
    from tests.conftest import test_no_other_package_network_send_path as check

    check()


def test_constructing_public_objects_cannot_bypass_synthetic_guard():
    from refestramus_huey.files import Capture, Snapshot

    snapshot = json.loads((FIXTURES / "synthetic.snap").read_text())
    snapshot["creator_sn"] = "REAL"
    capture = json.loads(CAPTURE.read_text())
    capture["synthetic"] = False
    for source in (Snapshot(snapshot), Capture(capture)):
        with pytest.raises(FileError):
            Replayer(source)


def test_wrong_protocol_port_refused(client):
    with Replayer(CAPTURE) as server:
        client.sendto(b"WING?", server.address)
        client.sendto(encode_read("/?"), server.discovery_address)
        with pytest.raises(socket.timeout):
            client.recvfrom(32768)
        assert server.counters["refused"] == 2


def test_conflicting_recorded_replies_never_mix_segments(tmp_path):
    import copy

    data = json.loads(CAPTURE.read_text())
    changed = copy.deepcopy(data["exchanges"][2])
    changed["reply_hex"] = "2f63682f312f6d75746500002c73666900000000300000000000000000000000"
    changed["decoded"]["reply"]["arguments"] = ["0", 0.0, 0]
    data["exchanges"].append(changed)
    file = tmp_path / "conflicting.json"
    file.write_text(json.dumps(data))
    with pytest.raises(FileError, match="Ambiguous"):
        Replayer(file)


def test_seeded_fractional_loss_is_repeatable(client):
    outcomes = []
    for _ in range(2):
        with Replayer(CAPTURE, drop_rate=0.5, seed=7) as server:
            for _ in range(40):
                client.sendto(bytes.fromhex(VENDOR[2]["request"]), server.address)
            received = 0
            while True:
                try:
                    client.recvfrom(32768)
                    received += 1
                except TimeoutError:
                    break
            assert server.counters["received"] == 40
            assert server.counters["dropped"] + received == 40
            assert 5 < received < 35
            outcomes.append(received)
    assert outcomes[0] == outcomes[1]


def test_replayer_refuses_mixing_disjoint_reads_from_multiple_sittings(tmp_path):
    data = json.loads(CAPTURE.read_text())
    data["segments"].append({"id": 1, "started": "2026-11-21T01:00:00Z"})
    data["exchanges"][2]["segment"] = 1
    file = tmp_path / "multiple-sittings.json"
    file.write_text(json.dumps(data))
    assert len(load_capture(file).data["segments"]) == 2
    with pytest.raises(FileError, match="single.*segment|sitting"):
        Replayer(file)


def test_decoded_capture_bool_cannot_masquerade_as_integer(tmp_path):
    data = json.loads(CAPTURE.read_text())
    data["exchanges"][2]["decoded"]["reply"]["arguments"][2] = True
    file = tmp_path / "wrong-decoded-type.json"
    file.write_text(json.dumps(data))
    with pytest.raises(FileError, match="decoded"):
        load_capture(file)


def test_discovery_identity_refuses_ambiguous_comma_fields(tmp_path):
    data = json.loads((FIXTURES / "synthetic.snap").read_text())
    data["creator_name"] = "Synthetic,another field"
    file = tmp_path / "ambiguous.snap"
    file.write_text(json.dumps(data))
    with pytest.raises(FileError, match="identity"):
        Replayer(file)
