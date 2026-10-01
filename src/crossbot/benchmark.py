"""A regression gate over every selected grid × solver × seed combination."""

import argparse
import sys
from pathlib import Path
from time import perf_counter

from .cli import Parser, positive_timeout
from .grid import InputError, load_grid
from .lexicon import load_dictionary
from .problem import build_problem
from .runner import own_stats, run_solver
from .solvers import registry

ROOT = Path(__file__).resolve().parents[2]


def csv_ints(value: str) -> list[int]:
    try:
        return [int(part) for part in value.split(",")]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected comma-separated integers") from exc


def grid_files(directory: Path, identifiers: list[int] | None) -> list[Path]:
    if not directory.is_dir():
        raise InputError(f"{directory}: grid directory does not exist")
    files = list(directory.rglob("*.yaml"))
    for path in files:
        try:
            int(path.stem)
        except ValueError as exc:
            raise InputError(f"{path}: grid basename must be an integer") from exc
    files.sort(key=lambda p: (int(p.stem), str(p)))
    if identifiers is not None:
        missing = set(identifiers) - {int(path.stem) for path in files}
        if missing:
            raise InputError(
                f"grid ids not found: {', '.join(str(i) for i in sorted(missing))}"
            )
        files = [path for path in files if int(path.stem) in identifiers]
    if not files:
        raise InputError(f"{directory}: no grid files selected")
    return files


def main(argv: list[str] | None = None) -> int:
    parser = Parser(prog="benchmark")
    parser.add_argument("--solvers", default=registry.default)
    parser.add_argument("--seeds", type=csv_ints, default=[0])
    parser.add_argument("--timeout", type=positive_timeout, default=5.0)
    parser.add_argument("--grids", type=csv_ints)
    parser.add_argument("--grid-dir", type=Path, default=ROOT / "grids")
    parser.add_argument(
        "--dict", type=Path, default=ROOT / "dictionaries/words_alpha.txt"
    )
    try:
        args = parser.parse_args(argv)
        solvers = [registry.get(name) for name in args.solvers.split(",")]
        files = grid_files(args.grid_dir, args.grids)
        start = perf_counter()
        dictionary = load_dictionary(args.dict)
        print(
            f"dictionary: {len(dictionary.words)} words loaded in {perf_counter() - start:.2f}s"
        )
        print(
            f"{'grid':>5}  {'solver':>8}  {'seed':>5}  {'time':>8}  {'status':<6}  stats"
        )
        print("-" * 64)
        failures: list[tuple[int, str, int, str]] = []
        for path in files:
            grid = load_grid(path)
            problem = build_problem(grid, dictionary)
            for solver in solvers:
                for seed in args.seeds:
                    run = run_solver(problem, solver, seed, args.timeout)
                    print(
                        f"{grid.id:>5}  {solver.name:>8}  {seed:>5}  {run.elapsed:>7.2f}s  {run.status:<6}  {own_stats(run.result)}",
                        flush=True,
                    )
                    if run.status != "ok":
                        failures.append((grid.id, solver.name, seed, run.status))
        print()
        if failures:
            print(f"{len(failures)} failures:")
            for failure in failures:
                print(f"  ({failure[0]}, {failure[1]}, {failure[2]}, {failure[3]})")
            return 1
        print("all solved and verified")
        return 0
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
