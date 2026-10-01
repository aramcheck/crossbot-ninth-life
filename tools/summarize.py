"""Generate the complete README benchmark table and lossless CSV summary."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    data = json.loads((ROOT / "benchmarks/results.json").read_text())
    summary = json.loads((ROOT / "documentation/data.json").read_text())
    default = summary["headlines"][0]
    text = f"""# Crossbot

A validated crossword-filling compiler with independently verified output,
bit-parallel constraint propagation, and an extensible solver registry.

**Status: the goal is not fully reached.** On the recorded machine, `mac`
solved and verified **{default['solved']}/{default['runs']} grids (98.86%)**,
all successful runs below one second. Core grid **87 remains unresolved**:
no fill and no unsatisfiability proof was obtained. Neither shipped solver
meets the all-grids-under-five-seconds exit condition. The benchmark gate
correctly exits 1 on the full suite; this is not hidden as a success.

## Setup and commands

Requires Python 3.14+, [uv](https://docs.astral.sh/uv/), and (for the report)
Typst 0.13+. No external solving library is used. The dependency-free local
build backend installs console entry points; `uv.lock` pins the permitted
runtime/development dependencies and their transitive dependencies.

```sh
uv sync
uv run crossbot list-solvers
uv run crossbot grid-info grids/core/5.yaml
uv run crossbot solve grids/core/5.yaml dictionaries/words_alpha.txt
uv run crossbot solve grids/core/5.yaml dictionaries/words_alpha.txt --seed 0 --timeout 5 -w 1h:aas
# Equivalent module / compatibility entry points:
uv run python -m crossbot list-solvers
uv run python main.py list-solvers
```

Dictionary lines are lowercased, not accent-stripped; invalid lines are
silently discarded, and their surviving order is preserved. Lock words
are accent-stripped with `ñ` preserved and are exempt from membership.
Locks must have valid keys, lengths, unique words and consistent crossings.
Grid metadata is checked against derived geometry, not trusted.

## Benchmarks and regression checks

```sh
# Start with core, then expand to Gecode. The full core gate currently fails on 87.
uv run benchmark --grid-dir grids/core --timeout 5
uv run benchmark --grid-dir grids/gecode --timeout 5
uv run benchmark --solvers mac,forward --seeds 0,1,2 --timeout 5
uv run benchmark --grids 5,51 --dict dictionaries/uk220k.txt
# Every returned fill is verified; INVALID and FAIL both make benchmark exit 1.
uv run pytest
uv run mypy
uv run black --check src tests tools documentation/diagrams/generate.py build_backend.py main.py
```

`--grids` filters integer file basenames, so an ID shared by two families
selects both files. Files are scanned recursively and sorted numerically.
`--timeout` is a positive finite per-solver-run wall-clock budget.
Deadlines are cooperatively checked using a monotonic performance counter;
a running operation may overshoot by its bounded cost / OS scheduling delay.
A timeout is **not** a proof that no fill exists.

### Reproduce all committed evidence

```sh
uv run python tools/measure.py       # suite, solver comparison, isolated ablations, 87 with all dictionaries
uv run python tools/audit_results.py
uv run python documentation/diagrams/generate.py
uv run python tools/summarize.py
(cd documentation && typst compile analysis.typ)
```

`measure.py` records failures as data and therefore exits 0; use `benchmark`
for a gating exit code. `benchmarks/results.json` includes verified witnesses,
full-precision times, work counts, interpreter/platform details and source /
dictionary SHA-256 hashes. CSV: `benchmarks/suite.csv`.
The report is in `documentation/analysis.pdf`; see its README for provenance.

## Design and adding a solver

- `src/crossbot/grid.py`: schema validation, numbering and crossing topology.
- `lexicon.py`, `problem.py`: stable dictionary indexes and thematic locks.
- `solvers/propagation.py`: reversible integer domains and letter support sets.
- `solvers/ordering.py`: MRV, degree ties and sampled least-constraining values.
- `solvers/search.py`: depth-first search and geometric restarts.
- `solvers/api.py`: solver contract; `solvers/__init__.py`: registrations.
- `verify.py`: independent membership, coverage, crossings and uniqueness checks.
- `cli.py`, `benchmark.py`, `runner.py`, `render.py`: solver-neutral frontends.

To add a strategy, implement `(Problem, seed: int, deadline: float) -> Result`
and register one `Solver` in `solvers/__init__.py`. The deadline is an absolute
`perf_counter()` value. Return `solved`, `unsatisfiable`, or `timeout`, with
an assignment keyed by slot index (not key number). Always report the same
statistics keys; names match `[a-z_]+`, values are finite numbers. Exactly one
registration is default. Neither frontend needs a strategy-specific change.

`mac` is the default: maintaining arc consistency reduces failures on the
hard cases. `forward` is the lower-overhead baseline; it is faster on many
easy grids but failed Gecode 45 as well as core 87 in this seed-0 campaign.
Both use the same seeded ordering and restart machinery. There is no
precomputed-fill cache, special-case grid solver, or parallel worker.

## Complete benchmark results

Machine: Apple-vendor aarch64 Linux VM, 5 vCPUs, 7.9 GiB RAM (host model
not exposed). CPython **{data['environment']['python']}**; **370,105** surviving
`words_alpha.txt` lines; seed **0**; **5 s** per run. Serial execution.
Solver time excludes grid/dictionary loading, indexing and verification,
as in the CLI specification. Dictionary loading took
**{data['environment']['dictionary_load_seconds']:.3f} s**; total once-per-grid
preparation across the suite was **{sum(r['preparation'] for r in data['suite'] if r['solver']=='mac'):.3f} s**.
These are not cold-process end-to-end compiler times. Sub-millisecond times
are shown as `<0.001`; timeouts retain measured elapsed time, not zero.
The default median over solved runs was **{default['median']:.3f} s** and worst
solved run **{default['worst_solved']:.3f} s** (Gecode 45).

| Family | Grid | MAC time (s) | MAC status / nodes | Forward time (s) | Forward status / nodes |
|---|---:|---:|---|---:|---|
"""
    grouped = {}
    for row in data["suite"]:
        grouped.setdefault(row["grid"], {})[row["solver"]] = row
    for path, runs in grouped.items():
        a, b = runs["mac"], runs["forward"]

        def time(row):
            return "<0.001" if row["elapsed"] < 0.001 else f"{row['elapsed']:.3f}"

        text += f"| {path.split('/')[1]} | {a['id']} | {time(a)} | {a['status']} / {a['stats']['nodes']} | {time(b)} | {b['status']} / {b['stats']['nodes']} |\n"
    text += "\n### Remaining work\n\nCore 87 needs a materially stronger search mechanism or a reliable structural\ndecomposition, not merely a more generous hidden timeout. The report records\nnegative experiments, an explicit absence of a state-of-the-art claim, and\nevidence-backed improvement opportunities. No suite-wide success is claimed.\n"
    (ROOT / "README.md").write_text(text)
    with (ROOT / "benchmarks/suite.csv").open("w", newline="") as stream:
        fields = [
            "grid",
            "id",
            "solver",
            "seed",
            "budget",
            "preparation",
            "elapsed",
            "status",
            "reason",
            "nodes",
            "backtracks",
            "revisions",
            "restarts",
        ]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in data["suite"]:
            writer.writerow(
                {key: row.get(key, row["stats"].get(key)) for key in fields}
            )


if __name__ == "__main__":
    main()
