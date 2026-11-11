"""Main application window."""

from PySide6.QtGui import QCloseEvent, QAction
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from ged_editor.app.constants import APP_NAME
from ged_editor.services.project_service import ProjectService


class MainWindow(QMainWindow):
    """Main window with the project commands available in this phase."""

    def __init__(self, project_service: ProjectService | None = None) -> None:
        """Initialize the window, project service, and file menu."""
        super().__init__()
        self._project_service = project_service or ProjectService()
        self.setWindowTitle(APP_NAME)
        self._create_file_menu()

    def _create_file_menu(self) -> None:
        file_menu = self.menuBar().addMenu("Datei")

        new_project_action = QAction("Neues Projekt", self)
        new_project_action.triggered.connect(lambda: self._create_new_project())
        file_menu.addAction(new_project_action)

        open_project_action = QAction("Projekt öffnen", self)
        open_project_action.setEnabled(False)
        file_menu.addAction(open_project_action)

        save_project_action = QAction("Projekt speichern", self)
        save_project_action.setEnabled(False)
        file_menu.addAction(save_project_action)

        file_menu.addSeparator()
        exit_action = QAction("Beenden", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _create_new_project(self) -> None:
        selected_path, _ = QFileDialog.getSaveFileName(
            self,
            "Neues Projekt erstellen",
            "",
            "GED Editor-Projekt (*.edg)",
        )
        if not selected_path:
            return

        result = self._project_service.create_new_project(selected_path)
        if not result.succeeded or result.project is None:
            QMessageBox.critical(
                self,
                "Projekt konnte nicht erstellt werden",
                result.error_message or "Ein unbekannter Fehler ist aufgetreten.",
            )
            return

        self.setWindowTitle(f"{APP_NAME} - {result.project.project_name}")
        self.statusBar().showMessage(str(self._project_service.project_path))
        QMessageBox.information(
            self,
            "Projekt erstellt",
            f"Das Projekt „{result.project.project_name}“ wurde erstellt.",
        )

    def closeEvent(self, event: QCloseEvent) -> None:
        """Close the active project connection before the window exits."""
        self._project_service.close_project()
        super().closeEvent(event)
