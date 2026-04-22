"""Entry point for PyRME application."""

from __future__ import annotations

import argparse
import sys


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pyrme")
    subparsers = parser.add_subparsers(dest="command")

    stack_parser = subparsers.add_parser(
        "stack",
        help="List and validate the local agent stack",
    )
    stack_parser.add_argument("--json", action="store_true", help="Print JSON output")
    stack_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Print only failures and return a non-zero exit code on issues",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Launch the PyRME application or stack report."""
    args = list(argv if argv is not None else sys.argv)
    parser = _build_parser()
    parsed = parser.parse_args(args[1:])

    if parsed.command == "stack":
        from pyrme.devtools.codex.stack_report import build_stack_report

        report = build_stack_report()
        ok = getattr(report, "ok", True)
        if getattr(parsed, "json", False):
            print(report.render_json(), end="")
        elif not getattr(parsed, "quiet", False) or not ok:
            print(report.render(), end="")
        return 0 if ok else 1

    from pyrme.app import create_app, run_app

    app = create_app(args)
    return run_app(app)


if __name__ == "__main__":
    sys.exit(main())
