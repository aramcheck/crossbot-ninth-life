# Technical analysis

`analysis.pdf` is an interim technical report of the shipped system and its
measurements, **not a claim that the all-grid performance goal has been met**.
Core grid 87 remains unresolved. Its timeout is retained in the charts and
full README benchmark table.

## Layout

- `analysis.typ`: title, abstract, ordered sections and IEEE bibliography.
- `sections/01-context.typ` … `07-conclusions.typ`: seven frozen main sections.
- `sections/appendix-a.typ`: subsequent unshipped min-conflicts experiment.
- `shared.typ`: typography helpers and data access.
- `references.bib`: primary-source and engineering-interface references.
- `diagrams/*.svg`: six deterministic vector figures.
- `diagrams/generate.py`: standard-library SVG/data generator (imports the
  project's own grid and dictionary modules, no plotting dependency).
- `data.json`: summaries derived from `../benchmarks/results.json`.
- `local-search.json`: copied experiment data derived by the same generator.
- `research-notes.md`: literature-search scope and limitations.
- `analysis.pdf`: compiled report, kept in sync with its sources.

## Build and regenerate

Typst >= 0.13 is required; this repository's output was built with 0.15.1.
From the repository root:

```sh
uv sync
uv run python tools/measure.py
uv run python tools/audit_results.py
uv run python documentation/diagrams/generate.py  # all six SVGs + data.json
uv run python tools/summarize.py                 # README table + suite.csv
cd documentation && typst compile analysis.typ
```

To rebuild only the PDF:

```sh
cd documentation && typst compile analysis.typ
```

No package downloads are needed by Typst. The report uses the bundled
Libertinus Serif face and DejaVu Sans Mono, A4 pages, numbered headings,
label-based cross-references, captioned figures/tables and a running header
on pages after the first. Rebuilding SVGs/data is deterministic for the same
raw measurement artifact. Rerunning timings is inherently not byte-identical.
Regenerate derived files and the PDF together after changing measurements.
The measurement collector preserves failures and exits 0; the production
`benchmark` command, not that collector, is the regression gate.

## Notes on the data

Every primary number comes from the serial campaign in
`../benchmarks/results.json`: Apple-vendor aarch64 Linux 6.18.15 VM, five
exposed vCPUs, 7.9 GiB RAM, physical host model unavailable; CPython 3.14.7;
`words_alpha.txt`, 370,105 surviving lines (SHA-256 in the artifact);
five seconds per solver run. Complete-suite/cross-solver measurements use
seed 0; isolated ablations on core 90 and Gecode 45/49 use seeds 0, 1, 2.
Solver timing excludes input/index preparation and independent verification;
the dictionary load and problem preparation are separately reported.
Cold-process end-to-end suite performance has not been measured.

Core 87's alternative-dictionary campaign uses the same machine/interpreter,
five seconds, seeds 0, 1, 2, and 370,105 English / 225,349 UK-English /
109,419 Spanish surviving lines, with individual fingerprints recorded.
Every persisted successful assignment was independently verified both at
collection and by `audit_results.py`. Failed runs are censored, not proofs of
unsatisfiability. The independent-letter boundary proxy uses the original
English dictionary masks and exact core-87 geometry; it is an explicitly
uncalibrated diagnostic, not an observed phase transition.

Exploratory logs in `../benchmarks/exploration/` precede the final code;
their README documents the same machine/interpreter and each budget. These
are negative observations, not reproducible head-to-head benchmarks because
the intermediate prototypes were reverted. The main text states that limit.

Appendix A records an additional unshipped min-conflicts campaign: same
machine and interpreter, core 87 only, all three dictionaries, seeds 0/1/2,
five seconds per run, fixed noise settings 0.02 and 0.10. All eighteen runs
were censored without a fill. Reproduce with
`uv run python tools/local_search_experiment.py`; then regenerate report data,
figures and the PDF. Its work statistic is repair replacements, not DFS nodes.
The production source and original measurements did not change.

The report's seven sections are frozen before any subsequent solver campaign.
Further work is recorded in appendices rather than retroactively rewriting
predictions or attributing new measurements to the original implementation.
