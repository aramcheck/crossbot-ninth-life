"""Register strategies here; frontends depend only on the registry contract."""

from ..problem import Problem
from .api import Registry, Result, Solver
from .search import Features, solve


def forward(problem: Problem, seed: int, deadline: float) -> Result:
    return solve(problem, seed, deadline, Features(arc_consistency=False))


registry = Registry()
registry.register(
    Solver(
        "mac",
        "Bit-parallel arc consistency with sampled least-constraining words.",
        solve,
        default=True,
    )
)
registry.register(
    Solver(
        "forward", "Forward checking with the same search and value ordering.", forward
    )
)
