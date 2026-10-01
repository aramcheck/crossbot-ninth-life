#import "../shared.typ": *
= Intellectual Lineage <sec:lineage>

We distinguish an established *principle* from priority for an exact piece of code. “Established origin” below means the primary work to which we can trace that principle; it does not assert that every cited author was the first to use every elementary data structure. If we could not locate the exact realization, we say so rather than interpreting absence as novelty. Every shipped algorithmic mechanism is classified as established; untraced packaging is conservatively treated as an engineering realization of an established principle, not as a demonstrated new device.

We searched Crossref titles and bibliographic queries for crossword construction, crossword complexity, arc consistency, bitwise table filtering and backtrack programming; we also inspected the arXiv crossword-title feed and the primary metadata/abstracts for the complexity, Dr.Fill and recent clued-solvers papers. The record is summarized in `documentation/research-notes.md`. This was not an exhaustive archival or patent search, and some publisher/DBLP endpoints were unavailable or rate-limited. Claims of *absence from all prior work* would not be justified by this search.

#figure(
  table(
    columns: (1.05fr, 1.1fr, 1.2fr),
    inset: 5pt,
    stroke: 0.4pt + luma(75%),
    table.header([*Mechanism in crossbot*], [*Established origin*], [*Deviation / refinement*]),
    [Slot-word variables and indexed crossing equality], [Crossword precedence/search formulations @mazlack76 @ginsberg90; relation networks @montanari74], [Established. A fixed-pattern feasibility CSP, not pattern creation or clued weighted inference.],
    [Length partition, membership set and stable first-occurrence word IDs], [Not found in the surveyed literature for this exact representation. General finite-domain indexing is established @mackworth77.], [Established indexing principle; stable IDs and duplicate-load accounting are untraced engineering packaging.],
    [Unicode normalization and preserved `ñ`], [Canonical normalization in Unicode Annex 15 @unicode], [Established. Accent removal excludes `ñ`; dictionary loading deliberately does not remove accents.],
    [Locked singleton domains, including non-dictionary words], [Unary restrictions in relation networks @montanari74], [Established. Problem-local appended IDs implement the dictionary exemption and preserve same-length ID identity.],
    [Integer domains; position/letter masks; intersections], [Bitwise arc filtering @lecoutre08; reversible bitset table filtering @compact16], [Established. Plain Python integers, not sparse machine-word sets; masks project words onto letters.],
    [Packed bytearray index compilation], [Not found in the surveyed literature for this exact compiler device. Bitset construction is an established principle @lecoutre08.], [Established principle; byte-to-integer materialization is an untraced engineering realization.],
    [FIFO propagation queue with duplicate suppression], [Queued arc-consistency filtering @mackworth77], [Established. Sources queue slots, not arbitrary binary arcs. No AC-4 support counts @mohr86 or AC-6 residue machinery @bessiere94.],
    [Crossing revision from supported letter sets], [Arc consistency @mackworth77; bitwise support filtering @lecoutre08], [Established. Alphabet projections specialize the binary relation; the target uses a union of masks.],
    [Unchanged-letter-signature skip], [Event-based propagation and necessary wake-up conditions @schulte08], [Established event-filtering principle. A per-position signature is saved/restored with domains; exact 27-bit packaging was not located.],
    [Union the smaller of supported/absent letters], [Not found in the surveyed literature for this exact heuristic; bitwise filtering is established @lecoutre08.], [Established set-complement principle, untraced engineering choice; no new-device claim.],
    [Singleton word deletion from same-length peers], [Forward checking @haralick80; difference constraints discussed by @regin94], [Established, weaker than matching-based all-different. No Hall-set detection.],
    [Reversible domain/support trail], [State restoration in backtracking @golomb65; explicit trail machinery @warren83], [Established. Save whole integer domains and small signature lists, not individual value deletions or Prolog bindings.],
    [MRV slot selection], [Fail-first/backtrack ordering @golomb65 @haralick80], [Established. Recomputed popcounts; already singleton slots are omitted.],
    [Unresolved-degree tie-break, then slot index], [Connectivity-aware search ordering @haralick80], [Established. Count only nonsingleton crossing neighbours, not global distinctness peers; deterministic final tie.],
    [Least-constraining sampled word score], [Value ordering and future-domain freedom @haralick80], [Established LCV principle. Sum logarithms of immediate support counts; independence approximation, no full lookahead. Exact formula's first origin not located.],
    [48-value sample, dense rejection or sparse enumeration], [Not found in the surveyed literature for the exact two-regime sampling device. Randomized search is established @gomes98.], [Established random-sampling/search principle; thresholds 48, 96 and one eighth are engineering choices, not learned constants.],
    [Seeded pseudorandom stream; sorted sets before shuffle], [Mersenne Twister @matsumoto98], [Established PRNG. Python's `Random` supplies draws; canonical set-to-list conversion avoids hash-order dependence.],
    [Sample first, exhaustive ascending-ID remainder], [Enumerative backtracking @golomb65], [Established. Sampling changes priority, never domain completeness within one uninterrupted attempt.],
    [Geometric node-budget restarts], [Randomized combinatorial restarts @gomes98; schedule theory @luby93], [Established. 400-node initial quota, doubling with exponent capped at 12; not the universal Luby schedule.],
    [Forward-checking alternative], [Forward checking @haralick80], [Established. Reuses the engine but only singleton sources constrain crossings.],
    [Monotonic absolute deadline], [Python performance-clock interface @pep418], [Established engineering API. Cooperative cancellation, not hard real-time preemption.],
    [Independent witness validation and registry boundary], [Not found in the surveyed algorithmic literature for this exact interface.], [Established software-verification and modularity principles; no novel application or algorithmic claim. No solver-side structural splitting exists.],
  ),
  kind: table,
  caption: [Mechanism-by-mechanism lineage of the shipped code baseline `d9e568f`. This is a source/code comparison, not measurement; dictionary, seed, budget and machine are inapplicable.],
) <tab:lineage>

== Inexact correspondences and nearby ideas
The bitset correspondence is direct at the set-operation level, but crossbot does not implement Compact-Table's sparse reversible bitset representation, active tuple bookkeeping or its generic GAC propagator @compact16. A word-slot domain and its letter projections are enough for a shared-character binary relation. This reduces code and domain operations, but should not be described as a new table-consistency algorithm.

Signature caching is an event condition: removing words need not change the set of letters available at a crossing. Schulte and Stuckey analyze efficient propagation-engine wake-up conditions @schulte08. Our cache is simpler and problem-specific. It differs from remembering a particular support tuple, as in residue-based consistency algorithms @bessiere94, and from maintaining a support count for every value @mohr86. The complement-union choice and bytearray compilation are ordinary set algebra and representation engineering; their exact code idioms have no recovered paper origin. They are not tagged *new device*.

The LCV score treats neighbour-domain counts as independent. That is inexact on cyclic crossing graphs and ignores correlations within a dictionary word. It is much weaker than the probabilistic message passing of Pearl @pearl82 or the clue-weighted beliefs of PROVERB and Berkeley @littman99 @wallace22. Taking logarithms only avoids multiplying large counts; it does not turn this ordering into a calibrated probability model. Restricting expensive ranking to a bounded sample is an engineering compromise. Randomization preserves a deterministic draw stream for a fixed interpreter/input/seed, but a censored run can execute different amounts of work under different machine loads.

Geometric restart quotas are related to heavy-tailed randomized search @gomes98, not proven optimal for this distribution. Luby's universal schedule has a different sequence and guarantees under assumptions that are not established here @luby93. Our cap is explicit and unexercised in the reported experiments. No constant was chosen through a train/held-out optimization campaign; this limits generalization claims about 48 or 400.

Finally, global uniqueness is not a local crossing edge. The distinction matters for decomposition: a region filled independently can still reuse a word chosen elsewhere. Freuder's structural conditions for backtrack-free search @freuder82 and Dechter and Pearl's network heuristics @dechter87 describe useful graph structure, but they do not license treating crossbot's regions as independent. Ginsberg's crossword-specific partition/postprocessing work @ginsberg11 addresses a richer objective; merely copying a grid partition does not inherit its guarantees. This is a divergence between the visually local crossword graph and general CSP dependence, not a discovery of a new structural theorem.
