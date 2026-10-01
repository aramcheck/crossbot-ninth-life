# Crossbot

A validated crossword-filling compiler with independently verified output,
bit-parallel constraint propagation, and an extensible solver registry.

**Status: the goal is not fully reached.** On the recorded machine, `mac`
solved and verified **87/88 grids (98.86%)**,
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
not exposed). CPython **3.14.7**; **370,105** surviving
`words_alpha.txt` lines; seed **0**; **5 s** per run. Serial execution.
Solver time excludes grid/dictionary loading, indexing and verification,
as in the CLI specification. Dictionary loading took
**0.198 s**; total once-per-grid
preparation across the suite was **0.883 s**.
These are not cold-process end-to-end compiler times. Sub-millisecond times
are shown as `<0.001`; timeouts retain measured elapsed time, not zero.
The default median over solved runs was **0.036 s** and worst
solved run **0.271 s** (Gecode 45).

| Family | Grid | MAC time (s) | MAC status / nodes | Forward time (s) | Forward status / nodes |
|---|---:|---:|---|---:|---|
| gecode | 0 | 0.003 | ok / 6 | 0.001 | ok / 34 |
| gecode | 1 | 0.002 | ok / 9 | <0.001 | ok / 9 |
| gecode | 2 | 0.002 | ok / 9 | <0.001 | ok / 9 |
| gecode | 3 | 0.001 | ok / 9 | <0.001 | ok / 9 |
| gecode | 4 | 0.001 | ok / 27 | <0.001 | ok / 9 |
| core | 5 | 0.001 | ok / 9 | <0.001 | ok / 9 |
| gecode | 5 | 0.003 | ok / 9 | 0.001 | ok / 9 |
| gecode | 6 | 0.002 | ok / 9 | <0.001 | ok / 8 |
| gecode | 7 | 0.002 | ok / 9 | <0.001 | ok / 9 |
| gecode | 8 | 0.001 | ok / 9 | <0.001 | ok / 9 |
| gecode | 9 | <0.001 | ok / 9 | <0.001 | ok / 26 |
| gecode | 10 | 0.039 | ok / 72 | 0.012 | ok / 124 |
| gecode | 11 | 0.034 | ok / 73 | 0.021 | ok / 549 |
| gecode | 12 | 0.040 | ok / 73 | 0.013 | ok / 73 |
| gecode | 13 | 0.032 | ok / 69 | 0.014 | ok / 473 |
| gecode | 14 | 0.034 | ok / 73 | 0.010 | ok / 75 |
| gecode | 15 | 0.047 | ok / 67 | 0.027 | ok / 478 |
| gecode | 16 | 0.042 | ok / 64 | 0.011 | ok / 89 |
| gecode | 17 | 0.033 | ok / 86 | 0.012 | ok / 84 |
| gecode | 18 | 0.034 | ok / 78 | 0.021 | ok / 344 |
| gecode | 19 | 0.044 | ok / 66 | 0.012 | ok / 202 |
| gecode | 20 | 0.076 | ok / 122 | 0.025 | ok / 259 |
| gecode | 21 | 0.069 | ok / 108 | 0.021 | ok / 180 |
| gecode | 22 | 0.079 | ok / 109 | 0.104 | ok / 2037 |
| gecode | 23 | 0.059 | ok / 124 | 0.039 | ok / 611 |
| gecode | 24 | 0.058 | ok / 118 | 0.017 | ok / 126 |
| gecode | 25 | 0.065 | ok / 120 | 0.018 | ok / 136 |
| gecode | 26 | 0.066 | ok / 127 | 0.022 | ok / 148 |
| gecode | 27 | 0.073 | ok / 122 | 0.023 | ok / 147 |
| gecode | 28 | 0.058 | ok / 123 | 0.018 | ok / 180 |
| gecode | 29 | 0.064 | ok / 122 | 0.018 | ok / 120 |
| gecode | 30 | 0.112 | ok / 129 | 0.076 | ok / 1138 |
| gecode | 31 | 0.106 | ok / 139 | 0.033 | ok / 257 |
| gecode | 32 | 0.096 | ok / 136 | 0.037 | ok / 345 |
| gecode | 33 | 0.144 | ok / 144 | 0.274 | ok / 3078 |
| gecode | 34 | 0.116 | ok / 150 | 0.066 | ok / 650 |
| gecode | 35 | 0.106 | ok / 140 | 0.030 | ok / 193 |
| gecode | 36 | 0.096 | ok / 144 | 0.181 | ok / 3006 |
| gecode | 37 | 0.105 | ok / 143 | 0.032 | ok / 143 |
| gecode | 38 | 0.119 | ok / 142 | 0.032 | ok / 141 |
| gecode | 39 | 0.162 | ok / 179 | 0.351 | ok / 5170 |
| gecode | 40 | 0.098 | ok / 152 | 0.144 | ok / 2154 |
| gecode | 41 | 0.123 | ok / 175 | 0.099 | ok / 1043 |
| gecode | 42 | 0.124 | ok / 158 | 0.650 | ok / 12173 |
| gecode | 43 | 0.158 | ok / 153 | 0.046 | ok / 208 |
| gecode | 44 | 0.152 | ok / 174 | 0.045 | ok / 229 |
| gecode | 45 | 0.271 | ok / 213 | 5.000 | FAIL / 63190 |
| gecode | 46 | 0.143 | ok / 170 | 0.039 | ok / 208 |
| gecode | 47 | 0.151 | ok / 156 | 0.126 | ok / 1030 |
| gecode | 48 | 0.160 | ok / 165 | 0.294 | ok / 3086 |
| gecode | 49 | 0.207 | ok / 197 | 0.348 | ok / 4918 |
| gecode | 50 | <0.001 | ok / 2 | <0.001 | ok / 2 |
| core | 51 | 0.031 | ok / 79 | 0.009 | ok / 80 |
| gecode | 51 | <0.001 | ok / 5 | <0.001 | ok / 5 |
| gecode | 52 | <0.001 | ok / 7 | <0.001 | ok / 7 |
| gecode | 53 | 0.001 | ok / 9 | <0.001 | ok / 9 |
| gecode | 54 | 0.001 | ok / 10 | <0.001 | ok / 10 |
| core | 55 | 0.037 | ok / 75 | 0.013 | ok / 75 |
| gecode | 55 | 0.002 | ok / 10 | 0.001 | ok / 10 |
| gecode | 56 | 0.002 | ok / 16 | 0.001 | ok / 16 |
| core | 57 | 0.034 | ok / 75 | 0.012 | ok / 75 |
| gecode | 57 | 0.004 | ok / 24 | 0.002 | ok / 22 |
| gecode | 58 | 0.005 | ok / 16 | 0.002 | ok / 16 |
| gecode | 59 | 0.005 | ok / 19 | 0.002 | ok / 19 |
| gecode | 60 | 0.006 | ok / 17 | 0.002 | ok / 16 |
| gecode | 61 | 0.005 | ok / 25 | 0.003 | ok / 25 |
| gecode | 62 | 0.008 | ok / 31 | 0.003 | ok / 31 |
| gecode | 63 | 0.009 | ok / 26 | 0.004 | ok / 26 |
| gecode | 64 | 0.012 | ok / 43 | 0.005 | ok / 77 |
| gecode | 65 | 0.019 | ok / 61 | 0.008 | ok / 63 |
| gecode | 66 | 0.038 | ok / 85 | 0.013 | ok / 82 |
| gecode | 67 | 0.030 | ok / 77 | 0.011 | ok / 78 |
| gecode | 68 | 0.037 | ok / 74 | 0.014 | ok / 177 |
| gecode | 69 | 0.008 | ok / 23 | 0.003 | ok / 23 |
| gecode | 70 | 0.018 | ok / 61 | 0.008 | ok / 59 |
| gecode | 71 | 0.014 | ok / 53 | 0.007 | ok / 205 |
| core | 74 | 0.030 | ok / 69 | 0.012 | ok / 72 |
| core | 75 | 0.029 | ok / 80 | 0.010 | ok / 78 |
| core | 82 | 0.029 | ok / 81 | 0.012 | ok / 82 |
| core | 83 | 0.039 | ok / 74 | 0.012 | ok / 81 |
| core | 84 | 0.037 | ok / 70 | 0.012 | ok / 86 |
| core | 85 | 0.049 | ok / 64 | 0.035 | ok / 577 |
| core | 86 | 0.036 | ok / 72 | 0.008 | ok / 79 |
| core | 87 | 5.000 | FAIL / 6255 | 5.000 | FAIL / 83715 |
| core | 88 | 0.068 | ok / 96 | 0.159 | ok / 3955 |
| core | 89 | 0.034 | ok / 77 | 0.012 | ok / 77 |
| core | 90 | 0.222 | ok / 535 | 0.017 | ok / 217 |
| core | 92 | 0.035 | ok / 77 | 0.013 | ok / 126 |

### Remaining work

Core 87 needs a materially stronger search mechanism or a reliable structural
decomposition, not merely a more generous hidden timeout. The report records
negative experiments, an explicit absence of a state-of-the-art claim, and
evidence-backed improvement opportunities. No suite-wide success is claimed.
