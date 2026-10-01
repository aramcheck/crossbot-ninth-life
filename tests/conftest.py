from pathlib import Path

import pytest
import yaml

from crossbot.grid import Grid, geometry


@pytest.fixture
def tiny_grid() -> Grid:
    return geometry(7, ("--", "--"))


@pytest.fixture
def tiny_file(tmp_path: Path, tiny_grid: Grid) -> Path:
    data = {
        "id": tiny_grid.id,
        "dimensions": {"rows": tiny_grid.rows, "cols": tiny_grid.cols},
        "grid": "\n".join(tiny_grid.pattern) + "\n",
        "keys": [
            {
                "number": k.number,
                "position": list(k.position),
                "directions": list(k.directions),
            }
            for k in tiny_grid.keys
        ],
    }
    path = tmp_path / "7.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


@pytest.fixture
def tiny_dictionary(tmp_path: Path) -> Path:
    path = tmp_path / "words.txt"
    path.write_text("ab\ncd\nac\nbd\n", encoding="utf-8")
    return path
