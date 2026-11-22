"""Hand-written Story 1 oracles; assumed synthetic 3.1.2 profile only."""

import copy
import json
import socket
from pathlib import Path

import pytest

from refestramus_huey.compare import compare_snapshots
from refestramus_huey.files import FileError, Snapshot, load_snapshot, plant

FIXTURE = Path(__file__).parent / "fixtures/synthetic.snap"


@pytest.fixture
def pair(tmp_path):
    def write(before=None, after=None):
        base = json.loads(FIXTURE.read_text())
        paths = []
        for name, updates in (("before", before), ("after", after)):
            data = copy.deepcopy(base)
            if updates is not None:
                data.update(updates)
            path = tmp_path / f"{name}.snap"
            path.write_text(json.dumps(data))
            paths.append(path)
        return paths

    return write


def entries(result):
    return result.to_dict()["differences"]


def test_assumed_identical_is_offline_pure_and_warns(pair, monkeypatch):
    before, after = pair()
    saved = [p.read_bytes() for p in (before, after)]
    files = set(before.parent.iterdir())

    def forbidden(*args, **kwargs):
        pytest.fail("Comparison must not open a socket")

    monkeypatch.setattr(socket, "socket", forbidden)
    result = compare_snapshots(before, after)
    assert result.status == "identical"
    assert result.exit_code == 0
    assert result.compared_count > 0
    assert entries(result) == []
    warnings = " ".join(result.warnings).lower()
    assert all(word in warnings for word in ("read-only", "synthetic", "unverified", "private"))
    assert [p.read_bytes() for p in (before, after)] == saved
    assert set(before.parent.iterdir()) == files


@pytest.mark.parametrize("count", [1, 2, 3])
def test_assumed_planted_changes_exactly_match_hand_written_oracle(tmp_path, count):
    changes = [
        ("/ae_data/ch/1/name", "Synthetic channel", "Changed channel"),
        ("/ae_data/ch/1/mute", 1, 0),
        ("/ae_data/ch/1/fdr", -144.0, -12.0),
    ]
    source = FIXTURE
    for index, (pointer, _, value) in enumerate(changes[:count]):
        target = tmp_path / f"planted{index}.snap"
        plant(source, pointer, value, target)
        source = target
    result = compare_snapshots(FIXTURE, source)
    assert result.status == "different"
    assert result.exit_code == 1
    expected = [
        {"identifier": p, "kind": "changed", "before": old, "after": new}
        for p, old, new in changes[:count]
    ]
    assert entries(result) == sorted(expected, key=lambda d: d["identifier"])


def test_added_removed_null_empty_containers_and_array_indices(pair):
    paths = pair(
        {"ae_data": {"removed": None, "empty": {}, "array": [1, 2]}},
        {"ae_data": {"added": None, "empty": [], "array": [1, 3, None]}},
    )
    assert entries(compare_snapshots(*paths)) == [
        {"identifier": "/ae_data/added", "kind": "added", "after": None},
        {"identifier": "/ae_data/array/1", "kind": "changed", "before": 2, "after": 3},
        {"identifier": "/ae_data/array/2", "kind": "added", "after": None},
        {"identifier": "/ae_data/empty", "kind": "changed", "before": {}, "after": []},
        {"identifier": "/ae_data/removed", "kind": "removed", "before": None},
    ]


@pytest.mark.parametrize("left,right", [(True, 1), (False, 0), ("1", 1), ({}, [])])
def test_types_do_not_collapse_under_python_equality(pair, left, right):
    paths = pair({"ae_data": {"x": left}}, {"ae_data": {"x": right}})
    result = compare_snapshots(*paths)
    assert result.status == "different"
    assert entries(result) == [
        {"identifier": "/ae_data/x", "kind": "changed", "before": left, "after": right}
    ]


def test_terminal_branch_replacement_and_pointer_escaping(pair):
    paths = pair(
        {"ae_data": {"branch": {"x": 1}, "a/b": 1, "m~n": 1, "~1": 1, "": 1}},
        {"ae_data": {"branch": None, "a/b": 2, "m~n": 2, "~1": 2, "": 2}},
    )
    assert entries(compare_snapshots(*paths)) == [
        {"identifier": "/ae_data/", "kind": "changed", "before": 1, "after": 2},
        {"identifier": "/ae_data/a~1b", "kind": "changed", "before": 1, "after": 2},
        {"identifier": "/ae_data/branch", "kind": "added", "after": None},
        {"identifier": "/ae_data/branch/x", "kind": "removed", "before": 1},
        {"identifier": "/ae_data/m~0n", "kind": "changed", "before": 1, "after": 2},
        {"identifier": "/ae_data/~01", "kind": "changed", "before": 1, "after": 2},
    ]


def test_ignore_exact_literal_and_overlapping_case_sensitive_globs(pair):
    paths = pair(
        {"ae_data": {"[ab]": 1, "a": 1, "branch": {"x": 1}, "Case": 1}},
        {"ae_data": {"[ab]": 2, "a": 1, "branch": {"x": 2}, "Case": 2}},
    )
    plain = compare_snapshots(*paths)
    result = compare_snapshots(
        *paths,
        ignore=["/ae_data/[ab]"],
        ignore_patterns=["/ae_data/branch/*", "/ae_data/a", "/ae_data/branch/x", "/ae_data/case"],
    )
    assert result.ignored_identifiers == ("/ae_data/[ab]", "/ae_data/a", "/ae_data/branch/x")
    assert result.ignored_count == 3
    assert result.compared_count == plain.compared_count - 3
    assert entries(result) == [
        {"identifier": "/ae_data/Case", "kind": "changed", "before": 1, "after": 2}
    ]
    assert result.to_dict()["ignore"] == ["/ae_data/[ab]"]
    assert result.to_dict()["ignore_patterns"][0] == "/ae_data/branch/*"


@pytest.mark.parametrize("key,value", [("creator_fw", "0.0.0"), ("creator_model", "other")])
def test_incompatibility_precedes_every_ignore_without_comparing_values(pair, key, value):
    paths = pair(None, {key: value, "ae_data": {"hidden": "changed"}})
    result = compare_snapshots(*paths, ignore_patterns=["*"])
    assert result.status == "not_comparable"
    assert result.exit_code == 3
    assert result.compared_count == result.ignored_count == 0
    assert entries(result) == []
    assert ("firmware" if key == "creator_fw" else "model") in result.reason
    assert result.before_identity != result.after_identity


@pytest.mark.parametrize("updates", [
    {"type": "snapshot.999"}, {"creator_sn": "REAL"}, {"creator_name": None},
    {"ae_data": []}, {"creator_fw": "0.0.0"}, {"creator_model": "other"},
])
def test_assumption_guard_not_widened_for_matching_invalid_profiles(pair, updates):
    with pytest.raises(FileError):
        compare_snapshots(*pair(updates, updates))


@pytest.mark.parametrize("text", [
    '{"x": 1, "x": 2}', '{"x": NaN}', '{"x": 1e999}', '[]', '{broken',
])
def test_bad_json_is_refused_before_comparison(tmp_path, text):
    bad = tmp_path / "bad.snap"
    bad.write_text(text)
    with pytest.raises(FileError):
        compare_snapshots(FIXTURE, bad)


def test_object_order_unmatched_ignores_and_snapshot_object_defensive_copy(pair):
    paths = pair()
    data = json.loads(paths[1].read_text())
    paths[1].write_text(json.dumps(dict(reversed(list(data.items()))), indent=4))
    first = load_snapshot(paths[0])
    original = copy.deepcopy(first.data)
    result = compare_snapshots(first, paths[1], ignore_patterns=["/missing/*"])
    assert result.status == "identical"
    assert result.ignored_count == 0
    result.before_identity["name"] = "mutated result"
    assert first.data == original
    invalid = Snapshot({**first.data, "creator_sn": "REAL"})
    with pytest.raises(FileError):
        compare_snapshots(invalid, first)


def test_name_difference_warned_and_still_reported(pair):
    result = compare_snapshots(*pair(None, {"creator_name": "Other synthetic"}))
    assert entries(result) == [
        {"identifier": "/creator_name", "kind": "changed",
         "before": "Synthetic", "after": "Other synthetic"}
    ]
    assert any("name" in warning.lower() for warning in result.warnings)


def test_empty_creator_name_remains_valid_under_existing_snapshot_guard(pair):
    paths = pair({"creator_name": ""}, {"creator_name": ""})
    assert load_snapshot(paths[0]).identity["name"] == ""
    assert compare_snapshots(*paths).status == "identical"


def test_nonempty_object_and_array_with_same_leaf_are_not_identical(pair):
    paths = pair({"ae_data": {"x": {"0": 1}}}, {"ae_data": {"x": [1]}})
    result = compare_snapshots(*paths)
    assert result.status == "different"
    assert entries(result) == [
        {"identifier": "/ae_data/x", "kind": "changed", "before": {"0": 1}, "after": [1]}
    ]


@pytest.mark.parametrize("kwargs", [
    {"ignore": "/ae_data/x"}, {"ignore_patterns": "*"},
    {"ignore": [1]}, {"ignore_patterns": [1]}, {"ignore": ["/~invalid"]},
])
def test_invalid_ignore_forms_refuse(kwargs):
    with pytest.raises(FileError):
        compare_snapshots(FIXTURE, FIXTURE, **kwargs)


@pytest.mark.parametrize("before,after", [(1, 1.0), (1.0, 1), (1, 2.0), (2.0, 1)])
def test_owner_approved_numeric_representation_is_different(pair, before, after):
    result = compare_snapshots(*pair({"ae_data": {"x": before}}, {"ae_data": {"x": after}}))
    assert result.status == "different"
    assert result.exit_code == 1
    assert entries(result) == [
        {"identifier": "/ae_data/x", "kind": "changed", "before": before, "after": after}
    ]
    assert type(result.differences[0].before) is type(before)
    assert type(result.differences[0].after) is type(after)


def test_owner_approved_all_ignored_refuses():
    with pytest.raises(FileError) as error:
        compare_snapshots(FIXTURE, FIXTURE, ignore_patterns=["*"])
    assert str(error.value) == "Nothing left to compare after ignores"


@pytest.mark.parametrize("value", [{1: "bad key"}, {"bad": (1, 2)}])
def test_snapshot_object_cannot_bypass_json_validation(value):
    before = load_snapshot(FIXTURE)
    invalid = Snapshot({**before.data, "ae_data": value})
    with pytest.raises(FileError):
        compare_snapshots(before, invalid)
