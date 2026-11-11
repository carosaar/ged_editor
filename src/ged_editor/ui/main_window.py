"""Main application window."""

from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from ged_editor.app.constants import APP_NAME
from ged_editor.services.gedcom_import_service import GEDCOMImportService
from ged_editor.services.project_service import ProjectService


class MainWindow(QMainWindow):
    """Main window with the project commands available in this phase."""

    def __init__(self, project_service: ProjectService | None = None) -> None:
        """Initialize the window, project service, and file menu."""
        super().__init__()
        self._project_service = project_service or ProjectService()
        self.setWindowTitle(APP_NAME)
        self._save_project_action: QAction | None = None
        self._gedcom_import_action: QAction | None = None
        self._create_file_menu()

    def _create_file_menu(self) -> None:
        file_menu = self.menuBar().addMenu("Datei")

        new_project_action = QAction("Neu", self)
        new_project_action.triggered.connect(lambda: self._create_new_project())
        file_menu.addAction(new_project_action)

        open_project_action = QAction("Öffnen", self)
        open_project_action.triggered.connect(lambda: self._open_project())
        file_menu.addAction(open_project_action)

        save_project_action = QAction("Speichern", self)
        save_project_action.setEnabled(self._project_service.current_project is not None)
        save_project_action.triggered.connect(lambda: self._save_project())
        file_menu.addAction(save_project_action)
        self._save_project_action = save_project_action

        import_gedcom_action = QAction("GEDCOM importieren", self)
        import_gedcom_action.setEnabled(self._project_service.connection is not None)
        import_gedcom_action.triggered.connect(self._import_gedcom)
        file_menu.addAction(import_gedcom_action)
        self._gedcom_import_action = import_gedcom_action

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

        self._set_active_project_ui(result.project.project_name)
        QMessageBox.information(
            self,
            "Projekt erstellt",
            f"Das Projekt „{result.project.project_name}“ wurde erstellt.",
        )

    def _open_project(self) -> None:
        selected_path, _ = QFileDialog.getOpenFileName(
            self,
            "Projekt öffnen",
            "",
            "GED Editor-Projekt (*.edg)",
        )
        if not selected_path:
            return

        result = self._project_service.open_project(selected_path)
        if not result.succeeded or result.project is None:
            QMessageBox.critical(
                self,
                "Projekt konnte nicht geöffnet werden",
                result.error_message or "Ein unbekannter Fehler ist aufgetreten.",
            )
            return

        self._set_active_project_ui(result.project.project_name)

    def _save_project(self) -> None:
        result = self._project_service.save_project()
        if not result.succeeded or result.project is None:
            QMessageBox.critical(
                self,
                "Projekt konnte nicht gespeichert werden",
                result.error_message or "Ein unbekannter Fehler ist aufgetreten.",
            )
            return
        self.statusBar().showMessage(
            f"Projekt gespeichert: {self._project_service.project_path}",
            5000,
        )

    def _set_active_project_ui(self, project_name: str) -> None:
        self.setWindowTitle(f"{APP_NAME} - {project_name}")
        if self._project_service.project_path is not None:
            self.statusBar().showMessage(str(self._project_service.project_path))
        if self._save_project_action is not None:
            self._save_project_action.setEnabled(True)
        if self._gedcom_import_action is not None:
            self._gedcom_import_action.setEnabled(True)

    def _import_gedcom(self) -> None:
        connection = self._project_service.connection
        if connection is None:
            QMessageBox.warning(
                self,
                "Kein Projekt geöffnet",
                "Öffnen oder erstellen Sie zuerst ein EDG-Projekt.",
            )
            return

        selected_path, _ = QFileDialog.getOpenFileName(
            self,
            "GEDCOM-Datei importieren",
            "",
            "GEDCOM-Dateien (*.ged *.GED);;Alle Dateien (*)",
        )
        if not selected_path:
            return

        result = GEDCOMImportService(connection).import_file(selected_path)
        if not result.succeeded:
            QMessageBox.critical(
                self,
                "GEDCOM-Import fehlgeschlagen",
                result.error_message or "Der GEDCOM-Import ist fehlgeschlagen.",
            )
            return

        message = (
            "Import abgeschlossen\n\n"
            f"Personen: {result.persons_imported}\n"
            f"Familien: {result.families_imported}\n"
            f"Quellen: {result.sources_imported}"
        )
        if result.warnings:
            message += "\n\nHinweise:\n" + "\n".join(result.warnings)
        QMessageBox.information(self, "GEDCOM-Import", message)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Close the active project connection before the window exits."""
        self._project_service.close_project()
        super().closeEvent(event)
