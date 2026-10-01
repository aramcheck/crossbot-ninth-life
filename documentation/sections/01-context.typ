#import "../shared.typ": *
= Context <sec:context>

== Problem and scope
A fixed grid defines a variable for each maximal horizontal or vertical run of at least two open cells. Its domain is the set of dictionary words of the required length. A crossing equates two indexed characters. Distinctness applies globally, including locked words. A lock fixes one variable to an explicitly normalized word, even if that word is absent from the dictionary. The grid is filled only if every open cell is covered by assigned slots; an isolated open cell therefore makes a fill impossible, rather than inviting an arbitrary extra letter. These are the contracts in `crossbot.spec.md` and the checks in `grid.py`, `problem.py` and `verify.py`.

The report concerns *filling*, not discovering a grid pattern, writing clues, or judging word quality. Membership in these supplied dictionaries is the only lexical-quality criterion. Alphabet handling preserves `ñ` as a distinct letter. YAML metadata, canonical numbering, lock consistency, coverage and the final assignment are all validated. The suite exercises ordinary, unlocked filling; the thematic and Spanish-letter paths are covered by tests, not by the main English performance campaign.

The goal requests a solver capable of filling every supplied grid with at least one supplied dictionary in less than five seconds, and at least ninety percent below one second. The measured result reaches the second aim in the solver-time metric but not the first condition. This is an *interim analysis of a shipped implementation*, not a certificate that the goal has been reached. Loading and indexing are accounted for separately in @sec:evaluation; cold-process compiler performance has not been measured suite-wide.

== Complexity
The general crossword construction/filling decision problem is a classical NP-complete problem in Garey and Johnson's catalogue @garey79. An explicit assignment is a polynomial-size certificate and is checked by testing lengths, letters, membership and distinctness. Gourvès and colleagues revisit the grid-graph formulation and prove hardness even under severe structural restrictions when word reuse is prohibited @gourves21. Their reuse-allowed treewidth algorithms do not automatically apply to crossbot's global distinctness rule. These general results neither prove that this finite suite is difficult nor prove the unresolved instance unsatisfiable. The supplied fixed alphabet and fixed collection are an experimental domain, not an asymptotic hardness argument.

== Prior construction and filling systems
Our earliest recovered primary construction publication is Mazlack's probability-based conference paper @mazlack73; his subsequent system organizes precedence relationships to guide construction @mazlack76. We do not assert that these are historically the first programs: the search recovered them, not a complete chronology of unpublished or earlier work. XENO supports computer-assisted compilation and interactive construction @smith83. Ginsberg, Frank, Halpin and Torrance study search choices specifically through crossword instances @ginsberg90; this is a closer predecessor to fixed-pattern filling than unconstrained puzzle generation.

PROVERB generates clue-dependent candidate answers and combines them probabilistically over intersections @littman99. WebCrow adds web-derived candidate retrieval to the same shared-letter core @ernandes05. Dr.Fill represents clued puzzles as singly weighted constraint problems, with discrepancy search, postprocessing and partitioning @ginsberg11. The Berkeley Crossword Solver combines neural candidate generation, loopy belief propagation and local search @wallace22. French WebCrow demonstrates multilingual candidate experts @angelini23. Saha and colleagues combine language-model clue answers with full-grid search @saha25. The more recent reactive construction study of Biemer and Cooper addresses difficulty during puzzle generation rather than the exact fixed-grid contract used here @biemer26. These are characterized as related systems, *not* as controlled performance baselines; their objectives, candidate domains, corpora and hardware differ.

== Questions answered by this report
- What is actually implemented, and how can the default strategy be reproduced? @sec:system.
- Which ideas are established and which exact realizations remain untraced? @sec:lineage.
- What do complete-suite, cross-solver and isolated-feature measurements establish? @sec:evaluation.
- Is any novelty or state-of-the-art claim justified? @sec:novelty.
- Which changes are supported now, and which need a new experiment? @sec:opportunities.
- What has been achieved, and what prevents declaring the goal complete? @sec:conclusions.
