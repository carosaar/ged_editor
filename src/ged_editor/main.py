"""Command-line entry point for ged_editor."""

from ged_editor.app.application import run


def main() -> int:
    """Start the desktop application."""
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
