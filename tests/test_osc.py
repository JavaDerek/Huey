import json
from pathlib import Path

import pytest

from refestramus_huey.osc import MessageError, encode_read, encode_reply, parse_message

FIXTURES = json.loads((Path(__file__).parent / "fixtures/vendor-exchanges.json").read_text())


@pytest.mark.parametrize("exchange", FIXTURES["exchanges"])
def test_vendor_examples_in_both_directions(exchange):
    request = bytes.fromhex(exchange["request"])
    assert encode_read(exchange["address"]) == request
    assert parse_message(request).arguments == ()
    reply = bytes.fromhex(exchange["reply"])
    decoded = parse_message(reply)
    assert encode_reply(decoded.address, decoded.tags, decoded.arguments) == reply


def test_exact_vendor_decoded_fader_mute_values():
    fader = parse_message(bytes.fromhex(FIXTURES["exchanges"][1]["reply"]))
    mute = parse_message(bytes.fromhex(FIXTURES["exchanges"][2]["reply"]))
    assert (fader.tags, fader.arguments) == ("sff", ("-oo", 0.0, -144.0))
    assert (mute.tags, mute.arguments) == ("sfi", ("1", 1.0, 1))


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"bad",
        b"#bundle\0",
        b"/ch/1/mute\0\0bad!",
        b"/x\0\xff",
        b"/x\0\0,s\0\0",
        b"/x\0\0,i\0\0\0",
        b"/x\0\0,T\0\0",
        b"/x\0\0\0\0\0\0",
    ],
)
def test_malformed_unsupported_or_nonzero_padding_refused(data):
    with pytest.raises(MessageError):
        parse_message(data)


def test_empty_tag_distinguished_from_absent_tag():
    assert parse_message(b"/?\0\0").tags is None
    assert parse_message(b"/?\0\0,\0\0\0").tags == ""
