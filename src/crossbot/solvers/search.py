"""Depth-first search with geometrically increasing randomized restarts."""

import random
from dataclasses import dataclass
from typing import Literal

from ..problem import Problem
from .api import Result
from .ordering import candidates, choose_slot
from .propagation import Deadline, Domains


@dataclass(frozen=True)
class Features:
    arc_consistency: bool = True
    value_ordering: bool = True
    restarts: bool = True
    degree: bool = True
    support_cache: bool = True
    sample_size: int = 48
    restart_nodes: int = 400


class Restart(Exception):
    """Node quota exhausted, but not a proof of unsatisfiability."""


class Search:
    def __init__(
        self, problem: Problem, seed: int, deadline: float, features: Features
    ) -> None:
        self.problem = problem
        self.features = features
        self.rng = random.Random(seed)
        self.state = Domains(
            problem, deadline, features.arc_consistency, features.support_cache
        )
        self.nodes = 0
        self.backtracks = 0
        self.restarts = 0
        self.stop_at = features.restart_nodes

    def dfs(self) -> bool:
        self.state.check()
        slot = choose_slot(self.state, self.features.degree)
        if slot is None:
            return True
        for candidate in candidates(
            self.state,
            slot,
            self.rng,
            self.features.sample_size,
            self.features.value_ordering,
        ):
            self.state.check()
            if self.features.restarts and self.nodes >= self.stop_at:
                raise Restart
            self.nodes += 1
            mark = len(self.state.trail)
            self.state.set(slot, 1 << candidate)
            if self.state.propagate([slot]) and self.dfs():
                return True
            self.state.restore(mark)
            self.backtracks += 1
        return False

    def run(self) -> Result:
        reason: Literal["solved", "unsatisfiable", "timeout"] = "unsatisfiable"
        assignment = None
        covered = {cell for slot in self.problem.grid.slots for cell in slot.cells}
        coverable = all(
            value != "-" or (r, c) in covered
            for r, row in enumerate(self.problem.grid.pattern)
            for c, value in enumerate(row)
        )
        try:
            self.state.check()
            if coverable and self.state.propagate(list(range(len(self.state.values)))):
                root = list(self.state.values)
                root_supports = [row.copy() for row in self.state.supports]
                self.state.trail.clear()
                while True:
                    try:
                        if self.dfs():
                            assignment = {
                                i: index.words[self.state.values[i].bit_length() - 1]
                                for i, index in enumerate(self.problem.indexes)
                            }
                            reason = "solved"
                        break
                    except Restart:
                        self.restarts += 1
                        self.state.values = list(root)
                        self.state.supports = [row.copy() for row in root_supports]
                        self.state.trail.clear()
                        self.stop_at = self.nodes + self.features.restart_nodes * (
                            2 ** min(self.restarts, 12)
                        )
        except Deadline:
            reason = "timeout"
        return Result(
            assignment,
            reason,
            {
                "nodes": self.nodes,
                "backtracks": self.backtracks,
                "revisions": self.state.revisions,
                "restarts": self.restarts,
            },
        )


def solve(
    problem: Problem, seed: int, deadline: float, features: Features = Features()
) -> Result:
    return Search(problem, seed, deadline, features).run()
