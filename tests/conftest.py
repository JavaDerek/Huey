"""Deny non-local networking and count actual package datagrams below its gate."""

import ast
import inspect
import json
import socket
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def localhost_and_independent_sender_audit(monkeypatch):
    from refestramus_huey.osc import parse_message

    inventory = json.loads((Path(__file__).parent / "independent-operations.json").read_text())
    original = socket.socket
    sent = []
    received = set()

    class AuditedSocket(original):
        def bind(self, address):
            assert address[0] == "127.0.0.1", f"Non-local bind: {address}"
            return super().bind(address)

        def connect(self, address):
            assert address[0] == "127.0.0.1", f"Non-local connection: {address}"
            return super().connect(address)

        def recvfrom(self, *args):
            data, source = super().recvfrom(*args)
            received.add((self.fileno(), bytes(data), source))
            return data, source

        def sendto(self, data, *args):
            destination = args[-1]
            assert destination[0] == "127.0.0.1", f"Non-local datagram: {destination}"
            caller = inspect.currentframe().f_back.f_globals.get("__name__", "")
            if caller.startswith("refestramus_huey"):
                assert caller == "refestramus_huey.safety", "Network path outside final gate"
                request = (
                    b"WING?"
                    if data.startswith(b"WING,")
                    else (parse_message(data).address.encode("ascii"))
                )
                if request != b"WING?":
                    request += b"\0" * (4 - len(request) % 4)
                assert (self.fileno(), request, destination) in received, (
                    "Reply has no corresponding request from that originating client"
                )
                sent.append((bytes(data), destination))
            return super().sendto(data, *args)

    monkeypatch.setattr(socket, "socket", AuditedSocket)
    yield sent
    for data, destination in sent:
        assert destination[0] == inventory["destination_ip"]
        if data.startswith(b"WING,"):
            assert data == inventory["discovery_reply"].encode("ascii")
            continue
        if data == bytes.fromhex(inventory["discovery_request"]):
            continue
        decoded = parse_message(data)
        assert decoded.address in inventory["request_addresses"]
        assert decoded.tags == inventory["reply_tags"][decoded.address]


def test_no_other_package_network_send_path():
    root = Path(__file__).parents[1] / "refestramus_huey"
    sends = []
    for file in root.glob("*.py"):
        for node in ast.walk(ast.parse(file.read_text())):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in {"sendto", "sendall", "send", "connect", "create_connection"}
            ):
                sends.append((file.name, node.func.attr))
    assert sends == [("safety.py", "sendto")]
