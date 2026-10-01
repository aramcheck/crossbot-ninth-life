#import "shared.typ": *
#set document(title: "Crossbot: bit-parallel constraint search and a remaining dense-grid bottleneck", author: "Crossbot engineering study")
#set page(paper: "a4", margin: (x: 22mm, y: 22mm), numbering: "1", header: context {
  if counter(page).get().first() > 1 {
    set text(size: 9pt)
    [Crossbot — verified filling and measured limitations #h(1fr) Technical analysis]
    line(length: 100%, stroke: 0.4pt + gray)
  }
})
#set text(font: "Libertinus Serif", size: 10.5pt)
#set par(justify: true, leading: 0.65em)
#set heading(numbering: "1.1")
#set raw(lang: "text")
#show raw: set text(font: "DejaVu Sans Mono", size: 8.5pt)
#set figure(gap: 0.8em)
#show figure.caption: set text(size: 9pt)
#show table: set text(size: 9pt)
#show figure.where(kind: table): set block(breakable: true)

#align(center)[
  #text(size: 21pt, weight: "bold")[Crossbot: bit-parallel constraint search and a remaining dense-grid bottleneck]
  #v(0.7em)
  #text(size: 11pt)[A reproducible engineering study of the shipped implementation]
  #v(0.5em)
  Code baseline: `d9e568f` · Measurements: `benchmarks/results.json`
]
#v(1em)
*Abstract.* Crossbot validates and fills fixed crossword grids with distinct dictionary words and optional thematic locks, then independently verifies every returned assignment. On an Apple-vendor aarch64 Linux VM using CPython 3.14.7, the default bitset maintaining-arc-consistency solver filled 87 of 88 supplied grids within a five-second budget; all 87 successful seed-zero runs took less than one second. Core grid 87 remains unresolved, so the prescribed all-grid exit condition is not met. We traced the solver's mechanisms to established constraint-search, bitset, restoration, randomization and propagation literature, explicitly recording where the exact engineering realization has no located origin. An isolated study on three known-fill grids with three seeds each is consistent with arc consistency, value ordering and restarts contributing more than support-signature caching or degree ties. Forward checking has lower overhead on easy instances but more timeouts. We claim neither a new algorithmic principle nor state-of-the-art performance: no controlled external-system comparison was performed. Stronger reasoning and structure-aware search on the unresolved dense instance remain open. The report preserves failures, negative exploratory results and verified witnesses rather than substituting a hidden timeout or precomputed fill.

#include "sections/01-context.typ"
#include "sections/02-system.typ"
#include "sections/03-lineage.typ"
#include "sections/04-evaluation.typ"
#include "sections/05-novelty.typ"
#include "sections/06-opportunities.typ"
#include "sections/07-conclusions.typ"
#bibliography("references.bib", style: "ieee", title: "References")
#pagebreak()
#include "sections/appendix-a.typ"
