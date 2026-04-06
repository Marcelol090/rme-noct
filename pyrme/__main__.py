"""Entry point for PyRME application."""

import sys


def main() -> int:
    """Launch the PyRME application."""
    from pyrme.app import create_app, run_app

    app = create_app(sys.argv)
    return run_app(app)


if __name__ == "__main__":
    sys.exit(main())
