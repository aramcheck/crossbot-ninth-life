"""Minimum remaining values and bounded-sample least-constraining values."""

import math
import random
from typing import Iterator

from ..lexicon import LETTER_ID
from .propagation import Domains, bits


def choose_slot(state: Domains, degree_ties: bool) -> int | None:
    best: tuple[int, int, int] | None = None
    for i, domain in enumerate(state.values):
        count = domain.bit_count()
        if count <= 1:
            continue
        degree = (
            sum(
                state.values[c.other].bit_count() > 1
                for c in state.problem.grid.crossings[i]
            )
            if degree_ties
            else 0
        )
        key = (count, -degree, i)
        if best is None or key < best:
            best = key
    return None if best is None else best[2]


def candidates(
    state: Domains,
    slot: int,
    rng: random.Random,
    sample_size: int,
    value_ordering: bool,
) -> Iterator[int]:
    domain = state.values[slot]
    count = domain.bit_count()
    if count <= sample_size * 2:
        sample = list(bits(domain))
        rng.shuffle(sample)
    elif count * 8 >= domain.bit_length():
        chosen: set[int] = set()
        while len(chosen) < sample_size:
            state.check()
            candidate = rng.randrange(domain.bit_length())
            if (domain >> candidate) & 1:
                chosen.add(candidate)
        sample = sorted(chosen)  # Never depend on set iteration for reproducibility.
        rng.shuffle(sample)
    else:
        sample = rng.sample(list(bits(domain)), sample_size)
    if value_ordering:
        index = state.problem.indexes[slot]

        def score(candidate: int) -> float:
            state.check()
            word = index.words[candidate]
            total = 0.0
            for edge in state.problem.grid.crossings[slot]:
                supports = (
                    state.values[edge.other]
                    & state.problem.indexes[edge.other].masks[edge.there][
                        LETTER_ID[word[edge.here]]
                    ]
                )
                if not supports:
                    return -math.inf
                total += math.log(supports.bit_count())
            return total

        sample.sort(key=score, reverse=True)
    yield from sample
    remaining = domain
    for candidate in sample:
        remaining &= ~(1 << candidate)
    yield from bits(remaining)
