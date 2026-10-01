# Literature-search record and limits

The report distinguishes a traced principle from absolute historical priority.
The search was performed while building this implementation, using public
Crossref metadata/title queries, arXiv's title feed and primary-publication
metadata/abstracts. No bibliographic search API or solver is a project dependency.

Queries included:

- `complexity crossword puzzles`, `crossword NP complete`, `Filling Crosswords is Very Hard`;
- `computer crossword construction`, `computer crossword Siklossy`, `Taieb crossword construction`;
- `automated crossword puzzle solving`, `Dr.Fill`, `Automated Crossword Solving`;
- `Enforcing Arc Consistency using Bitwise Operations`, `Lecoutre Vion bitwise`;
- `Compact-Table Efficiently Filtering Table Constraints`, `Networks of constraints Fundamental properties`;
- `Improving Backtrack Search for Solving the CSP Problem`, `Backtrack Programming`.

Endpoints were `https://api.crossref.org/works?query.title=...`, bibliographic
queries on the same service, DOI metadata endpoints, and
`https://export.arxiv.org/api/query?search_query=ti:crossword&max_results=20`.
Some queries returned irrelevant records; exact DOI lookup confirmed the
Mazlack construction papers, Smith's XENO, Golomb/Baumert's Backtrack
Programming, Haralick/Elliott's *Increasing tree search efficiency for
constraint satisfaction problems*, Compact-Table and the ACL Berkeley paper.
The arXiv feed supplied the complexity paper's abstract and authors, Dr.Fill's
JAIR citation/DOI, the French WebCrow preprint, and the NAACL 2025 system.
Crossref also identified the 2026 reactive-construction article.

An important correction during lookup: the initially guessed DOI for
Backtrack Programming was another article. The committed bibliography uses
`10.1145/321296.321300`, confirmed by title metadata; the earlier guess is not
cited. Likewise, the Haralick/Elliott title is the actual *Increasing tree
search efficiency...*, not a guessed title based on its topic.

Access limits: several Crossref requests returned gateway errors or poor title
matches; DBLP returned a bot challenge, and some publisher full-text endpoints
were inaccessible. These are not evidence of absence. The report uses stable
primary-paper or record URLs where DOI metadata was unavailable. It does not
claim a systematic review, first historical use of all data structures, or a
complete survey of the earliest construction programs. Mazlack 1973 is the
earliest primary publication recovered by this search, not a certified first.

Exact origins not located: problem-local stable IDs and duplicate-load
accounting, bytearray-to-int mask compilation, choosing the smaller
supported/complement alphabet union, the exact 48/96/one-eighth sampling
thresholds, and the verified registry/interface packaging. Their parent
principles (indexing, bitsets, set algebra, randomized value ordering and
software modularity) are established. No new-device priority is inferred from
an unsuccessful search. The mechanism table makes these gaps explicit.

Bibliography entries serve distinct roles: crossword construction/filling
history; complexity; primary search/propagation/bitset/trail/randomization
mechanisms; nearby but non-identical algorithms; and established upgrades or
experimental methodology. Every entry is cited; references to unimplemented
methods do not imply that crossbot implements them or benefits from them.
