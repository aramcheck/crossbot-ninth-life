"""Wall-clock measurement and independent verification shared by both CLIs."""

import math
import re
from decimal import Decimal
from dataclasses import dataclass
from time import perf_counter

from .problem import Problem
from .solvers.api import Result, Solver
from .verify import lock_defects, verify


@dataclass(frozen=True)
class Run:
    result: Result
    elapsed: float
    defects: tuple[str, ...]
    bad_locks: tuple[str, ...]

    @property
    def status(self) -> str:
        if self.defects:
            return f"INVALID: {self.defects[0]}"
        return "ok" if self.result.assignment is not None else "FAIL"


def own_stats(result: Result) -> str:
    for key, value in result.stats.items():
        if (
            re.fullmatch(r"[a-z_]+", key) is None
            or type(value) not in (int, float)
            or not math.isfinite(value)
        ):
            raise ValueError("invalid solver statistics")
    return " ".join(
        f"{key}={format(Decimal(str(value)), 'f')}"
        for key, value in result.stats.items()
    )


def run_solver(problem: Problem, solver: Solver, seed: int, timeout: float) -> Run:
    start = perf_counter()
    result = solver.solve(problem, seed, start + timeout)
    elapsed = perf_counter() - start
    assignment = result.assignment
    return Run(
        result,
        elapsed,
        tuple(verify(problem, assignment)) if assignment is not None else (),
        tuple(lock_defects(problem, assignment)) if assignment is not None else (),
    )


def stats_block(run: Run, solver: str, seed: int) -> str:
    extra = own_stats(run.result)
    return f"solver={solver} seed={seed} time={run.elapsed:.2f}s" + (
        f" {extra}" if extra else ""
    )
