from unittest.mock import patch

from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox

from ged_editor.app.constants import APP_NAME
from ged_editor.services.project_service import ProjectService
from ged_editor.ui.main_window import MainWindow


def test_file_menu_creates_a_new_edg_project(tmp_path) -> None:
    application = QApplication.instance()
    if application is None:
        application = QApplication([])

    project_path = tmp_path / "testprojekt.edg"
    service = ProjectService()
    window = MainWindow(service)
    file_menu = window.menuBar().actions()[0].menu()

    with (
        patch.object(
            QFileDialog,
            "getSaveFileName",
            return_value=(str(project_path), "GED Editor-Projekt (*.edg)"),
        ),
        patch.object(QMessageBox, "information"),
    ):
        file_menu.actions()[0].trigger()

    assert project_path.is_file()
    assert service.current_project is not None
    assert service.current_project.project_name == "Neues Projekt"
    assert window.windowTitle() == f"{APP_NAME} - Neues Projekt"

    window.close()
    application.processEvents()
