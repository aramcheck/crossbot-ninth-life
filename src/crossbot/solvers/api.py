"""A deliberately small solver contract and registry."""

from dataclasses import dataclass
from typing import Callable, Literal

from ..grid import InputError
from ..problem import Problem
from ..verify import Assignment


@dataclass(frozen=True)
class Result:
    assignment: Assignment | None
    reason: Literal["solved", "unsatisfiable", "timeout"]
    stats: dict[str, int | float]


Solve = Callable[[Problem, int, float], Result]


@dataclass(frozen=True)
class Solver:
    name: str
    description: str
    solve: Solve
    default: bool = False


class Registry:
    def __init__(self) -> None:
        self._solvers: dict[str, Solver] = {}

    def register(self, solver: Solver) -> None:
        if solver.name in self._solvers:
            raise ValueError(f"duplicate solver {solver.name}")
        if solver.default and any(s.default for s in self._solvers.values()):
            raise ValueError("only one default solver is allowed")
        self._solvers[solver.name] = solver

    def all(self) -> list[Solver]:
        return sorted(self._solvers.values(), key=lambda s: s.name)

    @property
    def default(self) -> str:
        defaults = [s.name for s in self.all() if s.default]
        if len(defaults) != 1:
            raise ValueError("exactly one default solver must be registered")
        return defaults[0]

    def get(self, name: str) -> Solver:
        if name not in self._solvers:
            raise InputError(
                f"unknown solver {name!r}; available: {', '.join(s.name for s in self.all())}"
            )
        return self._solvers[name]
