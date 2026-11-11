"""Tests for application setup and lifecycle."""

from unittest.mock import patch

from PySide6.QtWidgets import QApplication

from ged_editor.app.application import run
from ged_editor.app.constants import APP_NAME
from ged_editor.ui.main_window import MainWindow


def test_run_shows_the_main_window_and_returns_exit_code() -> None:
    shown_titles: list[str] = []

    def show_window(window: MainWindow) -> None:
        shown_titles.append(window.windowTitle())

    with (
        patch.object(MainWindow, "show", show_window),
        patch.object(QApplication, "exec", return_value=3),
    ):
        result = run([])

    assert result == 3
    assert shown_titles == [APP_NAME]
