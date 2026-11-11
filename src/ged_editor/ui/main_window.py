"""Main application window."""

from PySide6.QtWidgets import QMainWindow

from ged_editor.app.constants import APP_NAME


class MainWindow(QMainWindow):
    """Minimal main window for the desktop application."""

    def __init__(self) -> None:
        """Initialize the main window with the application title."""
        super().__init__()
        self.setWindowTitle(APP_NAME)
