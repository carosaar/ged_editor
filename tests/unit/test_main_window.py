"""Tests for the main application window."""

from PySide6.QtWidgets import QApplication

from ged_editor.app.constants import APP_NAME
from ged_editor.ui.main_window import MainWindow


def test_main_window_has_application_title() -> None:
    application = QApplication.instance()
    if application is None:
        application = QApplication([])
    window = MainWindow()

    assert window.windowTitle() == APP_NAME

    window.close()
    application.processEvents()
