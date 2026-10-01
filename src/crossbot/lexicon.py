"""Stable dictionary loading and length/position/letter bitset indexes."""

from dataclasses import dataclass
from pathlib import Path

from .grid import InputError

ALPHABET = "abcdefghijklmnopqrstuvwxyzñ"
LETTER_ID = {letter: i for i, letter in enumerate(ALPHABET)}


def valid_word(word: str) -> bool:
    return bool(word) and all(letter in LETTER_ID for letter in word)


@dataclass(frozen=True)
class WordIndex:
    words: tuple[str, ...]
    ids: dict[str, int]
    masks: tuple[tuple[int, ...], ...]

    @property
    def full(self) -> int:
        return (1 << len(self.words)) - 1

    @classmethod
    def build(cls, words: tuple[str, ...], length: int) -> "WordIndex":
        size = (len(words) + 7) // 8
        buffers = [[bytearray(size) for _ in ALPHABET] for _ in range(length)]
        for i, word in enumerate(words):
            byte, bit = i >> 3, 1 << (i & 7)
            for position, letter in enumerate(word):
                buffers[position][LETTER_ID[letter]][byte] |= bit
        return cls(
            words,
            {w: i for i, w in enumerate(words)},
            tuple(tuple(int.from_bytes(b, "little") for b in row) for row in buffers),
        )


class Lexicon:
    """Retain input order (including duplicates); index distinct words lazily."""

    def __init__(self, words: tuple[str, ...]) -> None:
        self.words = words
        self.members = frozenset(words)
        grouped: dict[int, list[str]] = {}
        for word in dict.fromkeys(words):
            grouped.setdefault(len(word), []).append(word)
        self.by_length = {length: tuple(group) for length, group in grouped.items()}
        self._indexes: dict[int, WordIndex] = {}

    def index(self, length: int) -> WordIndex:
        if length not in self._indexes:
            self._indexes[length] = WordIndex.build(
                self.by_length.get(length, ()), length
            )
        return self._indexes[length]


def load_dictionary(path: Path) -> Lexicon:
    try:
        with path.open(encoding="utf-8") as stream:
            words = tuple(
                word for line in stream if valid_word(word := line.strip().lower())
            )
    except (OSError, UnicodeError) as exc:
        raise InputError(f"{path}: {exc}") from exc
    return Lexicon(words)
