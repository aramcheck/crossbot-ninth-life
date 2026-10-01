from pathlib import Path

import pytest
import yaml

from crossbot.grid import Grid, GridSpec, InputError, geometry, load_grid, validate_grid
from crossbot.lexicon import LETTER_ID, Lexicon, load_dictionary
from crossbot.problem import build_problem, normalize_lock, parse_locks


def spec() -> dict:
    return {
        "id": 1,
        "dimensions": {"rows": 2, "cols": 2},
        "grid": "--\n--\n",
        "keys": [
            {"number": 1, "position": [0, 0], "directions": ["horizontal", "vertical"]},
            {"number": 2, "position": [0, 1], "directions": ["vertical"]},
            {"number": 3, "position": [1, 0], "directions": ["horizontal"]},
        ],
    }


@pytest.mark.parametrize(
    "field,value,detail",
    [
        ("grid", "--\n", "grid lines"),
        ("grid", "--\n---\n", "row 1"),
        ("grid", "--\n-?\n", "characters"),
        ("word_count", 3, "word_count"),
        ("density", 99.98, "density"),
    ],
)
def test_grid_mismatches(field, value, detail):
    data = spec()
    data[field] = value
    with pytest.raises(InputError, match=detail):
        validate_grid(GridSpec.model_validate(data))


@pytest.mark.parametrize(
    "change,detail",
    [
        ("order", "keys mismatch"),
        ("number", "keys mismatch"),
        ("direction", "keys mismatch"),
        ("missing", "keys mismatch"),
        ("duplicate", "keys mismatch"),
        ("bounds", "out of bounds"),
        ("position", "keys mismatch"),
    ],
)
def test_key_mismatches(change, detail):
    data = spec()
    keys = data["keys"]
    if change == "order":
        keys.reverse()
    elif change == "number":
        keys[0]["number"] = 2
    elif change == "direction":
        keys[0]["directions"] = ["horizontal"]
    elif change == "missing":
        keys.pop()
    elif change == "duplicate":
        keys[0]["directions"].append("horizontal")
    elif change == "bounds":
        keys[0]["position"] = [9, 0]
    elif change == "position":
        keys[1]["position"] = [1, 1]
    with pytest.raises(InputError, match=detail):
        validate_grid(GridSpec.model_validate(data))


def test_density_tolerance_and_informational_count():
    data = spec()
    data.update(density=99.99, word_count=4, stated_word_count=99)
    assert validate_grid(GridSpec.model_validate(data)).density == 100
    data["keys"][0]["directions"].reverse()
    assert len(validate_grid(GridSpec.model_validate(data)).slots) == 4


def test_blocked_key_and_numbering():
    grid = geometry(1, ("--x", "x--"))
    assert [(k.number, k.position) for k in grid.keys] == [
        (1, (0, 0)),
        (2, (0, 1)),
        (3, (1, 1)),
    ]
    data = {
        "id": 1,
        "dimensions": {"rows": 1, "cols": 2},
        "grid": "x-",
        "keys": [{"number": 1, "position": [0, 0], "directions": ["horizontal"]}],
    }
    with pytest.raises(InputError, match="blocked"):
        validate_grid(GridSpec.model_validate(data))


@pytest.mark.parametrize(
    "contents",
    [
        "[",
        "null",
        "id: nope",
        "id: 2\ndimensions: {rows: 0, cols: 1}",
        "!!python/object:os.system {}",
    ],
)
def test_bad_yaml_is_single_input_error(tmp_path, contents):
    path = tmp_path / "bad.yaml"
    path.write_text(contents)
    with pytest.raises(InputError, match=str(path)):
        load_grid(path)


def test_missing_files_and_bad_encoding(tmp_path):
    for loader in (load_grid, load_dictionary):
        with pytest.raises(InputError):
            loader(tmp_path / "missing")
        path = tmp_path / "invalid"
        path.write_bytes(b"\xff")
        with pytest.raises(InputError):
            loader(path)


def test_dictionary_preserves_order_and_does_not_strip_accents(tmp_path):
    path = tmp_path / "words"
    path.write_text(" AB \n\nÁB\nñA\na-b\nAB\nabc1\n")
    lexicon = load_dictionary(path)
    assert lexicon.words == ("ab", "ña", "ab")
    index = lexicon.index(2)
    assert index.words == ("ab", "ña")
    assert index.masks[0][LETTER_ID["ñ"]] == 2
    assert lexicon.index(2) is index


@pytest.mark.parametrize(
    "word,expected", [("NIÑO", "niño"), ("ÁÉÍÓÚÜ", "aeiouu"), ("N\u0303Á", "ña")]
)
def test_lock_normalization(word, expected):
    assert normalize_lock(word) == expected


@pytest.mark.parametrize(
    "locks,detail",
    [
        (["1:ab"], "expected"),
        (["1h:a-b"], "outside"),
        (["99h:ab"], "no key"),
        (["2h:ab"], "no word"),
        (["1h:abc"], "length 3.*length 2"),
        (["1h:ab", "1h:cd"], "twice"),
        (["1h:ab", "3h:ab"], "same word"),
        (["1h:ab", "1v:cd"], "crossing"),
    ],
)
def test_bad_locks_quote_offending_spec(tiny_grid: Grid, locks, detail):
    with pytest.raises(InputError, match=detail) as error:
        parse_locks(tiny_grid, locks)
    assert repr(locks[-1]) in str(error.value)


def test_duplicate_identical_lock_and_membership_exemption(tiny_grid):
    locks = parse_locks(tiny_grid, ["1H:XY", "1h:xy"])
    problem = build_problem(tiny_grid, Lexicon(("ab", "xa", "yb")), locks)
    assert problem.indexes[0].words == ("ab", "xa", "yb", "xy")
    assert problem.domains[0] == 8


def test_missing_length(tiny_grid):
    with pytest.raises(InputError, match="dictionary has no words of length 2"):
        build_problem(tiny_grid, Lexicon(("aaa",)))
    # A lock of that length satisfies the length check, though the fill is impossible.
    assert build_problem(tiny_grid, Lexicon(()), {0: "ab"}).domains[0] == 1


def test_all_asset_grids_validate():
    paths = sorted(Path("grids").rglob("*.yaml"))
    assert len(paths) == 88
    for path in paths:
        grid = load_grid(path)
        assert grid.slots
        for i, edges in enumerate(grid.crossings):
            for edge in edges:
                assert (
                    grid.slots[i].cells[edge.here]
                    == grid.slots[edge.other].cells[edge.there]
                )
