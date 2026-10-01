#import "../shared.typ": *
= Novelty Assessment <sec:novelty>

== What is established
Slot-based crossword CSPs and deliberate search ordering are established in construction and filling literature @mazlack76 @ginsberg90. Arc consistency, forward checking and fail-first search are established general techniques @mackworth77 @haralick80. Bitset support filtering and reversible table representations predate this code @lecoutre08 @compact16. State restoration, event-sensitive propagation, randomized search and restart scheduling are also established @warren83 @schulte08 @gomes98 @luby93. The same classification is used in @tab:lineage: an implementation independently arriving at a known idea does not make that idea novel.

The report's dictionary-exempt locks, Unicode handling, stable IDs, registry and verification boundary are requirements and software engineering devices. Their combination is useful for a conforming CLI; usefulness alone is not an archival novelty claim. The sampled log-support value score is an application of established LCV freedom estimation, not a new inference principle. In particular it does not implement the probabilistic models of clued systems @littman99 @wallace22.

== Is the combination new for this problem?
The package combines Python integer domains, per-position alphabet masks, signature-sensitive propagation, bounded LCV ranking and geometric restarts under a verified-input/output contract. We found no primary publication documenting precisely this implementation tuple and these constants for the supplied assets. However, crossword-specific search papers already combine heuristic variable/value choice with propagation @ginsberg90, and modern clued filling combines still richer inference and search @ginsberg11 @wallace22. We therefore cannot defend “first use of this combination” from the bounded literature search. The defensible contribution is a inspectable implementation and reproducible negative/positive measurements, not a demonstrated novel combination.

== Candidate individual devices
*Signature-sensitive filtering.* Its nearest published neighbour is event filtering in propagation engines @schulte08. The alphabet projection is a natural event abstraction for crossword equality. Verdict: an established principle with a problem-specific engineering realization, not a novel principle or a proven novel application.

*Packed bytearray construction and smaller-complement unions.* Their nearest neighbours are bitwise support and reversible table algorithms @lecoutre08 @compact16. The exact idioms were not traced to a publication, but they implement ordinary set construction and complement algebra. Verdict: engineering devices not worth a paper on their own; no demonstrated novelty.

*Two-regime sampled LCV and deterministic draw accounting.* The neighbours are LCV ordering @haralick80 and randomized combinatorial search @gomes98. The thresholds trade sorting effort against sample coverage. Verdict: engineering parameterization of established principles. No training protocol supports a claim that these constants are optimal, and the negative grid 87 outcome is evidence against a universal sufficient recipe.

Structural factoring, message-passing value guidance, learned nogoods and matching-based uniqueness are *untested improvement ideas for the shipped system*. We do not claim them as contributions; their established neighbours are identified in @sec:opportunities. The reverted exploratory devices likewise do not become novel merely because they were attempted unsuccessfully.

== Is it state of the art?
*No state-of-the-art claim is supported: crossbot has not undergone a controlled head-to-head comparison on the same machine, dictionaries, grids, uniqueness rule and budget against published filling systems.* The Berkeley and modern language-model results address clue-solving objectives and different candidate distributions @wallace22 @saha25; their reported accuracy is not a fill-time baseline for these assets. Our controlled baseline is only the shipped forward-checking strategy, and our default still fails one required grid. Comparisons to unimplemented AC-4/AC-6, generic table engines or Dr.Fill would require new measurements, not literature-title analogy.
