"""Application setup and event-loop management."""

import sys
from collections.abc import Sequence

from PySide6.QtWidgets import QApplication

from ged_editor.app.constants import APP_NAME
from ged_editor.app.settings import settings
from ged_editor.ui.main_window import MainWindow
from ged_editor.utils.logger import configure_logging, get_logger

logger = get_logger(__name__)


def create_application(argv: Sequence[str] | None = None) -> QApplication:
    """Create the Qt application using the provided or process arguments."""
    arguments = list(argv) if argv is not None else sys.argv
    application = QApplication.instance()
    if application is None:
        application = QApplication(arguments)
    return application


def run(argv: Sequence[str] | None = None) -> int:
    """Initialize the application window and run the Qt event loop."""
    configure_logging(settings.log_level)
    logger.info("Starting %s", APP_NAME)
    application = create_application(argv)
    window = MainWindow()
    window.show()
    return application.exec()
