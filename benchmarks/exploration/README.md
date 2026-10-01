# Reverted exploratory campaigns

These logs are retained negative results, **not reproducible controlled
ablations of the final source**. They precede code baseline `d9e568f`, and the
intermediate prototypes were reverted. There is no claim of relative superiority
based on these logs. The final controlled ablations live in `../results.json`.

Machine/interpreter: the same Apple-vendor aarch64 Linux VM (5 vCPUs, 7.9 GiB)
and CPython 3.14.7 used by the final campaign. All cases are core grid 87.
Names identify the supplied dictionary; surviving line counts are 370,105
English, 225,349 UK English and 109,419 Spanish. No locks were present.

- `tune.txt`: sample sizes 8/128/512, unresolved-degree on/off, three seeds,
  all three dictionaries; 5 s; initial restart quota 100 nodes.
- `probe.txt`: full-propagation candidate lookahead, samples 8/16/48, three
  seeds and all three dictionaries; 5 s; restart quota 100.
- `region.txt`: high-degree separators, region order including boundary slots;
  three seeds/dictionaries; 5 s; quota 100. First line gives region slot IDs.
- `region2.txt`: region order excluding boundary-slot branching; otherwise same.
- `wdeg.txt`: constraint-weighted variable selection; three seeds/dictionaries;
  5 s; quota 100.
- `letters.txt`: crossing-letter branching; three seeds/dictionaries; 5 s;
  quota 400.
- `random.txt`: disable LCV sorting, seeds 0–14 and all dictionaries; 2 s;
  quota 50.
- `distinct.txt`: defer word-uniqueness pruning until duplicate singleton
  detection, regional ordering on/off; three seeds/dictionaries; 5 s; quota 100.
- `87long.txt`: direct Spanish MAC baseline, seed 0, 120 s.

All these recorded runs timed out without a verified fill. Dictionary/index
preparation was outside the solver timer. Timings are solver wall time, and
stats retain each prototype's definitions. There are no precomputed fills in
these files; the production solver does not read them.
