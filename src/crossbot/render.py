"""Plain Unicode output: stable in terminals, pipes, and golden tests."""

from .grid import Grid
from .verify import Assignment


def render(grid: Grid, assignment: Assignment | None = None) -> str:
    numbers = {key.position: str(key.number) for key in grid.keys}
    letters = (
        {}
        if assignment is None
        else {
            cell: letter.upper()
            for i, slot in enumerate(grid.slots)
            for cell, letter in zip(slot.cells, assignment[i], strict=True)
        }
    )
    width = max(3, max((len(n) for n in numbers.values()), default=0))

    def rule(left: str, join: str, right: str) -> str:
        return left + join.join("─" * width for _ in range(grid.cols)) + right

    output = [rule("┌", "┬", "┐")]
    for r, row in enumerate(grid.pattern):
        values = []
        for c, value in enumerate(row):
            if value == "x":
                values.append("█" * width)
            elif assignment is None:
                values.append(numbers.get((r, c), "").ljust(width))
            else:
                values.append(letters.get((r, c), "").center(width))
        output.append("│" + "│".join(values) + "│")
        if r < grid.rows - 1:
            output.append(rule("├", "┼", "┤"))
    output.append(rule("└", "┴", "┘"))
    return "\n".join(output)
