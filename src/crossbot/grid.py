"""Validated grid geometry, canonical numbering, and crossing topology."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

Direction = Literal["horizontal", "vertical"]
Cell = tuple[int, int]


class InputError(ValueError):
    """An explanatory input failure suitable for a single CLI message."""


class Schema(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Dimensions(Schema):
    rows: int = Field(ge=1)
    cols: int = Field(ge=1)


class KeySpec(Schema):
    number: int
    position: list[int] = Field(min_length=2, max_length=2)
    directions: list[Direction]


class GridSpec(Schema):
    id: int
    source_page: int | None = None
    dimensions: Dimensions
    density: float | None = Field(default=None, allow_inf_nan=False)
    word_count: int | None = None
    stated_word_count: int | None = None
    grid: str
    keys: list[KeySpec]


@dataclass(frozen=True)
class Key:
    number: int
    position: Cell
    directions: tuple[Direction, ...]


@dataclass(frozen=True)
class Slot:
    number: int
    direction: Direction
    cells: tuple[Cell, ...]

    @property
    def label(self) -> str:
        return f"{self.number}{self.direction[0]}"

    @property
    def length(self) -> int:
        return len(self.cells)


@dataclass(frozen=True)
class Crossing:
    other: int
    here: int
    there: int


@dataclass(frozen=True)
class Grid:
    id: int
    pattern: tuple[str, ...]
    keys: tuple[Key, ...]
    slots: tuple[Slot, ...]
    crossings: tuple[tuple[Crossing, ...], ...]

    @property
    def rows(self) -> int:
        return len(self.pattern)

    @property
    def cols(self) -> int:
        return len(self.pattern[0])

    @property
    def density(self) -> float:
        return (
            100 * sum(row.count("-") for row in self.pattern) / (self.rows * self.cols)
        )


def geometry(identifier: int, pattern: tuple[str, ...]) -> Grid:
    """Derive numbering and maximal runs; no input metadata is trusted."""
    rows, cols = len(pattern), len(pattern[0])
    keys: list[Key] = []
    slots: list[Slot] = []
    occupants: dict[Cell, list[tuple[int, int]]] = {}
    for r in range(rows):
        for c in range(cols):
            if pattern[r][c] != "-":
                continue
            directions: list[Direction] = []
            for direction, dr, dc in (("horizontal", 0, 1), ("vertical", 1, 0)):
                if r - dr >= 0 and c - dc >= 0 and pattern[r - dr][c - dc] == "-":
                    continue
                cells: list[Cell] = []
                rr, cc = r, c
                while rr < rows and cc < cols and pattern[rr][cc] == "-":
                    cells.append((rr, cc))
                    rr, cc = rr + dr, cc + dc
                if len(cells) < 2:
                    continue
                typed_direction: Direction = "horizontal" if dc else "vertical"
                directions.append(typed_direction)
                index = len(slots)
                for position, cell in enumerate(cells):
                    occupants.setdefault(cell, []).append((index, position))
                slots.append(Slot(len(keys) + 1, typed_direction, tuple(cells)))
            if directions:
                keys.append(Key(len(keys) + 1, (r, c), tuple(directions)))
    crossings: list[list[Crossing]] = [[] for _ in slots]
    for entries in occupants.values():
        if len(entries) == 2:
            (a, ap), (b, bp) = entries
            crossings[a].append(Crossing(b, ap, bp))
            crossings[b].append(Crossing(a, bp, ap))
    return Grid(
        identifier,
        pattern,
        tuple(keys),
        tuple(slots),
        tuple(tuple(x) for x in crossings),
    )


def validate_grid(spec: GridSpec) -> Grid:
    lines = tuple(spec.grid.splitlines())
    if len(lines) != spec.dimensions.rows:
        raise InputError(
            f"grid lines: expected {spec.dimensions.rows}, got {len(lines)}"
        )
    for r, line in enumerate(lines):
        if len(line) != spec.dimensions.cols:
            raise InputError(
                f"row {r}: expected {spec.dimensions.cols} characters, got {len(line)}"
            )
        if set(line) - {"-", "x"}:
            raise InputError(f"row {r}: grid characters must be '-' or 'x'")
    result = geometry(spec.id, lines)
    for key in spec.keys:
        r, c = key.position
        if not (0 <= r < result.rows and 0 <= c < result.cols):
            raise InputError(f"key {key.number}: position out of bounds")
        if lines[r][c] != "-":
            raise InputError(f"key {key.number}: position is blocked")
    given = [(k.number, tuple(k.position), frozenset(k.directions)) for k in spec.keys]
    expected = [(k.number, k.position, frozenset(k.directions)) for k in result.keys]
    if given != expected or any(
        len(k.directions) != len(set(k.directions)) for k in spec.keys
    ):
        raise InputError(
            "keys mismatch: expected exactly the canonical numbering and directions in order"
        )
    if spec.word_count is not None and spec.word_count != len(result.slots):
        raise InputError(
            f"word_count mismatch: declared {spec.word_count}, computed {len(result.slots)}"
        )
    if spec.density is not None and abs(spec.density - result.density) > 0.010000001:
        raise InputError(
            f"density mismatch: declared {spec.density:.2f}%, computed {result.density:.2f}%"
        )
    return result


def load_grid(path: Path) -> Grid:
    try:
        data: object = yaml.safe_load(path.read_text(encoding="utf-8"))
        return validate_grid(GridSpec.model_validate(data))
    except ValidationError as exc:
        issue = exc.errors()[0]
        location = ".".join(str(part) for part in issue["loc"])
        raise InputError(f"{path}: {location}: {issue['msg']}") from exc
    except (OSError, UnicodeError, yaml.YAMLError, InputError) as exc:
        raise InputError(f"{path}: {exc}") from exc
