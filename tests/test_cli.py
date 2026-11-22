import json
from pathlib import Path

from refestramus_huey import Replayer, load_capture, load_snapshot, plant
from refestramus_huey.cli import main

FIXTURE = Path(__file__).parent / "fixtures/synthetic.snap"


def test_importable_public_file_and_replayer_api():
    assert load_snapshot(FIXTURE).synthetic
    assert callable(load_capture)
    assert callable(plant)
    assert Replayer is not None


def test_inspect_prints_assumption_and_privacy(capsys):
    assert main(["inspect", str(FIXTURE)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["synthetic"] is True
    assert output["assumed_compatibility"] is True
    assert "private" in output["warning"].lower()


def test_cli_plant_then_inspect_pointer(tmp_path, capsys):
    path = tmp_path / "planted.snap"
    assert main(["plant", str(FIXTURE), "/ae_data/ch/1/mute", "0", str(path)]) == 0
    capsys.readouterr()
    assert main(["inspect", str(path), "--pointer", "/ae_data/ch/1/mute"]) == 0
    assert json.loads(capsys.readouterr().out)["value"] == 0


def test_cli_refuses_bad_file_value_or_network_bind(tmp_path):
    assert main(["inspect", str(tmp_path / "missing.snap")]) == 6
    assert (
        main(["plant", str(FIXTURE), "/ae_data/ch/1/mute", "true", str(tmp_path / "out.snap")]) == 6
    )
    assert main(["replay", str(FIXTURE), "--host", "0.0.0.0", "--duration", "0.01"]) == 6


def test_replay_cli_starts_on_localhost_and_stops_cleanly(capsys):
    assert main(["replay", str(FIXTURE), "--duration", "0.03"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["osc"][0] == output["discovery"][0] == "127.0.0.1"
    assert output["osc"][1] != output["discovery"][1]


def test_cli_has_no_real_console_command():
    import pytest

    for command in ("discover", "read", "record", "restore", "recall", "set"):
        with pytest.raises(SystemExit) as exc:
            main([command])
        assert exc.value.code == 2


def test_compare_cli_statuses_ignores_and_public_api(tmp_path, capsys):
    from refestramus_huey import ComparisonResult, Difference, compare_snapshots

    assert isinstance(compare_snapshots(FIXTURE, FIXTURE), ComparisonResult)
    assert Difference is not None
    assert main(["compare", str(FIXTURE), str(FIXTURE)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "identical"
    changed = tmp_path / "changed.snap"
    plant(FIXTURE, "/ae_data/ch/1/mute", 0, changed)
    assert main(["compare", str(FIXTURE), str(changed)]) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "different"
    assert main([
        "compare", str(FIXTURE), str(changed), "--ignore", "/ae_data/ch/1/mute",
        "--ignore-pattern", "/missing/*",
    ]) == 0
    assert json.loads(capsys.readouterr().out)["ignored_count"] == 1
    data = json.loads(changed.read_text())
    data["creator_fw"] = "0.0.0"
    changed.write_text(json.dumps(data))
    assert main(["compare", str(FIXTURE), str(changed), "--ignore-pattern", "*"]) == 3
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "not_comparable"
    assert output["differences"] == []
    assert main(["compare", str(FIXTURE), str(tmp_path / "missing.snap")]) == 6


def test_compare_cli_approved_numeric_and_all_ignored_rules(tmp_path, capsys, caplog):
    after = tmp_path / "numeric.snap"
    data = json.loads(FIXTURE.read_text())
    data["ae_data"]["ch"]["1"]["mute"] = 1.0
    after.write_text(json.dumps(data))
    assert main(["compare", str(FIXTURE), str(after)]) == 1
    output = json.loads(capsys.readouterr().out)
    assert output["differences"] == [
        {"identifier": "/ae_data/ch/1/mute", "kind": "changed", "before": 1, "after": 1.0}
    ]
    assert main(["compare", str(FIXTURE), str(after), "--ignore-pattern", "*"]) == 6
    assert capsys.readouterr().out == ""
    assert "Nothing left to compare after ignores" in caplog.text
    assert "pending" not in caplog.text
