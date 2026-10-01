"""Re-verify persisted benchmark witnesses without consulting search domains."""

import json
from pathlib import Path

from crossbot.grid import load_grid
from crossbot.lexicon import load_dictionary
from crossbot.problem import build_problem
from crossbot.verify import verify
from measure import fingerprint, source_digest

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    data = json.loads((ROOT / "benchmarks/results.json").read_text())
    env = data["environment"]
    assert (
        source_digest() == env["source_sha256"]
    ), "source has changed since measurement"
    primary_path = ROOT / env["dictionary"]
    assert fingerprint(primary_path) == env["dictionary_sha256"]
    dictionaries = {primary_path.name: load_dictionary(primary_path)}
    verified = 0
    failures = 0
    for category in ("suite", "ablation", "other_dictionaries"):
        for row in data[category]:
            name = row.get("dictionary", primary_path.name)
            path = ROOT / "dictionaries" / name
            if "dictionary_sha256" in row:
                assert fingerprint(path) == row["dictionary_sha256"]
            if name not in dictionaries:
                dictionaries[name] = load_dictionary(path)
            problem = build_problem(load_grid(ROOT / row["grid"]), dictionaries[name])
            if row["assignment"] is None:
                assert row["status"] == "FAIL"
                failures += 1
            else:
                assignment = {int(k): v for k, v in row["assignment"].items()}
                defects = verify(problem, assignment)
                assert not defects, (row["grid"], row["solver"], defects)
                assert row["status"] == "ok"
                verified += 1
    print(
        f"audited: {verified} independently verified fills; {failures} explicitly retained failures"
    )


if __name__ == "__main__":
    main()
