# crossbot — CLI and benchmark tool specification

This document specifies the observable behavior of the two entry points —
the main CLI and the `benchmark` harness — in terms of commands, expected
input, and expected output. It is implementation-agnostic: any program that
honours these contracts is a conforming crossbot.

## 1. Domain

Crossbot fills **crossword grids** with words from a dictionary.

- A **grid** is a rectangular matrix of cells, each either _open_ (`-`) or
  _blocked_ (`x`).
- A **slot** is a maximal horizontal or vertical run of open cells of length
  ≥ 2. Every slot must be filled with exactly one word of matching length,
  and where two slots cross they must agree on the shared letter.
- **Keys** are the canonical crossword numbering: scanning the grid
  row-major, a cell receives the next number if it starts a horizontal
  and/or vertical word (length ≥ 2). A key therefore addresses one or two
  slots (e.g. "25 horizontal", "25 vertical").
- A **solution** assigns a word to every slot such that: every open cell is
  filled, every slot's word is in the dictionary (with one exception, see
  locked words), crossings agree, and **no word is used twice** in the grid.
- **Locked words** are thematic hard constraints: a word pinned to a key's
  slot before solving begins. Locked words are validated for shape and
  mutual consistency but are **exempt from dictionary membership**.
- The working **alphabet** is `a–z` plus `ñ` (treated as a letter in its own
  right). All matching is lowercase; accents are stripped on input where
  noted.
- A **solver** is a named strategy that the CLI can select. The program
  ships one or more solvers, exactly one of which is the **default**. A
  solver receives a problem (grid, dictionary, locked words), an integer
  seed and a deadline, and returns either an assignment or a failure, plus
  zero or more solver-defined **statistics** (`key=value` pairs, see 2.2).
  Adding a solver must not require changes to the CLI or the benchmark
  tool beyond making the solver known to them.

### 1.1 Grid file format

A grid is a YAML document with these fields:

| field               | required | meaning                                                                                |
| ------------------- | -------- | -------------------------------------------------------------------------------------- |
| `id`                | yes      | integer identifier of the grid                                                         |
| `source_page`       | no       | provenance annotation (page of the source report)                                      |
| `dimensions`        | yes      | `{rows: R, cols: C}`, both ≥ 1                                                         |
| `density`           | no       | declared percentage of open cells (checked, ±0.01 tolerance)                           |
| `word_count`        | no       | declared number of slot-words (checked exactly)                                        |
| `stated_word_count` | no       | informational only, not checked                                                        |
| `grid`              | yes      | multiline block: one line per row, `-` = open, `x` = blocked                           |
| `keys`              | yes      | full list of `{number, position: [row, col], directions: [horizontal\|vertical, ...]}` |

**Validation rules** (a file violating any of these is rejected with an
error naming the mismatch):

1. The number of grid lines equals `dimensions.rows`; every line has
   exactly `dimensions.cols` characters, all drawn from `{-, x}`.
2. Every key's position is in bounds and on an open cell.
3. The `keys` list must be **exactly** the canonical numbering derived from
   the grid pattern (same numbers, positions and direction sets, in order).
4. If `word_count` is declared it must equal the computed count
   (sum of directions over all keys).
5. If `density` is declared it must match the computed percentage of open
   cells within a tolerance of 0.01.

### 1.2 Dictionary file format

Plain text, one word per line. On load, each line is stripped and
lowercased; lines that are empty or contain any character outside the
alphabet (`a–z`, `ñ`) are silently discarded. The order of the remaining
lines is preserved.

### 1.3 Locked-word spec grammar

```
<key-number><h|v>:<word>        e.g.  25h:dudar
```

Case-insensitive; the word is normalized (lowercased, accents stripped, `ñ`
preserved). A spec is rejected — with a message quoting the offending
spec — when any of the following holds:

- it does not match the grammar;
- the word contains characters outside the alphabet after normalization;
- the grid has no key with that number;
- the key has no word in the requested direction;
- the word length differs from the slot length (message states both);
- the same slot is locked twice to different words;
- two locks pin the **same word** to different slots (words may not repeat);
- two locks disagree on the letter of a shared crossing cell.

## 2. Main CLI

```
<cli> <command> [arguments] [options]
```

Three subcommands: `grid-info`, `solve`, `list-solvers`. All errors
terminate with a non-zero exit status and a single explanatory message
(prefixed `error:` for input problems). Success output goes to stdout.

### 2.1 `grid-info <grid-file>`

Validate a grid file and render it.

**Input:** path to a grid file (section 1.1).

**Output on success** (exit 0):

1. A box-drawing rendering of the empty grid: blocked cells filled solid
   (`███`), open cells showing their key number (left-aligned) or blank.
2. A summary line:
   `grid <id>: <R>x<C>, density <D.DD>%, <K> keys, <W> words`
3. The line `OK: grid is consistent`.

Example:

```
┌───┬───┬───┬───┬───┐
│1  │2  │3  │███│███│
├───┼───┼───┼───┼───┤
│4  │   │   │5  │███│
├───┼───┼───┼───┼───┤
│6  │   │   │   │7  │
├───┼───┼───┼───┼───┤
│███│8  │   │   │   │
├───┼───┼───┼───┼───┤
│███│███│9  │   │   │
└───┴───┴───┴───┴───┘
grid 5: 5x5, density 76.00%, 9 keys, 10 words
OK: grid is consistent
```

**Output on failure:** `error: <path>: <validation message>`, non-zero exit.

### 2.2 `solve <grid-file> <dictionary> [options]`

Fill the grid with distinct dictionary words and print the verified
solution.

**Positional input:**

- `grid-file` — grid file per section 1.1.
- `dictionary` — word list per section 1.2.

**Options:**

| option               | default                       | meaning                                                                    |
| -------------------- | ----------------------------- | -------------------------------------------------------------------------- |
| `--solver <name>`    | the registered default solver | which solver to use; must be one of the available solvers                  |
| `--seed <int>`       | `0`                           | random seed; the same (grid, dictionary, solver, seed) run is reproducible |
| `--timeout <float>`  | `10.0`                        | time budget in seconds; the solver must stop at the deadline               |
| `-w / --word <spec>` | none                          | lock a word into a key (grammar in 1.3); repeatable                        |

**Behavior:**

1. Load and validate the grid (as `grid-info` does) and the dictionary.
2. Parse and validate every lock spec (section 1.3).
3. Build the problem; if the dictionary (locked words included) has **no
   word of some required slot length**, exit with
   `error: dictionary has no words of length <L>`.
4. Run the chosen solver with the seed and deadline.
5. Verify any returned solution end-to-end before printing (locked slots
   honoured; every cell filled; every word in the dictionary or among the
   locked words; no repeats).

**Output on success** (exit 0):

1. A box-drawing rendering of the solved grid, uppercase letters centered
   in their cells, blocked cells solid.
2. If any locks were given, one line listing them (sorted, key label to
   uppercased word):
   `locked words honoured: 20h=SOL 25h=DUDAR 25v=DANES`
3. A final status line:
   `SOLVED grid <id>: <N> words placed, all distinct (<stats>)`

The **stats block** `<stats>` always begins with the three mandatory
fields `solver=<name> seed=<s> time=<t.tt>s` (elapsed wall time with two
decimals). A solver may append zero or more of its own statistics as
space-separated `key=value` pairs, where `key` matches `[a-z_]+` and
`value` is an integer or decimal. Which keys a solver reports, if any, is
up to the solver, but a given solver must always report the same keys.

Example:

```
┌───┬───┬───┬───┬───┐
│ A │ A │ A │███│███│
├───┼───┼───┼───┼───┤
│ S │ A │ R │ T │███│
├───┼───┼───┼───┼───┤
│ T │ H │ A │ I │ S │
├───┼───┼───┼───┼───┤
│███│ S │ K │ E │ E │
├───┼───┼───┼───┼───┤
│███│███│ S │ S │ P │
└───┴───┴───┴───┴───┘
SOLVED grid 5: 10 words placed, all distinct (solver=basic seed=0 time=0.04s steps=17)
```

**Failure modes** (all non-zero exit; where applicable the message includes
the same `<stats>` block as the success line):

| condition                                   | message                                                      |
| ------------------------------------------- | ------------------------------------------------------------ |
| unreadable / invalid grid file              | `error: <path>: <detail>`                                    |
| unreadable dictionary                       | `error: <path>: <detail>`                                    |
| bad lock spec                               | `error: <spec-specific message>` (section 1.3)               |
| missing word length                         | `error: dictionary has no words of length <L>`               |
| locks determined to be unsatisfiable        | `locked words admit no solution for this grid (<stats>)`     |
| deadline reached without a solution         | `no solution found within <timeout>s (<stats>)`              |
| solver returned a solution violating a lock | `internal error: locked slots [...] not honoured`            |
| solver returned an invalid fill             | `invalid solution:` followed by one indented line per defect |

### 2.3 `list-solvers`

No arguments. Prints one line per available solver, sorted by name:
the name (padded to a common width), its one-line description, and
` (default)` appended to the default solver.

```
basic  One-line description of this solver. (default)
other  One-line description of another solver.
```

Exit 0.

## 3. `benchmark` tool

Runs every **(grid, solver, seed)** combination over a directory of grid
files and prints a table of solve times. No locked words are involved.

```
benchmark [--solvers A,B] [--seeds 0,1,2] [--timeout S]
          [--grids 51,87] [--grid-dir DIR] [--dict PATH]
```

**Options (all optional):**

| option       | default                                    | meaning                                                          |
| ------------ | ------------------------------------------ | ---------------------------------------------------------------- |
| `--solvers`  | the registered default solver              | comma-separated solver names                                     |
| `--seeds`    | `0`                                        | comma-separated integer seeds                                    |
| `--timeout`  | `5.0`                                      | per-run time budget in seconds                                   |
| `--grids`    | all                                        | comma-separated grid ids; filters by file basename               |
| `--grid-dir` | the repository's `grids/`                  | directory scanned recursively for `*.yaml` grid files            |
| `--dict`     | the repository's `dictionaries/words_alpha.txt` | dictionary file                                             |

**Behavior:**

1. Load the dictionary once; print
   `dictionary: <N> words loaded in <t.tt>s`.
2. Enumerate grid files under the grid directory (including
   subdirectories) sorted **numerically** by their integer basename (so `5`
   sorts before `51`); apply the `--grids` filter if given.
3. For each grid, build the problem once, then for each solver × seed run
   the solver with that seed and the timeout.
4. Every solution returned is **independently verified** (all cells filled,
   dictionary membership, no repeated words) before being counted as a
   success.

**Output:** a table, one row per run:

```
dictionary: 370105 words loaded in 0.12s
 grid  solver  seed    time  status  stats
------------------------------------------
    5   basic     0   0.01s  ok      steps=17
   51   basic     0   0.24s  ok      steps=402
```

Columns: grid id, solver name, seed, elapsed wall time, status, and the
solver's own statistics (the optional `key=value` pairs of section 2.2,
space-separated; may be empty). The first five columns are fixed-width;
`stats` is free-form and comes last. Status is:

- `ok` — solved and verified;
- `FAIL` — no solution within the timeout;
- `INVALID: <first defect>` — the solver returned a fill that failed
  verification.

**Epilogue and exit code:** after the table, a blank line, then either

- `all solved and verified` and exit 0, or
- `<N> failures:` followed by one indented
  `(grid, solver, seed, status)` tuple per non-`ok` run, and exit 1.

The non-zero exit on any failure makes the tool usable as a regression
gate in automation.
