# crossbot — analysis document specification

This document specifies the written analysis that must accompany the
crossbot implementation once the goal in `goal.spec.md` has been reached. It
defines where the document lives, how it is built, which sections and
figures it must contain, and the standard of evidence and tone it must meet.
It says nothing about what the analysis should conclude: the content is
whatever the implementation and its measurements honestly support.

## 1. Purpose and audience

The analysis is an academic-style technical report about the system that
was actually built. Its reader is a competent engineer or researcher who
has the repository in front of them and wants to know three things:

1. **What was built** — precisely enough that the default solver could be
   reimplemented from the report alone.
2. **Where every idea came from** — each mechanism traced to its origin in
   the published literature, or explicitly marked as untraced.
3. **What the evidence shows** — what was measured, what the measurements
   attribute the observed performance to, what is new, what remains open.

The report is not marketing and not a changelog. Every claim in it must be
traceable to a measurement in the report, a cited source, or a location in
the code.

## 2. Location, format and build

| item             | requirement                                                                  |
| ---------------- | ---------------------------------------------------------------------------- |
| directory        | `documentation/` at the repository root                                      |
| typesetting      | [Typst](https://typst.app) ≥ 0.13, no other toolchain                        |
| entry point      | `documentation/analysis.typ` (title, abstract, includes, bibliography)       |
| sections         | one file per section under `documentation/sections/`, included in order      |
| bibliography     | `documentation/references.bib` in BibTeX, rendered in IEEE style             |
| figures          | `documentation/diagrams/*.svg` (see section 3)                               |
| compiled output  | `documentation/analysis.pdf`, committed and kept in sync with the sources    |
| build command    | `cd documentation && typst compile analysis.typ`                             |
| readme           | `documentation/README.md`: layout, build and regeneration commands, and a "notes on the data" paragraph stating the machine, interpreter, dictionary, time budget and seeds behind every reported number |

The build must complete with no warnings about unresolved references,
missing figures or missing bibliography keys.

**House style.** A4 paper; numbered headings (`1.1`); a running header on
every page after the first; justified serif body text; monospace `raw`
for identifiers, file names and command output; numbered figures and
tables, each with a caption; cross-references by label (`@sec:…`,
`@fig:…`, `@tab:…`) rather than by hard-coded number; the bibliography
placed after the conclusions and before any appendix.

## 3. Figures

All figures are **SVG**. Raster formats, screenshots and embedded bitmaps
are not accepted. Figures may be hand-authored or generated; if generated,
the generator (for example `documentation/diagrams/generate.py`) is
committed, deterministic, dependency-free beyond the project's allowed
dependencies, and regenerates every figure with one command documented in
the readme.

Figures share one visual vocabulary: a serif face matching the body text, a
monospace face for identifiers, at most two accent colours plus greys, a
white background, and text that stays legible when the figure is set at
full page width.

**Mandatory figures.** The report contains at least one figure of each of
the following kinds (more are welcome). Their subjects are described
generically because they depend on what was built:

| #   | subject                                                                                                                                     |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| F1  | the central data representation the default solver works on, and the elementary operation it performs on that representation, shown on a small concrete example |
| F2  | the control flow of the default solver: what happens in one step of its main loop and, if it has one, the outer loop around it              |
| F3  | how the default solver relates to the shared machinery and to the other solvers (architecture / data-flow view), including any staging or sub-problem structure it uses |
| F4  | sorted per-grid solve times of the default solver over the entire grid suite, log scale, the two grid families visually distinguished, unsolved grids shown censored at the budget |
| F5  | the attribution study of section 4.4: one bar per configuration, annotated with total time, number of runs solved and the solver's own work statistic |
| F6  | the structure of the hardest grid(s) in the suite, drawn so that the reader can see why it is hard                                          |

Every caption states what is shown, the data behind it (dictionary, seeds,
time budget, machine) and how zero or censored readings were plotted.

## 4. Required content

The report consists of a title block, an abstract, seven numbered sections,
a bibliography and, when applicable, appendices. The section titles below
are the expected ones; the questions listed under each are what the section
must answer. How they are answered is entirely determined by the system and
its measurements.

**Title and abstract.** A descriptive title naming the system and its
central technique(s) in the report's own words. The abstract (≤ 250 words)
states: what the system does, the headline numbers (grid count, budget,
share solved, share under one second), that the lineage of every technique
was traced, what the attribution study found, what is claimed as new, and
what remains open.

### 4.1 Context

- Problem statement in the report's own words (grid, slots, crossings,
  distinctness, locked words).
- Known computational complexity of the problem, with citations to the
  results that establish it.
- Prior work on automatic construction and filling of this kind of puzzle,
  from the earliest published attempts to the most recent, each cited and
  characterised in a sentence. Include systems that solve clued puzzles if
  their filling stage faces the same combinatorial core.
- Scope of the report as an explicit list of questions, each pointing to
  the section that answers it.

### 4.2 The System

- The implementation as shipped, described bottom-up: how the problem is
  modelled, the core data structures, the shared machinery, each solver
  strategy and its one-line role, and which one is the default and why.
- The default solver's mechanisms spelled out precisely — every choice
  point, every parameter and its shipped value — so the reader could
  reimplement it. Figures F1–F3 belong here.
- Anything the system does that is _not_ exercised by the benchmark suite
  must be identified as such.

### 4.3 Intellectual Lineage

This section is critical and is held to a strict standard.

- A table with exactly these columns: **Mechanism in crossbot** |
  **Established origin** | **Deviation / refinement**. One row per
  mechanism used by any shipped solver, including the problem model itself,
  every data structure, every ordering or selection rule, every pruning or
  filtering step, every randomisation or scheduling device, and every
  structural splitting of the problem into parts.
- Each **Established origin** cell cites the primary source(s) — the paper,
  book or well-known system that first described the idea — not a survey
  or textbook unless that is where it originated. If no origin can be
  found after a genuine search, the cell reads "not found in the surveyed
  literature" and the prose explains what was searched.
- Each **Deviation** cell states how the implementation differs from the
  cited source, or "none". A row may be tagged _new device_ only if
  section 4.5 defends that tag.
- Prose after the table discusses every row whose correspondence to its
  source is inexact: that is where the system's own contributions, if any,
  live. Related but distinct ideas in the literature are named and cited
  so that the reader can judge the distance.
- Where the crossword-specific literature and the general literature
  diverge — a technique standard in one but absent from the other — say so.

### 4.4 Empirical Evaluation

- **Setup**: machine, interpreter and version, dictionary and its size,
  per-run budget, seeds, and the statement that every returned fill was
  independently re-verified.
- **Headline results** over both grid families with figure F4: share
  solved, share under one second, median and worst solve time, and the
  identity of any unsolved grid.
- **Cross-solver comparison** on the harder family: what each shipped
  solver achieves, with a paragraph on what the raw numbers reveal about
  the trade-offs between them.
- **Structural findings**: any property of the benchmark suite discovered
  during the analysis that changes how the results must be read (for
  instance a mechanism that never activates on any suite grid). Such a
  finding must be reported even when it weakens the story.
- **Attribution (ablation) study** with figure F5: on the hardest grids
  that are known to have a fill, with at least three seeds each, toggle
  each feature of the default solver individually and report total time,
  runs solved and the solver's work statistic per configuration. State the
  conclusions explicitly and rank the features by contribution. If a
  configuration present in the code but not shipped outperforms the
  default, say so plainly.
- **The hardest instance(s)** with figure F6: how much compute was spent
  on it and how, what its structure is, an estimate of how close it sits
  to the boundary between having and lacking a fill (with the estimation
  method cited), and an explicit statement of whether it is known to have
  a fill, known not to, or open.

### 4.5 Novelty Assessment

Held to the standard of an archival venue: a technique is _established_ if
any prior publication describes it, whether or not the implementers knew of
it.

- **What is established** — list with citations.
- **What is a novel combination for this problem** — which established
  techniques have not previously been documented together for this
  problem, and where the problem-specific literature stopped, with citations.
- **What is novel as an individual device** — each candidate described
  conservatively, its nearest published neighbours cited, and a verdict:
  novel principle, novel application of a known principle, or engineering
  device not worth a paper on its own. An untested idea is labelled as
  such.
- **Is it state of the art?** — answered with the evidence that supports a
  claim and the evidence that is missing (uncontrolled comparisons,
  absent baselines, hardware and dictionary differences). A state-of-the-art
  claim without a controlled head-to-head comparison is not permitted; the
  defensible statement must be spelled out in one sentence.

### 4.6 Improvement Opportunities

Three tiers, each item one paragraph:

1. **Immediate, evidence-backed** — changes justified by this report's own
   measurements, with the expected gain quantified from those measurements.
2. **Established engineering upgrades** — techniques from the literature
   with known payoffs that the system does not yet use, cited.
3. **Research directions** — open questions the analysis raised, including
   what corpus or experiment would be needed to answer each.

### 4.7 Conclusions

About one page: the lineage verdict, the empirical hierarchy of what
matters, the measured position relative to the state of the art, and the
concrete next steps. No new results.

### Bibliography

- Every citation key in the text resolves; every entry is cited at least
  once.
- Entries carry author, title, venue, year and a DOI or URL where one
  exists.
- Coverage must include the complexity results of 4.1, every prior
  construction system named in 4.1, and the origin of every row in the
  lineage table of 4.3. As a floor for coverage, not a quota, expect on the
  order of thirty or more entries.

### Appendices (conditional)

If work on the system continues after the main text is written, sections
1–7 are **frozen** as the pre-registration of what was predicted, and each
further campaign becomes an appendix (`A`, `B`, …) recording: what the main
text predicted, what was changed in the code, how any constants were chosen
(protocol, metric, train/held-out split), before/after measurements on the
same machine and dictionary, whether the rest of the suite regressed, and
the status of the test suite, type checker and formatter afterwards.
Appendix headings are numbered `A.1`, `B.1`, … and appendices follow the
bibliography.

## 5. Tone and evidence rules

- First-person plural ("we") for the authors' actions; present tense for
  the system, past tense for experiments.
- Measured and sceptical. Prefer "the evidence is consistent with" to
  "shows"; separate what was measured from what is conjectured; report
  negative results and reverted experiments alongside positive ones.
- Every number in prose has its provenance stated (seed, budget, machine)
  or points to a table or figure that states it.
- Every mechanism is classified explicitly as established, novel
  application, novel device, or untested idea; the classifications in 4.3
  and 4.5 must agree.
- Claims about the code (test count, type-checking status, formatting) are
  made only when the repository at the cited commit backs them.
- No superlatives without a measurement, no comparison without a stated
  baseline, no "fast" without a number.

## 6. Acceptance checklist

- [ ] `typst compile analysis.typ` succeeds with no warnings.
- [ ] Abstract, sections 4.1–4.7 and bibliography present; appendices only
      if applicable.
- [ ] Figures F1–F6 present as SVG under `documentation/diagrams/`, each
      referenced from the text, each with a caption meeting section 3.
- [ ] Lineage table present with a citation or an explicit
      "not found" statement on every row.
- [ ] Every `@key` resolves; every bibliography entry is cited.
- [ ] `documentation/README.md` explains how to rebuild the PDF and the
      figures and states the data provenance.
- [ ] `documentation/analysis.pdf` matches the committed sources.
