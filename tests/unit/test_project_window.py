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


def test_open_and_save_actions_track_active_project(tmp_path) -> None:
    application = QApplication.instance()
    if application is None:
        application = QApplication([])

    project_path = tmp_path / "existing.edg"
    creator = ProjectService()
    assert creator.create_new_project(project_path, "Vorhanden").succeeded
    creator.close_project()

    service = ProjectService()
    window = MainWindow(service)
    actions = window.menuBar().actions()[0].menu().actions()
    open_action, save_action = actions[1], actions[2]
    assert open_action.text() == "Öffnen"
    assert open_action.isEnabled()
    assert save_action.text() == "Speichern"
    assert not save_action.isEnabled()

    with patch.object(
        QFileDialog,
        "getOpenFileName",
        return_value=(str(project_path), "GED Editor-Projekt (*.edg)"),
    ):
        open_action.trigger()

    assert service.current_project is not None
    assert service.current_project.project_name == "Vorhanden"
    assert save_action.isEnabled()
    assert actions[3].isEnabled()

    save_action.trigger()
    assert "Projekt gespeichert" in window.statusBar().currentMessage()

    window.close()
    application.processEvents()
