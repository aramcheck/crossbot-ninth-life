"""Compatibility entry point; prefer the installed `crossbot` command."""

from crossbot.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
