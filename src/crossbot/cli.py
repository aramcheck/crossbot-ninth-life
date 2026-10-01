"""The user-facing contract: loading, solving, verification, and rendering."""

import argparse
import math
import sys
from pathlib import Path
from typing import NoReturn

from .grid import InputError, load_grid
from .lexicon import load_dictionary
from .problem import build_problem, parse_locks
from .render import render
from .runner import run_solver, stats_block
from .solvers import registry


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise InputError(message)


def positive_timeout(value: str) -> float:
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "timeout must be a positive finite number"
        ) from exc
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("timeout must be a positive finite number")
    return number


def parser() -> Parser:
    result = Parser(prog="crossbot")
    commands = result.add_subparsers(dest="command", required=True)
    info = commands.add_parser("grid-info", help="validate and render a numbered grid")
    info.add_argument("grid_file", type=Path)
    solve = commands.add_parser("solve", help="fill a grid and independently verify it")
    solve.add_argument("grid_file", type=Path)
    solve.add_argument("dictionary", type=Path)
    solve.add_argument("--solver", default=registry.default)
    solve.add_argument("--seed", type=int, default=0)
    solve.add_argument("--timeout", type=positive_timeout, default=10.0)
    solve.add_argument("-w", "--word", action="append", default=[])
    commands.add_parser("list-solvers", help="list registered strategies")
    return result


def main(argv: list[str] | None = None) -> int:
    try:
        args = parser().parse_args(argv)
        if args.command == "list-solvers":
            solvers = registry.all()
            width = max(len(s.name) for s in solvers)
            for solver in solvers:
                print(
                    f"{solver.name:<{width}}  {solver.description}"
                    + (" (default)" if solver.default else "")
                )
            return 0
        grid = load_grid(args.grid_file)
        if args.command == "grid-info":
            print(render(grid))
            print(
                f"grid {grid.id}: {grid.rows}x{grid.cols}, density {grid.density:.2f}%, {len(grid.keys)} keys, {len(grid.slots)} words"
            )
            print("OK: grid is consistent")
            return 0
        solver = registry.get(args.solver)
        dictionary = load_dictionary(args.dictionary)
        locks = parse_locks(grid, args.word)
        problem = build_problem(grid, dictionary, locks)
        run = run_solver(problem, solver, args.seed, args.timeout)
        stats = stats_block(run, solver.name, args.seed)
        if run.bad_locks:
            print(
                f"internal error: locked slots {list(run.bad_locks)} not honoured",
                file=sys.stderr,
            )
            return 1
        if run.defects:
            print(
                "invalid solution:\n"
                + "\n".join(f"  {defect}" for defect in run.defects),
                file=sys.stderr,
            )
            return 1
        if run.result.assignment is None:
            message = (
                "locked words admit no solution for this grid"
                if locks and run.result.reason == "unsatisfiable"
                else f"no solution found within {args.timeout:g}s"
            )
            print(f"{message} ({stats})", file=sys.stderr)
            return 1
        print(render(grid, run.result.assignment))
        if locks:
            ordered = sorted(
                locks, key=lambda i: (grid.slots[i].number, grid.slots[i].direction)
            )
            print(
                "locked words honoured: "
                + " ".join(f"{grid.slots[i].label}={locks[i].upper()}" for i in ordered)
            )
        print(
            f"SOLVED grid {grid.id}: {len(grid.slots)} words placed, all distinct ({stats})"
        )
        return 0
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
