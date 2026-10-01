"""Independent end-to-end verification; never trusts solver domains."""

from .problem import Problem

Assignment = dict[int, str]


def lock_defects(problem: Problem, assignment: Assignment) -> list[str]:
    return [
        problem.grid.slots[i].label
        for i, word in problem.locks.items()
        if assignment.get(i) != word
    ]


def verify(problem: Problem, assignment: Assignment) -> list[str]:
    defects: list[str] = []
    cells: dict[tuple[int, int], str] = {}
    used: set[str] = set()
    if set(assignment) - set(range(len(problem.grid.slots))):
        defects.append("assignment contains unknown slots")
    for i, slot in enumerate(problem.grid.slots):
        word = assignment.get(i)
        if word is None:
            defects.append(f"slot {slot.label} is unfilled")
            continue
        if len(word) != slot.length:
            defects.append(
                f"slot {slot.label}: wrong length {len(word)}, expected {slot.length}"
            )
            continue
        if i in problem.locks:
            if word != problem.locks[i]:
                defects.append(f"slot {slot.label}: lock not honoured")
        elif word not in problem.dictionary.members:
            defects.append(f"slot {slot.label}: {word!r} is not in dictionary")
        if word in used:
            defects.append(f"repeated word {word!r}")
        used.add(word)
        for cell, letter in zip(slot.cells, word, strict=True):
            if cell in cells and cells[cell] != letter:
                defects.append(f"crossing mismatch at {cell}")
            cells[cell] = letter
    for r, row in enumerate(problem.grid.pattern):
        for c, value in enumerate(row):
            if value == "-" and (r, c) not in cells:
                defects.append(f"open cell {(r, c)} is unfilled")
    return defects
