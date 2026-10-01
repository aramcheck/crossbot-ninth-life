#import "../shared.typ": *
= The System <sec:system>

== Geometry and dictionary representation
`Grid` records the pattern, canonical row-major keys, ordered slots and bidirectional indexed crossings. A key with two directions emits horizontal before vertical, so a slot index is not the same as a key number. Grid schemas reject unknown fields, malformed shapes, impossible key positions and metadata mismatches. Derived density has a tolerance of 0.01 percentage points; the stated informational word count is not validated. The canonical direction *sets* are compared in key order, and duplicate directions are rejected.

Dictionary lines are stripped and lowercased; empty lines and any line outside `a–z, ñ` are discarded. Unlike locks, dictionary lines are not accent-stripped. The surviving input order, including duplicates, is retained for the reported load count. A separate stable first-occurrence sequence assigns distinct word IDs by length. All IDs of a given length use the same index, including dictionary-exempt locked words appended for this problem. Consequently a word bit means the same thing in all same-length slots, a necessary invariant for distinctness pruning.

For each length, position and alphabet letter, `WordIndex` stores an integer mask whose set bits identify words with that letter at that position. Compilation first writes packed bytearrays and converts them to integers once; it does not repeatedly grow a large integer per word. An index is built lazily and reused by later problems with the same dictionary. With non-dictionary locks only the affected lengths are rebuilt. Dictionary membership also has an independent frozen set for verification.

#diagram("representation.svg", [F1. The central integer-domain representation and its elementary intersection, using the concrete toy index `ab, ac, bd, cd`. This is an analytic example, not a timed run; dictionary, seed, budget and machine are inapplicable. Bit strings are exact; no zero or censoring convention is needed.]) <fig:representation>

`Problem` contains geometry, the original lexicon, locks, per-slot indexes, initial domains and same-length peers. A lock is a singleton domain. If a required length has no dictionary word and no lock-provided word, construction raises an input error. Locks are case-insensitive, normalized to canonical Unicode before accent removal, and preserve `ñ`; their original specs are quoted in errors. Dictionary exemption applies to the locked assignment, not to an arbitrary fabricated word elsewhere.

== Shared propagation and restoration
`Domains.values[i]` is the live word bitset. A trail entry saves `(slot, old_domain, old_support_signatures)` before every change. A mark is a trail length; restoration pops to that length. Support signatures are 27-bit sets, one per slot position, initially unknown (`-1`). Root propagation and every assigned branch run a FIFO queue with a membership set that prevents duplicate queue entries.

For a queued source, a singleton removes its word bit from every same-length peer. A zero domain fails immediately. For each crossing from source position $p$ to target position $q$, compute the set $S$ of letters with a nonempty intersection between the source domain and `mask[p, letter]`. A singleton uses its actual character instead of scanning the alphabet. If $S$ equals the saved signature, that crossing needs no new filtering: the target has already been restricted to those letters. Otherwise save $S$, form the union of target masks for supported letters, and intersect the target domain. When fewer letters are absent than present, form the union of *absent* masks and remove it instead. The target is requeued only if its domain changes. This is arc consistency specialized to shared-letter equality, not an implementation of general table GAC.

The support cache is branch state. It is restored with domains; forgetting to restore it can incorrectly skip a needed revision after backtracking. Same-length peers share word IDs; assigning IDs from inconsistent indexes could incorrectly remove a different word. The tests explicitly check both representation invariants. Distinctness filtering only removes singleton values; it does *not* enforce Hall sets or Régin's matching-based all-different consistency @regin94.

== The default search, with all shipped choices
The default registered solver is `mac` (maintaining arc consistency). `forward` uses the same engine but skips crossing propagation from nonsingleton sources. The former is selected as default because the measured hard cases favour its reliability, not because it wins every timing comparison. There is no worker pool, structural partition, staged compilation solver, precomputed solution, persistent fill cache, or grid-ID special case.

At each depth, check the absolute `perf_counter()` deadline. Select a nonsingleton slot with minimum domain cardinality; ties prefer the greatest number of currently nonsingleton crossing neighbours, then the lowest slot index. Assigned singletons are excluded. If all slots are singleton, return their words. Before search, coverage is checked so an otherwise unconstrained isolated open cell cannot produce an invalid “solution”. An all-blocked grid has a valid empty assignment.

Values are ordered as follows; these details define the implementation, including random draws.

1. The sample limit is *48*. If the domain cardinality is at most *96*, enumerate all live IDs and shuffle them.
2. Otherwise, if at least one eighth of IDs up to the highest live bit are present, repeatedly draw a uniform integer in that range and retain distinct live IDs until 48 have been collected. Sort their set before shuffling, so hash iteration does not affect reproducibility.
3. For sparser domains, enumerate live IDs once and use `random.sample` to draw 48 without replacement.
4. Score each sampled word by $sum_e ln n_e$, where $n_e$ is the count of target-domain words supporting that word's letter on crossing $e$. A zero count gives negative infinity. Sort descending, stably preserving randomized order on equal scores. The score approximates the product of independent neighbour supports; it is not belief propagation or a count of globally extendable assignments.
5. Try those sampled values first, then every unsampled live ID in ascending order. Sampling prioritizes values; it does not delete unsampled candidates.

A value assignment saves a mark, makes the selected domain singleton, propagates, then recurses. A failure restores to the mark and increments `backtracks`. The `nodes` statistic counts attempted word assignments, not recursive calls or grid cells. `revisions` counts crossing-domain reductions, excluding distinctness deletions. These definitions matter when comparing MAC with forward checking.

The first search attempt has an allowance of *400 nodes*. A quota exhaustion raises a restart rather than unsatisfiability. The original propagated root domains and support signatures are restored, while the RNG stream continues. After restart number $r$, the next allowance is $400 times 2^(min(r,12))$ additional nodes. Statistics accumulate over attempts; quotas saturate at 1,638,400 nodes. Quota saturation is not exercised by the recorded suite or ablations. Individual uninterrupted DFS attempts enumerate all values; the restarting algorithm with a finite deadline is not a complete decision procedure. Only exhaustion of an entire attempt can return `unsatisfiable`.

```text
propagate root; preserve root domains and signatures
repeat:
    DFS:
        check deadline; choose nonsingleton MRV slot
        if none: return all singleton words
        for value in sampled-LCV order, then remaining IDs:
            check deadline and cumulative node quota
            save trail mark; assign; propagate
            if consistent and recursive DFS succeeds: return fill
            restore mark; count backtrack
        return exhaustive failure
    on quota: restore root; increase next node allowance
    on deadline: return timeout
```

#diagram("control.svg", [F2. Control-flow summary of the default strategy. A consistent but incomplete branch returns to selection; success is emitted only when every domain is singleton. Quota exhaustion is not an UNSAT proof. This is a code-derived schematic, with no measured dictionary/seed/budget/machine or zero/censored values.]) <fig:control>

== Frontends and verification boundaries
A registry holds a name, description, callback and default marker for each strategy. It rejects duplicate names or multiple defaults. The CLI and benchmark depend only on that contract. They report mandatory solver, seed and elapsed time fields plus the stable solver-specific keys `nodes`, `backtracks`, `revisions`, `restarts`. Time is solver wall time, not process startup, dictionary loading, problem preparation or verification.

A returned fill is checked against the original problem, not against reduced bitsets: slot coverage and lengths, original dictionary membership, exact lock equality, crossings and no repeats. Invalid fills never reach grid rendering or count as benchmark successes. A lock-violation error is distinguished from other fill defects. Both frontends print ordinary Unicode tables without a terminal-dependent layout. The benchmark builds each problem once and verifies every solver/seed result independently.

#diagram("architecture.svg", [F3. Frontend-independent solver architecture: both strategies share search, ordering, indexes and reversible domain state; each result crosses the independent verification boundary. There is no staging or subproblem decomposition. This is a code-derived schematic; dictionary, seed, budget, machine and zero/censoring conventions are inapplicable.]) <fig:architecture>

The code baseline `d9e568f` passed 105 tests, strict mypy over `src` and Black formatting. Tests include exhaustive independent tiny-instance oracles, metadata and lock defects, external thematic words, `ñ`, seeded equality, cache restoration, cancellation and deliberately invalid solver outputs. These are correctness checks, not evidence for performance on additional grid corpora.
