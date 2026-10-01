import re
from pathlib import Path
from time import perf_counter

import pytest

from crossbot.benchmark import grid_files, main as benchmark
from crossbot.cli import main
from crossbot.grid import InputError
from crossbot.lexicon import Lexicon
from crossbot.problem import build_problem
from crossbot.render import render
from crossbot.solvers import registry
from crossbot.solvers.api import Result, Solver
from crossbot.verify import verify


@pytest.mark.parametrize(
    "changes,defect",
    [
        ({0: "zz"}, "not in dictionary"),
        ({0: "a"}, "wrong length"),
        ({0: "cd"}, "repeated word"),
        ({0: None}, "unfilled"),
        ({9: "ab"}, "unknown slots"),
        ({0: "ac"}, "crossing mismatch"),
    ],
)
def test_independent_verifier(tiny_grid, changes, defect):
    problem = build_problem(tiny_grid, Lexicon(("ab", "ac", "bd", "cd")))
    assignment = {0: "ab", 1: "ac", 2: "bd", 3: "cd"}
    for slot, word in changes.items():
        if word is None:
            assignment.pop(slot)
        else:
            assignment[slot] = word
    assert any(defect in issue for issue in verify(problem, assignment))


def test_empty_render_and_info(tiny_file, capsys):
    assert main(["grid-info", str(tiny_file)]) == 0
    output = capsys.readouterr()
    assert output.err == ""
    assert (
        output.out
        == "┌───┬───┐\n│1  │2  │\n├───┼───┤\n│3  │   │\n└───┴───┘\ngrid 7: 2x2, density 100.00%, 3 keys, 4 words\nOK: grid is consistent\n"
    )


def test_solve_status_and_stats(tiny_file, tiny_dictionary, capsys):
    assert (
        main(
            [
                "solve",
                str(tiny_file),
                str(tiny_dictionary),
                "--seed",
                "12",
                "-w",
                "1h:AB",
            ]
        )
        == 0
    )
    output = capsys.readouterr()
    assert output.err == ""
    assert "│ A │ B │" in output.out
    assert "locked words honoured: 1h=AB" in output.out
    assert re.search(
        r"SOLVED grid 7: 4 words placed, all distinct \(solver=mac seed=12 time=\d+\.\d{2}s nodes=\d+ backtracks=\d+ revisions=\d+ restarts=\d+\)",
        output.out,
    )


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["wat"],
        ["list-solvers", "extra"],
        ["solve", "missing"],
        ["solve", "g", "d", "--timeout", "0"],
        ["solve", "g", "d", "--timeout", "nan"],
        ["solve", "g", "d", "--seed", "nope"],
        ["grid-info", "missing"],
    ],
)
def test_errors_are_single_message(args, capsys):
    assert main(args) == 1
    output = capsys.readouterr()
    assert output.out == ""
    assert output.err.startswith("error: ")
    assert output.err.count("\n") == 1


def test_list_solvers(capsys):
    assert main(["list-solvers"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert [line.split()[0] for line in lines] == ["forward", "mac"]
    assert sum("(default)" in line for line in lines) == 1


def test_numeric_recursive_file_filter(tmp_path):
    for relative in ("a/51.yaml", "b/5.yaml", "1.yaml"):
        path = tmp_path / relative
        path.parent.mkdir(exist_ok=True)
        path.touch()
    assert [p.stem for p in grid_files(tmp_path, None)] == ["1", "5", "51"]
    assert [p.stem for p in grid_files(tmp_path, [51, 5])] == ["5", "51"]
    with pytest.raises(InputError, match="not found"):
        grid_files(tmp_path, [99])
    with pytest.raises(InputError, match="does not exist"):
        grid_files(tmp_path / "missing", None)
    (tmp_path / "bad.yaml").touch()
    with pytest.raises(InputError, match="basename"):
        grid_files(tmp_path, None)


def test_benchmark_product_and_exit(tiny_file, tiny_dictionary, capsys):
    assert (
        benchmark(
            [
                "--grid-dir",
                str(tiny_file.parent),
                "--dict",
                str(tiny_dictionary),
                "--solvers",
                "forward,mac",
                "--seeds",
                "0,1,2",
            ]
        )
        == 0
    )
    output = capsys.readouterr().out
    assert output.startswith("dictionary: 4 words loaded in ")
    assert output.count("  ok") == 6
    assert output.endswith("\nall solved and verified\n")


@pytest.mark.parametrize(
    "locks,expected",
    [([], "invalid solution:"), (["1h:ab"], "internal error: locked slots")],
)
def test_untrusted_solver_output_is_not_printed(
    tiny_file, tiny_dictionary, capsys, monkeypatch, locks, expected
):
    from crossbot import cli
    from crossbot.solvers.api import Registry

    fake = Registry()
    fake.register(
        Solver(
            "fake",
            "deliberately invalid",
            lambda p, s, d: Result({0: "cd", 1: "ac", 2: "bd", 3: "cd"}, "solved", {}),
            True,
        )
    )
    monkeypatch.setattr(cli, "registry", fake)
    args = ["solve", str(tiny_file), str(tiny_dictionary)]
    for lock in locks:
        args += ["-w", lock]
    assert main(args) == 1
    output = capsys.readouterr()
    assert output.out == ""
    assert output.err.startswith(expected)


def test_benchmark_invalid_gate(tiny_file, tiny_dictionary, capsys, monkeypatch):
    import crossbot.benchmark as module
    from crossbot.solvers.api import Registry

    fake = Registry()
    fake.register(
        Solver("fake", "invalid", lambda p, s, d: Result({}, "solved", {}), True)
    )
    monkeypatch.setattr(module, "registry", fake)
    assert (
        benchmark(["--grid-dir", str(tiny_file.parent), "--dict", str(tiny_dictionary)])
        == 1
    )
    output = capsys.readouterr().out
    assert "INVALID: slot 1h is unfilled" in output
    assert "1 failures:" in output
    assert "(7, fake, 0, INVALID:" in output


def test_unsatisfiable_locks_and_timeout(tiny_file, tmp_path, capsys):
    dictionary = tmp_path / "dict"
    dictionary.write_text("ab\ncd\n")
    assert main(["solve", str(tiny_file), str(dictionary), "-w", "1h:ab"]) == 1
    assert "locked words admit no solution" in capsys.readouterr().err
    assert main(["solve", str(tiny_file), str(dictionary), "--timeout", "1e-12"]) == 1
    assert "no solution found within" in capsys.readouterr().err
