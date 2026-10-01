import itertools
import random
from dataclasses import replace
from time import perf_counter

import pytest

from crossbot.grid import geometry
from crossbot.lexicon import Lexicon, WordIndex
from crossbot.problem import build_problem, parse_locks
from crossbot.solvers import registry
from crossbot.solvers.api import Registry, Solver
from crossbot.solvers.propagation import Domains
from crossbot.solvers.search import Features, solve
from crossbot.verify import verify


@pytest.mark.parametrize("name", [s.name for s in registry.all()])
def test_tiny_fill(tiny_grid, name):
    problem = build_problem(tiny_grid, Lexicon(("ab", "cd", "ac", "bd")))
    result = registry.get(name).solve(problem, 0, perf_counter() + 1)
    assert result.reason == "solved"
    assert result.assignment is not None
    assert not verify(problem, result.assignment)
    again = registry.get(name).solve(problem, 0, perf_counter() + 1)
    assert result == again


@pytest.mark.parametrize(
    "word,words", [("xy", ("ab", "xa", "yb")), ("ña", ("bc", "ñb", "ac"))]
)
def test_external_locked_words_and_enye(tiny_grid, word, words):
    problem = build_problem(
        tiny_grid, Lexicon(words), parse_locks(tiny_grid, [f"1h:{word}"])
    )
    result = solve(problem, 0, perf_counter() + 1)
    assert result.assignment is not None
    assert result.assignment[0] == word
    assert not verify(problem, result.assignment)


def test_exhaustive_unsatisfiability(tiny_grid):
    problem = build_problem(tiny_grid, Lexicon(("ab", "cd")))
    result = solve(problem, 0, perf_counter() + 1)
    assert result.reason == "unsatisfiable"
    assert result.assignment is None


def oracle(words):
    for ab, ac, bd, cd in itertools.permutations(words, 4):
        if ab[0] == ac[0] and ab[1] == bd[0] and cd[0] == ac[1] and cd[1] == bd[1]:
            return True
    return False


@pytest.mark.parametrize("seed", range(30))
def test_against_exhaustive_independent_oracle(tiny_grid, seed):
    rng = random.Random(seed)
    alphabet = "abñ"
    words = rng.sample(
        [a + b for a in alphabet for b in alphabet], rng.randrange(1, 10)
    )
    problem = build_problem(tiny_grid, Lexicon(tuple(words)))
    for solver in registry.all():
        result = solver.solve(problem, seed, perf_counter() + 1)
        assert (result.assignment is not None) == oracle(words)
        if result.assignment is not None:
            assert not verify(problem, result.assignment)


@pytest.mark.parametrize(
    "feature",
    ["arc_consistency", "value_ordering", "restarts", "degree", "support_cache"],
)
def test_isolated_feature_toggles_preserve_correctness(tiny_grid, feature):
    problem = build_problem(tiny_grid, Lexicon(("ab", "cd", "ac", "bd")))
    result = solve(
        problem, 2, perf_counter() + 1, replace(Features(), **{feature: False})
    )
    assert result.assignment is not None
    assert not verify(problem, result.assignment)


def test_restarts_do_not_mean_unsatisfiable(tiny_grid):
    problem = build_problem(
        tiny_grid, Lexicon(tuple(a + b for a in "abc" for b in "abc"))
    )
    result = solve(problem, 0, perf_counter() + 1, Features(restart_nodes=1))
    assert result.assignment is not None
    assert result.stats["restarts"] > 0


def test_expired_deadline_has_stable_stats(tiny_grid):
    problem = build_problem(tiny_grid, Lexicon(("ab", "cd", "ac", "bd")))
    expired = solve(problem, 0, perf_counter() - 1)
    solved = solve(problem, 0, perf_counter() + 1)
    assert expired.reason == "timeout"
    assert expired.assignment is None
    assert expired.stats.keys() == solved.stats.keys()
    assert expired.stats["nodes"] == 0


def test_very_short_budget_is_cooperative():
    words = tuple("".join(chars) for chars in itertools.product("abc", repeat=3))
    problem = build_problem(geometry(1, ("---",) * 3), Lexicon(words))
    start = perf_counter()
    result = solve(problem, 0, start + 0.00001)
    assert perf_counter() - start < 0.05
    assert result.reason == "timeout"


def test_isolated_open_cell_and_all_blocked_grid():
    for pattern, expected in [(("-",), "unsatisfiable"), (("x",), "solved")]:
        problem = build_problem(geometry(1, pattern), Lexicon(()))
        result = solve(problem, 0, perf_counter() + 1)
        assert result.reason == expected
        if result.assignment is not None:
            assert not verify(problem, result.assignment)


def test_trail_restores_domains_and_supports(tiny_grid):
    problem = build_problem(tiny_grid, Lexicon(("ab", "cd", "ac", "bd")))
    state = Domains(problem, perf_counter() + 1, True, True)
    assert state.propagate(list(range(4)))
    root = state.values.copy()
    supports = [row.copy() for row in state.supports]
    mark = len(state.trail)
    state.set(0, 1)
    state.propagate([0])
    state.restore(mark)
    assert state.values == root
    assert state.supports == supports


def test_index_masks_against_plain_scanning():
    words = ("aba", "bñb", "ñaa", "aab")
    index = WordIndex.build(words, 3)
    from crossbot.lexicon import ALPHABET

    for position, masks in enumerate(index.masks):
        for letter, mask in zip(ALPHABET, masks):
            expected = sum(
                1 << i for i, word in enumerate(words) if word[position] == letter
            )
            assert mask == expected


def test_registry_rejects_duplicate_and_multiple_defaults():
    registry = Registry()
    registry.register(Solver("test", "test", solve, True))
    with pytest.raises(ValueError, match="duplicate"):
        registry.register(Solver("test", "test", solve))
    with pytest.raises(ValueError, match="one default"):
        registry.register(Solver("test2", "test", solve, True))
    assert registry.default == "test"
    with pytest.raises(ValueError, match="exactly one"):
        _ = Registry().default
