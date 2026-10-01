"""Reproduce the report's data; unlike `benchmark`, censored runs are retained.

No performance threshold is silently converted into a success. Each successful
row includes its verified assignment, and failures retain their solver reason.
"""

import argparse
import hashlib
import json
import platform
from dataclasses import replace
from pathlib import Path
from time import perf_counter

from crossbot.benchmark import grid_files
from crossbot.grid import load_grid
from crossbot.lexicon import load_dictionary
from crossbot.problem import build_problem
from crossbot.runner import run_solver
from crossbot.solvers import registry
from crossbot.solvers.api import Solver
from crossbot.solvers.search import Features, solve

ROOT = Path(__file__).resolve().parents[1]


def fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_digest() -> str:
    digest = hashlib.sha256()
    for path in sorted((ROOT / "src").rglob("*.py")):
        digest.update(str(path.relative_to(ROOT)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def row(path, problem, solver, seed, budget, preparation=0.0):
    run = run_solver(problem, solver, seed, budget)
    print(
        path.relative_to(ROOT),
        solver.name,
        seed,
        f"{run.elapsed:.6f}s",
        run.status,
        flush=True,
    )
    return {
        "grid": str(path.relative_to(ROOT)),
        "id": problem.grid.id,
        "solver": solver.name,
        "seed": seed,
        "budget": budget,
        "preparation": preparation,
        "elapsed": run.elapsed,
        "status": run.status,
        "reason": run.result.reason,
        "stats": run.result.stats,
        "assignment": run.result.assignment,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "benchmarks/results.json")
    args = parser.parse_args()
    dictionary_path = ROOT / "dictionaries/words_alpha.txt"
    start = perf_counter()
    dictionary = load_dictionary(dictionary_path)
    load_time = perf_counter() - start
    output = {
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "architecture": platform.machine(),
            "machine": "Apple-vendor aarch64 Linux VM; 5 vCPUs; 7.9 GiB RAM; host model not exposed",
            "source_sha256": source_digest(),
            "dictionary": str(dictionary_path.relative_to(ROOT)),
            "dictionary_sha256": fingerprint(dictionary_path),
            "words": len(dictionary.words),
            "dictionary_load_seconds": load_time,
            "timer": "time.perf_counter; preparation and verification excluded from solve timer",
            "timeout": 5.0,
            "suite_seeds": [0],
            "ablation_seeds": [0, 1, 2],
        },
        "suite": [],
        "ablation": [],
        "other_dictionaries": [],
    }
    for path in grid_files(ROOT / "grids", None):
        start = perf_counter()
        problem = build_problem(load_grid(path), dictionary)
        preparation = perf_counter() - start
        for solver in registry.all():
            output["suite"].append(row(path, problem, solver, 0, 5, preparation))
    configurations = {"default": Features()}
    for feature in (
        "arc_consistency",
        "value_ordering",
        "restarts",
        "degree",
        "support_cache",
    ):
        configurations[f"no_{feature}"] = replace(Features(), **{feature: False})
    for relative in (
        "grids/core/90.yaml",
        "grids/gecode/45.yaml",
        "grids/gecode/49.yaml",
    ):
        path = ROOT / relative
        problem = build_problem(load_grid(path), dictionary)
        for name, features in configurations.items():

            def configured(p, seed, deadline, f=features):
                return solve(p, seed, deadline, f)

            solver = Solver(name, "isolated ablation", configured)
            for seed in range(3):
                output["ablation"].append(row(path, problem, solver, seed, 5))
    path = ROOT / "grids/core/87.yaml"
    for name in ("words_alpha.txt", "uk220k.txt", "words.es.rae.txt"):
        dictionary_path = ROOT / "dictionaries" / name
        lexicon = (
            dictionary
            if name == "words_alpha.txt"
            else load_dictionary(dictionary_path)
        )
        problem = build_problem(load_grid(path), lexicon)
        for seed in range(3):
            result = row(path, problem, registry.get("mac"), seed, 5)
            result.update(
                dictionary=name,
                dictionary_sha256=fingerprint(dictionary_path),
                words=len(lexicon.words),
            )
            output["other_dictionaries"].append(result)
    args.output.parent.mkdir(exist_ok=True, parents=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")


if __name__ == "__main__":
    main()
