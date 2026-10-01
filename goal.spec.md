# goal - crossbot

Your goal is to implement the crossbot compiler as specified in the crossbot.spec.md file.

## Assets

- `dictionaries` - a directory containing the dictionaries to use to benchmark the crossbot compiler. One of them is in Spanish and contains words that use the special letter "ñ".
- `grids` - a directory containing the grids to use to benchmark the crossbot compiler. Start with the `core` grids and then move to `gecode` as you find more performing solvers.

## Dependencies

You are only allowed to use the following dependencies:

```
dependencies = [
    "pydantic>=2.13.4",
    "pydantic-settings>=2.15.0",
    "pyyaml>=6.0.3",
    "rich>=15.0.0",
]

[dependency-groups]
dev = [
    "black>=26.5.1",
    "mypy>=2.3.0",
    "pytest>=9.1.1",
    "types-pyyaml>=6.0",
]
```

With `mypy` setup in very strict mode:

```
[tool.mypy]
files = ["src"]
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_any_generics = true
disallow_any_explicit = true
disallow_subclassing_any = true
```

## Hard Constraints

- Since you are not allowed to use other external libraries or solvers, keep your algorithmic implementations clean and easy to follow and organize them into small, focused modules.
- Cover implementation with tests
- Keep solver implementations small and focused and make sure is easy to add new solvers in the future.
- Your exit condition is when all grids can be solved by the compiler with at least one of the dictionaries in less than 5 seconds.
- Aim for sub-second performance for at least 90% of the grids.
- The code should be an example of seasoned software engineering that can be used to teach a course that is a combination of software engineering and algorithmic problem solving.
- Keep the code in compliance and commit to the repository following the best practices of the industry.

## Deliverables

- All the code needed to implement the spec, benchmarks following hard constraints.
- A `README.md` file with instructions on how to run the benchmarks and the code as well as a full table of benchmark results.
- A written analysis of the final system, as specified in `documentation.spec.md`.
