"""Simple project-person search dialog for the marriage entry form."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)

from ged_editor.models.person import Person
from ged_editor.services.person_service import PersonService


class PersonSearchDialog(QDialog):
    """Search existing project people and return the selected person."""

    def __init__(
        self,
        person_service: PersonService,
        *,
        required_sex: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._person_service = person_service
        self._required_sex = required_sex
        self.setWindowTitle("Person suchen")
        self.resize(480, 360)

        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText(
            "Name, Geburtsdatum oder Geburtsort suchen"
        )
        self._people_list = QListWidget()
        self._empty_label = QLabel("Keine Personen gefunden.")
        self._empty_label.hide()
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        self._select_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
        self._select_button.setText("Übernehmen")
        self._select_button.setEnabled(False)

        layout = QVBoxLayout(self)
        layout.addWidget(self._search_edit)
        layout.addWidget(self._people_list)
        layout.addWidget(self._empty_label)
        layout.addWidget(buttons)

        self._search_edit.textChanged.connect(self._refresh_people)
        self._people_list.currentItemChanged.connect(
            self._selection_changed
        )
        self._people_list.itemDoubleClicked.connect(self._accept_person)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self._refresh_people("")

    @property
    def selected_person(self) -> Person | None:
        """Return the selected person from the current project."""
        item = self._people_list.currentItem()
        if item is None:
            return None
        person_id = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(person_id, int):
            return None
        return self._person_service.get_by_id(person_id)

    def _refresh_people(self, search_text: str) -> None:
        people = self._person_service.search(
            search_text,
            sex=self._required_sex,
        )
        self._people_list.clear()
        for person in people:
            item = QListWidgetItem(self._person_label(person))
            item.setData(Qt.ItemDataRole.UserRole, person.id)
            self._people_list.addItem(item)
        is_empty = not people
        self._people_list.setVisible(not is_empty)
        self._empty_label.setVisible(is_empty)
        self._select_button.setEnabled(False)

    def _accept_person(self, item: QListWidgetItem) -> None:
        self._people_list.setCurrentItem(item)
        if self.selected_person is not None:
            self.accept()

    def _selection_changed(
        self,
        current: QListWidgetItem | None,
        previous: QListWidgetItem | None,
    ) -> None:
        del previous
        self._select_button.setEnabled(current is not None)

    @staticmethod
    def _person_label(person: Person) -> str:
        details = [person.name]
        if person.sex:
            details.append(person.sex)
        if person.birth_place:
            details.append(person.birth_place)
        return " — ".join(details)
