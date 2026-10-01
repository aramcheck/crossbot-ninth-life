"""Unshipped min-conflicts experiment on the unresolved grid (Appendix A).

Bitset dynamic programming finds the Hamming-optimal replacement word.
Random walks and fixed-length restarts are experiments, not completeness claims.
"""

import json
import random
from pathlib import Path
from time import perf_counter

from crossbot.grid import load_grid
from crossbot.lexicon import LETTER_ID, load_dictionary
from crossbot.problem import build_problem
from crossbot.verify import verify

ROOT = Path(__file__).resolve().parents[1]


def pick(mask, rng):
    width = mask.bit_length()
    if mask.bit_count() * 8 < width:
        ids = []
        while mask:
            bit = mask & -mask
            ids.append(bit.bit_length() - 1)
            mask ^= bit
        return rng.choice(ids)
    while True:
        i = rng.randrange(width)
        if (mask >> i) & 1:
            return i


def run(problem, seed, budget, noise):
    rng = random.Random(seed)
    start = perf_counter()
    deadline = start + budget
    steps = 0
    restarts = 0
    best = 1000000
    while perf_counter() < deadline:
        assignment = []
        used = {}
        for i, index in enumerate(problem.indexes):
            length = problem.grid.slots[i].length
            live = index.full & ~used.get(length, 0)
            if not live:
                return None, steps, restarts, best, perf_counter() - start
            value = pick(live, rng)
            assignment.append(value)
            used[length] = used.get(length, 0) | (1 << value)
        for _ in range(2000):
            if perf_counter() >= deadline:
                break
            words = [
                index.words[value] for index, value in zip(problem.indexes, assignment)
            ]
            conflicts = []
            errors = 0
            for i, edges in enumerate(problem.grid.crossings):
                count = sum(words[i][e.here] != words[e.other][e.there] for e in edges)
                errors += count
                if count:
                    conflicts.append(i)
            errors //= 2
            if errors < best:
                best = errors
            if not conflicts:
                solution = dict(enumerate(words))
                assert not verify(problem, solution)
                return solution, steps, restarts, best, perf_counter() - start
            slot = rng.choice(conflicts)
            length = problem.grid.slots[slot].length
            old = assignment[slot]
            used[length] ^= 1 << old
            live = problem.indexes[slot].full & ~used[length]
            if rng.random() >= noise:
                groups = [live]
                for edge in problem.grid.crossings[slot]:
                    mask = problem.indexes[slot].masks[edge.here][
                        LETTER_ID[words[edge.other][edge.there]]
                    ]
                    groups = [groups[0] & mask] + [
                        (groups[k] & mask if k < len(groups) else 0)
                        | (groups[k - 1] & ~mask)
                        for k in range(1, len(groups) + 1)
                    ]
                live = next(group for group in groups if group)
            value = pick(live, rng)
            assignment[slot] = value
            used[length] |= 1 << value
            steps += 1
        restarts += 1
    return None, steps, restarts, best, perf_counter() - start


def main():
    rows = []
    grid = load_grid(ROOT / "grids/core/87.yaml")
    for name in ("words_alpha.txt", "uk220k.txt", "words.es.rae.txt"):
        problem = build_problem(grid, load_dictionary(ROOT / "dictionaries" / name))
        for noise in (0.02, 0.1):
            for seed in range(3):
                solution, steps, restarts, best, elapsed = run(problem, seed, 5, noise)
                row = {
                    "dictionary": name,
                    "seed": seed,
                    "noise": noise,
                    "budget": 5,
                    "elapsed": elapsed,
                    "steps": steps,
                    "restarts": restarts,
                    "best_crossing_errors": best,
                    "assignment": solution,
                }
                rows.append(row)
                print(
                    row if solution is None else {**row, "assignment": "verified"},
                    flush=True,
                )
    (ROOT / "benchmarks/local-search.json").write_text(
        json.dumps(rows, indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
