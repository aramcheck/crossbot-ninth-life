"""Deterministically regenerate all six vector figures and derived report data."""

import html
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from crossbot.grid import load_grid
from crossbot.lexicon import load_dictionary

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BLUE, ORANGE, GREY = "#245b78", "#bc6c25", "#666666"


def text(x, y, value, size=16, color="#222", mono=False, anchor="start"):
    family = "DejaVu Sans Mono" if mono else "Libertinus Serif"
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{family}" font-size="{size}" text-anchor="{anchor}">{html.escape(str(value))}</text>'


def line(x1, y1, x2, y2, color=GREY, dashed=False):
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.6"'
        + (' stroke-dasharray="5 4"' if dashed else "")
        + "/>"
    )


def box(x, y, w, h, label, color=BLUE):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="white" stroke="{color}" stroke-width="2"/>'
        + text(x + w / 2, y + h / 2 + 5, label, 16, color, anchor="middle")
    )


def save(name, width, height, parts):
    content = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/>'
        + "".join(parts)
        + "</svg>\n"
    )
    (HERE / name).write_text(content)


def main():
    results = json.loads((ROOT / "benchmarks/results.json").read_text())
    rows = [r for r in results["suite"] if r["solver"] == "mac"]
    save(
        "representation.svg",
        800,
        240,
        [
            text(20, 25, "A length-two word index and a letter restriction", 22),
            text(25, 65, "ID      0     1     2     3", mono=True),
            text(25, 98, "word   ab    ac    bd    cd", mono=True),
            box(20, 125, 300, 65, "D = 1111 (all words)"),
            line(322, 155, 450, 155),
            text(342, 143, "AND", mono=True),
            box(453, 125, 322, 65, "D' = 0011 (ab, ac)", ORANGE),
            text(420, 90, "M[position 0, a] = 0011", mono=True),
            text(
                25,
                222,
                "Bit order shown most-significant first; each set bit denotes a live word.",
            ),
        ],
    )
    save(
        "control.svg",
        800,
        400,
        [
            box(15, 30, 220, 60, "Initial propagation"),
            box(290, 30, 220, 60, "Check deadline / quota"),
            box(565, 30, 220, 60, "Select MRV slot"),
            line(235, 60, 290, 60),
            line(510, 60, 565, 60),
            box(565, 155, 220, 60, "Sample / order words"),
            line(675, 90, 675, 155),
            box(290, 155, 220, 60, "Assign; propagate"),
            line(565, 185, 510, 185),
            box(15, 155, 220, 60, "Success: return fill", ORANGE),
            line(290, 185, 235, 185),
            box(290, 280, 220, 60, "Failure: restore trail", ORANGE),
            line(400, 215, 400, 280),
            line(510, 310, 750, 310),
            line(750, 310, 750, 215),
            text(555, 293, "next word"),
            line(290, 310, 90, 310),
            line(90, 310, 90, 235),
            text(20, 350, "exhausted → backtrack; root exhausted → UNSAT", 16),
            text(
                20,
                378,
                "Quota → restore root, double allowance; deadline → TIMEOUT",
                16,
            ),
        ],
    )
    save(
        "architecture.svg",
        800,
        310,
        [
            box(15, 20, 215, 65, "YAML / words / locks"),
            box(292, 20, 220, 65, "Validated Problem"),
            line(230, 52, 292, 52),
            box(15, 140, 215, 65, "CLI / benchmark"),
            box(292, 125, 220, 65, "MAC (default)"),
            box(292, 225, 220, 65, "Forward checking", ORANGE),
            line(402, 85, 402, 125),
            line(512, 52, 540, 52),
            line(540, 52, 540, 256),
            line(540, 256, 512, 256),
            box(565, 125, 220, 65, "Shared DFS / ordering"),
            line(512, 157, 565, 157),
            line(512, 257, 675, 257),
            line(675, 257, 675, 190),
            text(563, 217, "Domains + position masks", 16),
            text(20, 245, "Registry selects a strategy"),
            text(20, 275, "Result → independent verifier → render / status", 16),
        ],
    )
    ordered = sorted(rows, key=lambda r: r["elapsed"])
    floor, budget = 0.0001, 5.0

    def ypos(t):
        return 325 - 275 * (
            math.log10(max(floor, min(budget, t))) - math.log10(floor)
        ) / (math.log10(budget) - math.log10(floor))

    parts = [
        text(35, 25, "Sorted default-solver times (all 88 files)", 22),
        line(75, 50, 75, 325),
        line(75, 325, 785, 325),
    ]
    for tick in (0.0001, 0.001, 0.01, 0.1, 1, 5):
        y = ypos(tick)
        parts += [
            line(75, y, 785, y, "#ddd"),
            text(65, y + 5, str(tick), 14, anchor="end"),
        ]
    for rank, row in enumerate(ordered):
        x, y = 85 + rank * 7.9, ypos(row["elapsed"])
        color = BLUE if "/core/" in row["grid"] else ORANGE
        if row["status"] != "ok":
            parts.append(
                f'<polygon points="{x},{y-6} {x-6},{y+5} {x+6},{y+5}" fill="{color}"/>'
            )
            parts.append(text(x - 8, y + 22, "core/87 ≥ 5 s", 14, color, anchor="end"))
        else:
            parts.append(f'<circle cx="{x}" cy="{y}" r="3.3" fill="{color}"/>')
    parts += [
        text(5, 43, "s", 15),
        text(340, 355, "rank (ascending time)", 16),
        text(135, 385, "● core", 16, BLUE),
        text(300, 385, "● gecode", 16, ORANGE),
        text(475, 385, "▲ censored at 5 s", 16),
    ]
    save("times.svg", 810, 410, parts)
    grouped = defaultdict(list)
    for row in results["ablation"]:
        grouped[row["solver"]].append(row)
    labels = {
        "default": ("default", ""),
        "no_arc_consistency": ("no arc", "consistency"),
        "no_value_ordering": ("no value", "ordering"),
        "no_restarts": ("no restarts", ""),
        "no_degree": ("no degree", "tie-break"),
        "no_support_cache": ("no support", "cache"),
    }
    parts = [
        text(25, 25, "Isolated ablations: 3 grids × 3 seeds", 22),
        line(70, 90, 70, 345),
        line(70, 345, 815, 345),
    ]
    summaries = []
    for i, (name, group) in enumerate(grouped.items()):
        total = sum(r["elapsed"] for r in group)
        solved = sum(r["status"] == "ok" for r in group)
        nodes = sum(r["stats"]["nodes"] for r in group)
        x, h = 90 + 123 * i, 205 * total / 11
        parts += [
            f'<rect x="{x}" y="{345-h}" width="88" height="{h}" fill="{BLUE if name == "default" else ORANGE}"/>',
            text(x + 44, 345 - h - 40, f"{total:.3f} s", 15, anchor="middle"),
            text(x + 44, 345 - h - 23, f"{solved}/9 solved", 14, anchor="middle"),
            text(x + 44, 345 - h - 6, f"{nodes} nodes", 13, anchor="middle"),
        ]
        for j, label in enumerate(labels[name]):
            parts.append(text(x + 44, 370 + 18 * j, label, 15, anchor="middle"))
        summaries.append(
            {"name": name, "seconds": total, "solved": solved, "nodes": nodes}
        )
    for tick in (0, 2, 4, 6, 8, 10):
        parts.append(text(60, 350 - 205 * tick / 11, str(tick), 14, anchor="end"))
    save("ablation.svg", 850, 415, parts)
    grid = load_grid(ROOT / "grids/core/87.yaml")
    parts = [
        text(20, 25, "Core 87: four dense regions and four long linking words", 22)
    ]
    for r, pattern in enumerate(grid.pattern):
        for c, value in enumerate(pattern):
            fill = "#444" if value == "x" else "white"
            if value == "-" and c in (6, 8) and 1 <= r <= 13:
                fill = "#d8e5ed"
            if value == "-" and r in (6, 8) and 1 <= c <= 13:
                fill = "#f1ddca"
            parts.append(
                f'<rect x="{25+c*23}" y="{50+r*23}" width="23" height="23" fill="{fill}" stroke="#888" stroke-width="0.7"/>'
            )
    for slot in grid.slots:
        if slot.length == 12:
            r, c = slot.cells[0]
            parts.append(
                text(
                    27 + c * 23,
                    63 + r * 23,
                    slot.label,
                    10,
                    BLUE if slot.direction == "vertical" else ORANGE,
                    True,
                )
            )
    parts += [
        box(460, 75, 140, 65, "northwest"),
        box(650, 75, 140, 65, "northeast"),
        box(460, 280, 140, 65, "southwest"),
        box(650, 280, 140, 65, "southeast"),
        line(600, 107, 650, 107, ORANGE),
        line(600, 312, 650, 312, ORANGE),
        line(530, 140, 530, 280, BLUE),
        line(720, 140, 720, 280, BLUE),
        text(610, 96, "23h", 13, ORANGE, True),
        text(610, 335, "26h", 13, ORANGE, True),
        text(480, 213, "13v", 13, BLUE, True),
        text(735, 213, "16v", 13, BLUE, True),
        text(445, 380, "Schematic omits two central 3-letter slots.", 15),
        text(
            25,
            430,
            "54 slots; 185 crossings; no verified fill found in the recorded runs.",
            17,
        ),
    ]
    save("hardest.svg", 820, 455, parts)
    lexicon = load_dictionary(ROOT / "dictionaries/words_alpha.txt")
    log_expected = sum(math.log(len(lexicon.by_length[s.length])) for s in grid.slots)
    for i, edges in enumerate(grid.crossings):
        for edge in edges:
            if edge.other <= i:
                continue
            a, b = lexicon.index(grid.slots[i].length), lexicon.index(
                grid.slots[edge.other].length
            )
            probability = sum(
                am.bit_count() * bm.bit_count()
                for am, bm in zip(a.masks[edge.here], b.masks[edge.there])
            ) / (len(a.words) * len(b.words))
            log_expected += math.log(probability)
    headlines = []
    for solver in ("mac", "forward"):
        for family in ("all", "core", "gecode"):
            group = [
                r
                for r in results["suite"]
                if r["solver"] == solver
                and (family == "all" or f"/{family}/" in r["grid"])
            ]
            times = [r["elapsed"] for r in group if r["status"] == "ok"]
            headlines.append(
                {
                    "solver": solver,
                    "family": family,
                    "runs": len(group),
                    "solved": len(times),
                    "subsecond": sum(t < 1 for t in times),
                    "median": statistics.median(times),
                    "worst_solved": max(times),
                    "total": sum(r["elapsed"] for r in group),
                }
            )
    derived = {
        "environment": results["environment"],
        "headlines": headlines,
        "ablation": summaries,
        "hardest": {
            "slot_lengths": dict(Counter(s.length for s in grid.slots)),
            "crossings": 185,
            "independent_log10": log_expected / math.log(10),
            "thinning_proxy": math.exp(-log_expected / len(grid.slots)),
        },
    }
    (HERE.parent / "data.json").write_text(json.dumps(derived, indent=2) + "\n")
    local_data = ROOT / "benchmarks/local-search.json"
    if local_data.exists():
        (HERE.parent / "local-search.json").write_text(local_data.read_text())


if __name__ == "__main__":
    main()
