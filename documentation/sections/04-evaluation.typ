#import "../shared.typ": *
= Empirical Evaluation <sec:evaluation>

== Setup and evidence protocol
We ran serially in a Linux 6.18.15 aarch64 virtual machine with Apple vendor identification, five exposed vCPUs and approximately 7.9 GiB RAM; the physical host model is not exposed. The interpreter was CPython 3.14.7. The primary dictionary was `dictionaries/words_alpha.txt`, with 370,105 surviving lines and SHA-256 `3ed0c94610d8bcf7c11bbb49c56aa49c7234d32b66824df91f554169e572da48`. `tools/measure.py` records the source hash, the environment, budgets, seeds, elapsed times and witnesses in `benchmarks/results.json`. Every returned assignment was independently verified before recording success. `tools/audit_results.py` subsequently reverified all 225 persisted successful fills; 14 censored/failing runs were retained explicitly across the suite, ablation and alternative-dictionary campaigns.

The complete suite uses seed 0 and a five-second budget for each solver run. Ablations use seeds 0, 1 and 2 at the same budget. Each problem is built once, then shared across strategies; solvers own independent mutable search state. `perf_counter` measures solver wall time, excluding dictionary loading, geometry/index preparation and verification. The primary dictionary load took 0.198 s; once-per-grid preparation summed to 0.883 s across all 88 files. Indexes are lazy and reused, so these preparation numbers are not equivalent to 88 fresh-process compilations. The code source digest is checked during artifact auditing. No timing confidence intervals or multiple-machine measurements were collected; millisecond differences should not be treated as statistically settled.

== Headline results
The default strategy solved *87/88 files (98.86%)*; all 87 successful seed-zero runs were below one second. Thus the under-one-second share of the entire suite is also 98.86% in this solver-time metric. The median over successful runs was 0.036 s, and the worst successful run was Gecode 45 at 0.271 s. Core 87 reached the budget without a fill (measured wall time 5.000134 s, not a zero reading). It is the only default-solver failure. The core and Gecode files sharing numeric IDs are distinct instances; the count is by file, not by unique ID.

#figure(
  table(columns: (auto, auto, auto, auto, auto, auto, auto), inset: 4pt,
    table.header([*Solver*], [*Family*], [*Runs*], [*Solved*], [*< 1 s*], [*Median solved*], [*Worst solved*]),
    ..data.headlines.map(r => (raw(r.solver), r.family, str(r.runs), str(r.solved), str(r.subsecond), seconds(r.median), seconds(r.worst_solved))).flatten(),
  ), kind: table,
  caption: measured-caption([Complete-suite summary. Medians/worst values exclude failures, but the denominators and subsecond counts include all selected files. No zero timings occur; failures remain censored, not imputed as solved.]),
) <tab:headline>

#diagram("times.svg", measured-caption([F4. Sorted default-solver wall times for every supplied file, logarithmic vertical scale; colours distinguish grid families.], extra: [The failed core 87 run is a triangle at the 5 s budget. Positive readings below 0.0001 s are plotted at that floor; there are no measured zero readings.])) <fig:times>

The all-grids exit condition remains unmet. More importantly, these measurements do not establish the requested target for *cold-process end-to-end compiler time*: the solver-time convention comes from the observable CLI contract. The separate preparation and load figures disclose this boundary rather than silently crediting free indexing. No unsolved file was dropped from @fig:times or the README's complete table.

== Cross-solver comparison on the harder family
On Gecode, `mac` solved 72/72 and `forward` 71/72 under the seed-zero protocol in @tab:headline. Forward checking's solved-run median was 0.013 s against MAC's 0.038 s, but it timed out on Gecode 45. Its full-family elapsed sum was 8.461 s versus MAC's 4.040 s; a low conditional median therefore does not imply a better regression-gate total. Both strategies failed core 87. Forward checking was also quicker on many core successes; the same domain representation and ordering isolate the principal strategy difference rather than conflating it with a new implementation stack.

The evidence is consistent with a propagation trade-off: forward checking avoids nonsingleton alphabet scans, while MAC invests in earlier detection of incompatible crossing domains. This is not proof that MAC dominates every grid or dictionary. The time limit, one suite seed and different failure sets prohibit an unconditional speedup claim.

== Structural findings
All supplied open cells are covered by some derived slot, so the isolated-open-cell rejection is exercised by tests but never changes a suite outcome. There are no locks in the performance suite; their normalization, membership exemption and mutual-consistency checks are likewise not performance-tested here. The support cache has measurable wall-time impact in the controlled ablation below, but does not change assignments or assignment counts. No feature for matching-based uniqueness, learned nogoods or structural splitting is shipped, so apparent visual regions cannot be credited as an implemented optimization.

Restarts activated in only two complete-suite MAC seed-zero runs: core 90 and unresolved core 87. The great majority of successful runs therefore do not test the restart policy. Its utility is better assessed by the seeded hard-instance study; attributing the entire suite's subsecond results to restart theory would exaggerate the evidence.

== Attribution study
We selected the three slowest *known-filled* default seed-zero cases from the suite: core 90 and Gecode 45 and 49. Their verified witnesses establish that these instances have fills. Core 87 was excluded from the attribution denominator because its fill status is open, not because its runtime was favourable. We toggled each default feature individually, preserving the other choices, dictionary and five-second budget, and ran seeds 0, 1, 2 for nine runs per configuration. Total time includes measured censored time. `nodes` is attempted assignments and includes restarts; it is a common work statistic, but a MAC node and a forward node have different costs.

#figure(
  table(columns: (1.5fr, auto, auto, auto), inset: 5pt,
    table.header([*Configuration*], [*Total time*], [*Verified*], [*Assignment nodes*]),
    ..data.ablation.map(r => (raw(r.name), seconds(r.seconds), str(r.solved) + "/9", str(r.nodes))).flatten(),
  ), kind: table,
  caption: measured-caption([Isolated-feature attribution on core 90 / Gecode 45 / Gecode 49.], extra: [Seeds 0, 1, 2. Time includes failures at their measured deadlines; no zero imputation.]),
) <tab:ablation>

#diagram("ablation.svg", measured-caption([F5. One bar per isolated configuration, annotated with total elapsed solver time, verified runs and assignment nodes.], extra: [Same three grids and seeds 0, 1, 2 as @tab:ablation. Positive totals are plotted linearly. Failed runs contribute their measured censored time; no zero readings occur.])) <fig:ablation>

Removing arc consistency increased the measured total from 2.004 to 10.956 s and lost Gecode 45 seed 0. Removing restarts lost Gecode 45 seed 2 and raised the total to 6.557 s. Without value ordering all nine runs still solved, but the total rose to 6.266 s. Restarts and value ordering interact: ranking them by these totals alone would obscure that one prevents a timeout while the other reduces work across several successes. With reliability first and total elapsed time second, the evidence ranks *arc consistency, restarts, then value ordering* as the consequential features on this selected set.

Removing the support-signature cache left exactly 2,466 assignment nodes, identical to the default, but increased total time to 2.332 s. Relative to the uncached measurement, caching saved approximately 14.1% wall time; this is consistent with avoiding redundant unions rather than pruning extra branches. Degree-tie removal changed 2,466 nodes to 2,600 and total time to 2.037 s. Its 1.6% aggregate timing difference is small enough that further repetitions are needed before ascribing a robust gain.

There is no unshipped configuration that beats the default on the *aggregate nine-run reliability-and-time metric* in this campaign. But the counterexample at instance level is explicit: disabling arc consistency solved the three core 90 seeds in a summed 0.050 s, versus the default's 0.377 s. Disabling restarts also marginally reduced that core-only sum, while failing a Gecode run. The default is a corpus-level reliability choice, not a per-instance oracle. These instances were selected from the same suite used for headline reporting; the ablation is an attribution study on hard known fills, not an independently held-out tuning result.

== The unresolved instance and a boundary proxy
Core 87 is 15 by 15, with 185 open crossing cells and 54 slots: 32 of length seven, 12 of length six, four of length five, four of length twelve and two of length three. Four dense regions communicate through the long slots. The English dictionary supplies 41,998 distinct seven-letter words and 29,124 twelve-letter words, but independent word counts do not guarantee compatible dense blocks.

#diagram("hardest.svg", measured-caption([F6. Exact blocked/open pattern of unresolved core 87, highlighting its long linking slots; the right panel is a region-level schematic, not a decomposition used by the solver.], extra: [The structure is derived from YAML, not timed. Its recorded solver readings are censored at 5 s; no zero-time or solution-status inference is drawn from the schematic.])) <fig:hardest>

The final campaign allocated 55 seconds of solver budget to core 87: two suite strategy runs and nine default runs across English, UK English and Spanish dictionaries with seeds 0, 1, 2. All eleven reached their deadlines without a fill. The alternative dictionary load counts were 225,349 and 109,419 surviving lines respectively; their exact fingerprints are in `other_dictionaries` in the raw artifact. This establishes failure of these runs, not absence of a fill. Its status is *open*: neither a witness nor an unsatisfiability proof is known to this implementation.

For a deliberately limited estimate of proximity to a feasibility boundary, we used a first-moment constrainedness surrogate inspired by phase-transition studies @cheeseman91 @gent96. Let each slot be independently uniform over its original length domain; let each crossing's agreement probability be the dot product of its two empirical position-letter frequency distributions. Then

```text
E_proxy = product(slot domain sizes) * product(crossing agreement probabilities)
q_proxy = exp(-log(E_proxy) / number_of_slots)
```

On core 87 and the primary English dictionary, this gives `log10(E_proxy) = 18.179` and `q_proxy = 0.461`, regenerated from masks by `diagrams/generate.py`. Under the *surrogate's independence assumptions*, uniform thinning to about 46% of each domain would reduce its expected count to one. This is not a measured threshold: within-word letter correlations, cycles and distinctness violate the approximation. The surrogate predicts abundance despite every censored attempt failing, so it provides no defensible estimate of the *actual* distance to a fill/no-fill boundary. Controlled thinning around a known witness and substantially stronger decision search are needed to locate that boundary. We report this failed diagnostic rather than assigning an unsupported “near-critical” label.

== Negative exploratory results and limits
Before the final controlled campaign, we tried full-propagation candidate lookahead, weighted-degree ordering, high-degree regional ordering, crossing-letter branching and coarse conflict-directed explanations. Related published mechanisms are weighted-degree search @boussemart04 and conflict-directed backjumping @prosser93. These prototypes did not produce a verified core 87 fill in their recorded five-second runs; the direct Spanish baseline also failed a recorded 120-second attempt. We reverted the prototypes to keep the shipped solver small. The archived `benchmarks/exploration` logs preserve these negative outcomes, dictionaries, seeds, quotas and work counts, but do not preserve every intermediate source version. Therefore they are *not* reproducible feature ablations and cannot support a controlled ranking of those techniques. The final isolated study in @tab:ablation is the evidence for shipped-feature attribution.

The single machine, chosen dictionary, reused indexes, suite-derived hard-set selection and limited seed sample restrict generalization. Neither statistical robustness on unseen dense grids nor superiority to an optimized external CSP engine has been measured. The all-grid goal and a reliable witness for core 87 remain the primary missing evidence.
