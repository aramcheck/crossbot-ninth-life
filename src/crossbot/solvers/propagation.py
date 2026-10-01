"""Reversible bitset domains and crossing arc consistency.

A domain is an integer whose set bits are dictionary word IDs. A supported
letter signature is a 27-bit set. A crossing need not be revised until this
signature changes, even if many words have been removed from its source.
"""

from collections import deque
from time import perf_counter
from typing import Iterator

from ..lexicon import LETTER_ID
from ..problem import Problem


class Deadline(Exception):
    """Cooperative cancellation at a monotonic wall-clock deadline."""


def bits(mask: int) -> Iterator[int]:
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


class Domains:
    def __init__(
        self, problem: Problem, deadline: float, arc: bool, cache: bool
    ) -> None:
        self.problem = problem
        self.deadline = deadline
        self.arc = arc
        self.cache = cache
        self.values = list(problem.domains)
        self.supports = [[-1] * slot.length for slot in problem.grid.slots]
        self.trail: list[tuple[int, int, list[int]]] = []
        self.revisions = 0

    def check(self) -> None:
        if perf_counter() >= self.deadline:
            raise Deadline

    def set(self, slot: int, value: int) -> None:
        self.trail.append((slot, self.values[slot], self.supports[slot].copy()))
        self.values[slot] = value

    def restore(self, mark: int) -> None:
        while len(self.trail) > mark:
            slot, value, supports = self.trail.pop()
            self.values[slot] = value
            self.supports[slot] = supports

    def propagate(self, changed: list[int]) -> bool:
        queue = deque(changed)
        queued = set(changed)

        def restrict(slot: int, value: int) -> bool:
            if value == self.values[slot]:
                return True
            self.set(slot, value)
            if not value:
                return False
            if slot not in queued:
                queue.append(slot)
                queued.add(slot)
            return True

        while queue:
            self.check()
            source = queue.popleft()
            queued.remove(source)
            domain = self.values[source]
            if not domain:
                return False
            index = self.problem.indexes[source]
            singleton = domain & (domain - 1) == 0
            if singleton:
                for other in self.problem.peers[source]:
                    if not restrict(other, self.values[other] & ~domain):
                        return False
            if not self.arc and not singleton:
                continue
            for edge in self.problem.grid.crossings[source]:
                if singleton:
                    letter = LETTER_ID[index.words[domain.bit_length() - 1][edge.here]]
                    signature = 1 << letter
                else:
                    signature = sum(
                        1 << letter
                        for letter, mask in enumerate(index.masks[edge.here])
                        if domain & mask
                    )
                if self.cache and signature == self.supports[source][edge.here]:
                    continue
                self.supports[source][edge.here] = signature
                masks = self.problem.indexes[edge.other].masks[edge.there]
                missing = ((1 << 27) - 1) ^ signature
                union = 0
                if missing.bit_count() < signature.bit_count():
                    for letter in bits(missing):
                        union |= masks[letter]
                    revised = self.values[edge.other] & ~union
                else:
                    for letter in bits(signature):
                        union |= masks[letter]
                    revised = self.values[edge.other] & union
                if revised != self.values[edge.other]:
                    self.revisions += 1
                    if not restrict(edge.other, revised):
                        return False
        return True
