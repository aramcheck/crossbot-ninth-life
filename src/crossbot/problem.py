"""Thematic locks and solver-neutral problem preparation."""

import re
import unicodedata
from dataclasses import dataclass

from .grid import Grid, InputError
from .lexicon import Lexicon, WordIndex, valid_word


def normalize_lock(word: str) -> str:
    # Protect the tilde: ñ is an alphabet member, not an accented n.
    return "".join(
        (
            "ñ"
            if part == "ñ"
            else "".join(
                c
                for c in unicodedata.normalize("NFD", part)
                if not unicodedata.combining(c)
            )
        )
        for part in unicodedata.normalize("NFC", word.lower())
    )


def parse_locks(grid: Grid, specs: list[str]) -> dict[int, str]:
    locks: dict[int, str] = {}
    labels = {(slot.number, slot.direction[0]): i for i, slot in enumerate(grid.slots)}
    cells: dict[tuple[int, int], str] = {}
    for spec in specs:

        def fail(reason: str) -> InputError:
            return InputError(f"lock {spec!r}: {reason}")

        match = re.fullmatch(r"([0-9]+)([hv]):(.+)", spec, re.IGNORECASE)
        if match is None:
            raise fail("expected <key-number><h|v>:<word>")
        number, direction, raw = match.groups()
        word = normalize_lock(raw)
        if not valid_word(word):
            raise fail("word contains characters outside a-z and ñ")
        key = (int(number), direction.lower())
        if key not in labels:
            if not any(k.number == key[0] for k in grid.keys):
                raise fail(f"no key {key[0]}")
            raise fail(f"key {key[0]} has no word in direction {key[1]}")
        index = labels[key]
        slot = grid.slots[index]
        if len(word) != slot.length:
            raise fail(
                f"word length {len(word)} differs from slot length {slot.length}"
            )
        if index in locks and locks[index] != word:
            raise fail("same slot locked twice to different words")
        if any(other != index and value == word for other, value in locks.items()):
            raise fail("same word locked to different slots")
        for cell, letter in zip(slot.cells, word, strict=True):
            if cell in cells and cells[cell] != letter:
                raise fail(f"crossing disagreement at {cell}")
            cells[cell] = letter
        locks[index] = word
    return locks


@dataclass(frozen=True)
class Problem:
    grid: Grid
    dictionary: Lexicon
    locks: dict[int, str]
    indexes: tuple[WordIndex, ...]
    domains: tuple[int, ...]
    peers: tuple[tuple[int, ...], ...]


def build_problem(
    grid: Grid, dictionary: Lexicon, locks: dict[int, str] | None = None
) -> Problem:
    locks = dict(locks or {})
    lengths = sorted({slot.length for slot in grid.slots})
    indexes: dict[int, WordIndex] = {}
    for length in lengths:
        extra = tuple(
            dict.fromkeys(
                word
                for word in locks.values()
                if len(word) == length and word not in dictionary.members
            )
        )
        if not dictionary.by_length.get(length) and not extra:
            raise InputError(f"dictionary has no words of length {length}")
        indexes[length] = (
            WordIndex.build(dictionary.by_length.get(length, ()) + extra, length)
            if extra
            else dictionary.index(length)
        )
    per_slot = tuple(indexes[slot.length] for slot in grid.slots)
    domains = tuple(
        1 << index.ids[locks[i]] if i in locks else index.full
        for i, index in enumerate(per_slot)
    )
    peers = tuple(
        tuple(
            j
            for j, other in enumerate(grid.slots)
            if i != j and slot.length == other.length
        )
        for i, slot in enumerate(grid.slots)
    )
    return Problem(grid, dictionary, locks, per_slot, domains, peers)
