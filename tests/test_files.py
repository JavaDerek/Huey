import json
import socket
from pathlib import Path

import pytest

from refestramus_huey.files import FileError, load_snapshot, plant

FIXTURE = Path(__file__).parent / "fixtures/synthetic.snap"


def test_assumed_snapshot_9_compatibility_with_synthetic_3_1_2_metadata():
    snapshot = load_snapshot(FIXTURE)
    assert snapshot.synthetic
    assert snapshot.assumed_compatibility
    assert snapshot.get("/ae_data/ch/1/mute") == 1
    assert snapshot.identity["firmware"] == "3.1.2"
    assert "/ae_data/ch/1/name" in snapshot.identifiers


def test_plant_changes_existing_value_only_and_records_provenance_without_network(
    tmp_path, monkeypatch
):
    def forbidden(*args, **kwargs):
        raise AssertionError("File functions must never open sockets")

    monkeypatch.setattr(socket, "socket", forbidden)
    output = tmp_path / "planted.snap"
    plant(FIXTURE, "/ae_data/ch/1/mute", 0, output)
    original = json.loads(FIXTURE.read_text())
    expected = json.loads(FIXTURE.read_text())
    expected["ae_data"]["ch"]["1"]["mute"] = 0
    assert json.loads(output.read_text()) == expected
    assert json.loads(FIXTURE.read_text()) == original
    assert load_snapshot(output).get("/ae_data/ch/1/mute") == 0
    record = json.loads(output.with_name(output.name + ".plant.json").read_text())
    assert record["synthetic"] is True
    assert record["changes"] == [{"pointer": "/ae_data/ch/1/mute", "old": 1, "new": 0}]
    assert len(record["source_sha256"]) == 64
    assert output.read_text().endswith("\n")


@pytest.mark.parametrize("value", [True, "0", 0.0, None, {}, []])
def test_plant_refuses_wrong_json_type(value, tmp_path):
    with pytest.raises(FileError, match="type"):
        plant(FIXTURE, "/ae_data/ch/1/mute", value, tmp_path / "out.snap")


def test_unknown_pointer_suggests_near_existing_identifiers(tmp_path):
    with pytest.raises(FileError, match="/ae_data/ch/1/mute"):
        plant(FIXTURE, "/ae_data/ch/1/mut", 0, tmp_path / "out.snap")


def test_input_output_and_existing_record_never_overwritten(tmp_path):
    with pytest.raises(FileError):
        plant(FIXTURE, "/ae_data/ch/1/mute", 0, FIXTURE)
    output = tmp_path / "out.snap"
    output.write_text("existing")
    with pytest.raises(FileError):
        plant(FIXTURE, "/ae_data/ch/1/mute", 0, output)
    assert output.read_text() == "existing"
    output.unlink()
    record = output.with_name(output.name + ".plant.json")
    record.write_text("existing record")
    with pytest.raises(FileError):
        plant(FIXTURE, "/ae_data/ch/1/mute", 0, output)
    assert not output.exists()
    assert record.read_text() == "existing record"


@pytest.mark.parametrize(
    "field,value",
    [
        ("type", "snapshot.999"),
        ("creator_fw", "3.0.6"),
        ("creator_model", "unknown"),
        ("creator_sn", "REAL"),
        ("ae_data", []),
    ],
)
def test_unverified_versions_models_real_files_and_bad_shapes_refused(field, value, tmp_path):
    data = json.loads(FIXTURE.read_text())
    data[field] = value
    file = tmp_path / "bad.snap"
    file.write_text(json.dumps(data))
    with pytest.raises(FileError):
        load_snapshot(file)


@pytest.mark.parametrize("text", ["[]", "{}", "not JSON", '{"a":1,"a":2}', '{"a":NaN}'])
def test_bad_json_and_duplicate_keys_refused(text, tmp_path):
    file = tmp_path / "bad.snap"
    file.write_text(text)
    with pytest.raises(FileError):
        load_snapshot(file)


def test_json_pointer_uses_rfc6901_escapes_and_rejects_bad_escape(tmp_path):
    data = json.loads(FIXTURE.read_text())
    data["ae_data"]["with/slash~"] = {"name": "synthetic"}
    path = tmp_path / "escaped.snap"
    path.write_text(json.dumps(data))
    snapshot = load_snapshot(path)
    assert snapshot.get("/ae_data/with~1slash~0/name") == "synthetic"
    with pytest.raises(FileError):
        snapshot.get("/ae_data/with~2slash/name")


def test_every_snapshot_fixture_is_marked_synthetic():
    for file in FIXTURE.parent.glob("*.snap"):
        assert json.loads(file.read_text())["creator_sn"] == "SYNTHETIC"


def test_every_json_fixture_is_explicitly_marked_synthetic():
    for file in FIXTURE.parent.glob("*.json"):
        data = json.loads(file.read_text())
        assert data.get("synthetic") is True, f"Missing synthetic provenance: {file.name}"
        if "identity" in data:
            assert data["identity"]["serial"] == "SYNTHETIC"


@pytest.mark.parametrize("token", ["-1", "00", "+0", "1.0", "-"])
def test_json_pointer_array_indices_do_not_accept_nonstandard_forms(token, tmp_path):
    data = json.loads(FIXTURE.read_text())
    data["ae_data"]["test_array"] = [{"name": "synthetic"}]
    path = tmp_path / "array.snap"
    path.write_text(json.dumps(data))
    with pytest.raises(FileError):
        load_snapshot(path).get(f"/ae_data/test_array/{token}/name")


def test_json_pointer_root_and_array_item_reads(tmp_path):
    data = json.loads(FIXTURE.read_text())
    data["ae_data"]["test_array"] = ["synthetic"]
    path = tmp_path / "array.snap"
    path.write_text(json.dumps(data))
    snapshot = load_snapshot(path)
    assert snapshot.get("") == data
    assert snapshot.get("/ae_data/test_array/0") == "synthetic"


def test_json_exponent_overflow_is_refused_instead_of_loading_infinity(tmp_path):
    text = FIXTURE.read_text().replace('"fdr": -144.0', '"fdr": 1e999')
    file = tmp_path / "overflow.snap"
    file.write_text(text)
    with pytest.raises(FileError, match="finite"):
        load_snapshot(file)


def test_plant_cannot_claim_to_change_the_required_synthetic_marker(tmp_path):
    output = tmp_path / "out.snap"
    with pytest.raises(FileError, match="synthetic"):
        plant(FIXTURE, "/creator_sn", "REAL", output)
    assert not output.exists()
