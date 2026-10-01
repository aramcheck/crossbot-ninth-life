#import "../shared.typ": *
#let local = json("../local-search.json")
#heading(numbering: none)[Appendix A: subsequent unshipped min-conflicts campaign]
#counter(heading).update(0)
#set heading(numbering: (..numbers) => "A." + numbers.pos().map(str).join("."))

= Prediction inherited from the frozen main text
The main text identifies core 87 as unresolved and predicts that a materially different search structure or stronger guidance may be needed. It does *not* predict that a larger hidden timeout, a low mismatch count or a local optimum certifies a fill. After freezing sections 1–7, we tested a separate heuristic-repair approach; those sections and their original measurements remain unchanged. This appendix records a negative experiment, not an improvement to the shipped default.

= Method and parameter protocol
`tools/local_search_experiment.py` implements an unregistered min-conflicts-style repair experiment, related to Minton and colleagues' established heuristic @minton92. It begins with independent dictionary words of each required length while maintaining global uniqueness. At each step it chooses uniformly among slots with at least one disagreement. A replacement word must not already occur in another slot. A bitset dynamic program computes domains grouped by exact Hamming disagreement with the current crossing letters: matching a letter leaves its cost unchanged; mismatching advances to the next cost bucket. The first nonempty bucket gives all minimum-conflict replacements; a uniform random live ID breaks ties. With noise probability `p`, the algorithm instead picks an arbitrary available word. After 2,000 repairs it restarts from a new distinct random assignment.

We selected `p = 0.02` and `p = 0.10` as two exploratory, fixed low/high noise settings before this campaign. Neither was trained or promoted based on the outcomes. The sole test case was core 87; there is no train/held-out split and no generalization claim. Each setting used seeds 0, 1, 2, the three supplied dictionaries and five seconds per run on the same Apple-vendor aarch64 VM and CPython 3.14.7 as the main campaign. All time, including restarts and repair selection, is charged inside that solver budget; loading/indexing is excluded as before. The script checks any zero-conflict assignment independently with `verify`. No zero-conflict assignment was returned.

This experiment does not support locks, completeness or unsatisfiability proofs and is not registered as a shipped solver. Reproduction command: `uv run python tools/local_search_experiment.py`. It writes `benchmarks/local-search.json`. The objective counts each mismatched crossing once; its “steps” count replacements, not the default engine's assignment nodes. These work units must not be compared as if they had identical cost.

= Measurements and comparison
#figure(table(columns: (1.8fr, auto, auto, auto, auto), inset: 5pt,
  table.header([*Dictionary*], [*Noise*], [*Time*], [*Repair steps*], [*Best errors*]),
  ..("words_alpha.txt", "uk220k.txt", "words.es.rae.txt").map(name => {
    (0.02, 0.1).map(noise => {
      let rows = local.filter(r => r.dictionary == name and r.noise == noise)
      (raw(name), str(noise), seconds(rows.map(r => r.elapsed).fold(0, (a, b) => a + b)), str(rows.map(r => r.steps).fold(0, (a, b) => a + b)), str(calc.min(..rows.map(r => r.best_crossing_errors))))
    }).flatten()
  }).flatten(),
), kind: table, caption: [Subsequent core-87 min-conflicts experiment: each row sums three seeds 0, 1, 2 at 5 s each, same machine/interpreter as the main report; dictionary counts 370,105 / 225,349 / 109,419 respectively. Every run is censored; no zero-time imputation. “Best errors” is the minimum recorded crossing disagreements, not a success or boundary certificate.]) <tab:local>

All 18 runs timed out without a verified fill. The smallest recorded disagreement count was 17 crossing errors; none reached zero. The main default comparison also timed out for core 87 across all three dictionaries and seeds 0, 1, 2. This is no solved-run improvement over that common dictionary/seed/budget baseline. Lower repair noise reached smaller mismatch minima in this campaign, but that cannot be translated into a measured success probability or a feasibility-distance estimate.

= Verdict, regression status and next action
The experiment did not reach the missing exit condition and was not promoted into the production registry. The production source fingerprint and both shipped strategies are unchanged, so no algorithmic regression to the rest of the suite is implied; we did not re-time unrelated grids for an unshipped script. The existing 105 tests, strict mypy check and Black check remained passing after the campaign, and persisted baseline fills remained independently verifiable. The report and bibliography compile without warnings after adding this appendix.

The next action is still to obtain a witness or sound stronger-search result for core 87. A local-repair attempt with many inexpensive moves has now been measured, but a low mismatch count is not a replacement for a solution. No new principle or state-of-the-art claim follows from this negative campaign.
