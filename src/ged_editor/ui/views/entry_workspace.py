"""Urkunde-oriented marriage entry workspace."""

import logging
import sqlite3
from dataclasses import replace
from datetime import date, datetime
from functools import partial

from PySide6.QtCore import QRegularExpression, Qt, QTimer
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from ged_editor.models.marriage_record import (
    MarriageRecord,
    MarriageRecordExportStatus,
    MarriageRecordStatus,
)
from ged_editor.models.person import Person
from ged_editor.repositories.marriage_record_repository import (
    MarriageRecordRepository,
)
from ged_editor.repositories.person_repository import PersonRepository
from ged_editor.services.marriage_record_service import MarriageRecordService
from ged_editor.services.person_service import PersonService
from ged_editor.services.project_service import ProjectService
from ged_editor.ui.dialogs.person_search_dialog import PersonSearchDialog
from ged_editor.utils.marriage_dates import (
    local_date_for_display,
    parse_local_date,
    step_local_date,
    to_gedcom_date,
)

logger = logging.getLogger(__name__)
_RECORD_ID_ROLE = Qt.ItemDataRole.UserRole


class MarriageDateEdit(QLineEdit):
    """Date entry with the keyboard stepping defined for marriage dates."""

    def keyPressEvent(self, event) -> None:
        key = event.key()
        if key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            step = 1 if key == Qt.Key.Key_Up else -1
            modifiers = event.modifiers()
            if modifiers == Qt.KeyboardModifier.ShiftModifier:
                date_text = step_local_date(self.text(), months=step)
            elif modifiers == Qt.KeyboardModifier.ControlModifier:
                date_text = step_local_date(self.text(), years=step)
            elif modifiers == Qt.KeyboardModifier.NoModifier:
                date_text = step_local_date(self.text(), days=step)
            else:
                date_text = None
            if date_text is not None:
                self.setText(date_text)
            if modifiers in (
                Qt.KeyboardModifier.NoModifier,
                Qt.KeyboardModifier.ShiftModifier,
                Qt.KeyboardModifier.ControlModifier,
            ):
                event.accept()
                return
        super().keyPressEvent(event)


class MarriageEntryWorkspace(QWidget):
    """Provide the sorted certificate list and its active entry form."""

    def __init__(
        self,
        project_service: ProjectService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        connection = project_service.connection
        if connection is None:
            raise ValueError("An open project is required for the entry workspace.")
        self._project_service = project_service
        self._marriages = MarriageRecordService(connection)
        self._persons_service = PersonService(connection)
        self._record: MarriageRecord | None = None
        self._baseline_record: MarriageRecord | None = None
        self._people: dict[str, Person | None] = {"husband": None, "wife": None}
        self._person_editable = {"husband": False, "wife": False}
        self._person_widgets: dict[str, dict[str, QLineEdit]] = {}
        self._person_buttons: dict[str, tuple[QPushButton, QPushButton]] = {}
        self._default_sex: dict[str, str] = {}
        self._dirty = False
        self._created_person_ids: list[int] = []
        self._previous_selection_id: int | None = None
        self._existing_marriage_hint = QLabel(
            "Diese Ehe ist bereits im Projekt vorhanden."
        )
        self._existing_marriage_hint.setObjectName("existing_marriage_hint")
        self._existing_marriage_hint.setStyleSheet("color: #8a5a00;")
        self._existing_marriage_hint.hide()
        self._loading = False
        self._validation_attempted = False

        self._build_ui()
        self._connect_inputs()
        self.refresh_records()
        self.start_new_record()

    def _build_ui(self) -> None:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("Urkunden"))
        self.new_record_button = QPushButton("Neue Urkunde")
        left_layout.addWidget(self.new_record_button)
        self.all_years_checkbox = QCheckBox("Alle Jahrgänge anzeigen")
        self.all_years_checkbox.setObjectName("all_years_checkbox")
        left_layout.addWidget(self.all_years_checkbox)
        self.records_table = QTableWidget(0, 5)
        self.records_table.setObjectName("marriage_records_table")
        self.records_table.setHorizontalHeaderLabels(
            ("Jahrgang", "Nummer", "Ehemann", "Ehefrau", "Heiratsdatum")
        )
        self.records_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.records_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.records_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.records_table.horizontalHeader().setStretchLastSection(True)
        left_layout.addWidget(self.records_table)
        splitter.addWidget(left_panel)

        self._form_content = QWidget()
        form_layout = QVBoxLayout(self._form_content)
        form_layout.addWidget(self._build_certificate_group())
        form_layout.addWidget(self._build_marriage_group())
        form_layout.addWidget(self._build_person_group("husband", "Ehemann", "M"))
        form_layout.addWidget(self._build_person_group("wife", "Ehefrau", "F"))
        form_layout.addWidget(self._build_notes_group())
        form_layout.addWidget(self._build_actions())
        form_layout.addStretch(1)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self._form_content)
        splitter.addWidget(scroll_area)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout = QHBoxLayout(self)
        layout.addWidget(splitter)

    def _build_certificate_group(self) -> QGroupBox:
        group = QGroupBox("Urkunde")
        layout = QFormLayout(group)
        self.year_edit = QLineEdit()
        self.year_edit.setObjectName("year_edit")
        self.year_edit.setValidator(self._integer_validator())
        self.number_edit = QLineEdit()
        self.number_edit.setObjectName("number_edit")
        self.number_edit.setValidator(self._integer_validator())
        layout.addRow("Jahrgang", self.year_edit)
        layout.addRow("Registriernummer", self.number_edit)
        self.workflow_status_label = QLabel()
        self.workflow_status_label.setObjectName("workflow_status_label")
        layout.addRow("Workflowstatus", self.workflow_status_label)
        self.exported_read_only_label = QLabel(
            "Diese Urkunde wurde bereits exportiert und kann nicht mehr bearbeitet werden."
        )
        self.exported_read_only_label.setObjectName("exported_read_only_label")
        self.exported_read_only_label.setWordWrap(True)
        self.exported_read_only_label.setStyleSheet("color: #8a5a00;")
        self.exported_read_only_label.hide()
        layout.addRow(self.exported_read_only_label)
        return group

    def _build_marriage_group(self) -> QGroupBox:
        group = QGroupBox("Heirat")
        layout = QFormLayout(group)
        self.marriage_place_edit = QLineEdit()
        self.marriage_place_edit.setObjectName("marriage_place_edit")
        self.marriage_date_edit = MarriageDateEdit()
        self.marriage_date_edit.setObjectName("marriage_date_edit")
        self.marriage_date_edit.setPlaceholderText("TT.MM.JJJJ")
        self.marriage_date_gedcom_edit = QLineEdit()
        self.marriage_date_gedcom_edit.setObjectName(
            "marriage_date_gedcom_edit"
        )
        self.marriage_date_gedcom_edit.setReadOnly(True)
        self.marriage_date_error_label = QLabel()
        self.marriage_date_error_label.setObjectName("marriage_date_error")
        self.marriage_date_error_label.setStyleSheet("color: #b00020;")
        self.marriage_date_error_label.hide()
        date_row = QVBoxLayout()
        date_row.addWidget(self.marriage_date_edit)
        date_row.addWidget(self.marriage_date_gedcom_edit)
        date_row.addWidget(self.marriage_date_error_label)
        date_container = QWidget()
        date_container.setLayout(date_row)
        layout.addRow("Heiratsort", self.marriage_place_edit)
        layout.addRow("Heiratsdatum", date_container)
        return group

    def _build_person_group(
        self,
        side: str,
        title: str,
        default_sex: str,
    ) -> QGroupBox:
        group = QGroupBox(title)
        layout = QFormLayout(group)
        actions = QHBoxLayout()
        search_button = QPushButton("Person suchen")
        search_button.setObjectName(f"{side}_search_button")
        new_button = QPushButton("Neue Person")
        new_button.setObjectName(f"{side}_new_button")
        actions.addWidget(search_button)
        actions.addWidget(new_button)
        action_container = QWidget()
        action_container.setLayout(actions)
        layout.addRow(action_container)

        name_edit = QLineEdit()
        name_edit.setObjectName(f"{side}_name_edit")
        sex_edit = QLineEdit()
        sex_edit.setObjectName(f"{side}_sex_edit")
        sex_edit.setReadOnly(True)
        birth_date_edit = QLineEdit()
        birth_date_edit.setObjectName(f"{side}_birth_date_edit")
        birth_place_edit = QLineEdit()
        birth_place_edit.setObjectName(f"{side}_birth_place_edit")
        layout.addRow("Name", name_edit)
        layout.addRow("Geschlecht", sex_edit)
        layout.addRow("Geburtsdatum", birth_date_edit)
        layout.addRow("Geburtsort", birth_place_edit)
        if side == "wife":
            layout.addRow(self._existing_marriage_hint)

        self._person_widgets[side] = {
            "name": name_edit,
            "sex": sex_edit,
            "birth_date": birth_date_edit,
            "birth_place": birth_place_edit,
        }
        self._person_buttons[side] = (search_button, new_button)
        self._default_sex[side] = default_sex
        return group

    def _build_notes_group(self) -> QGroupBox:
        group = QGroupBox("Notizen")
        layout = QFormLayout(group)
        self._note_edits: dict[str, QPlainTextEdit] = {}
        notes = (
            ("note_origin_husband", "Herkunft Ehemann"),
            ("note_origin_wife", "Herkunft Ehefrau"),
            ("note_death_husband", "Todesvermerk Ehemann"),
            ("note_death_wife", "Todesvermerk Ehefrau"),
            ("note_legitimation", "Legitimation"),
            ("note_marginal", "Randvermerke"),
            ("note_comments", "Kommentare"),
        )
        for field_name, label in notes:
            editor = QPlainTextEdit()
            editor.setObjectName(field_name)
            editor.setMaximumHeight(90)
            self._note_edits[field_name] = editor
            layout.addRow(label, editor)
        return group

    def _build_actions(self) -> QWidget:
        row = QHBoxLayout()
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.setObjectName("cancel_entry_button")
        self.reopen_button = QPushButton("Zur Bearbeitung")
        self.reopen_button.setObjectName("reopen_button")
        self.finish_button = QPushButton("Fertig")
        self.finish_button.setObjectName("finish_button")
        self.next_record_button = QPushButton("Nächste Urkunde")
        self.next_record_button.setObjectName("next_record_button")
        row.addWidget(self.cancel_button)
        row.addWidget(self.reopen_button)
        row.addWidget(self.finish_button)
        row.addWidget(self.next_record_button)
        container = QWidget()
        container.setLayout(row)
        return container

    def _connect_inputs(self) -> None:
        self.new_record_button.clicked.connect(self._start_new_from_button)
        self.all_years_checkbox.toggled.connect(self._all_years_toggled)
        self.records_table.cellDoubleClicked.connect(self._open_record_at_row)
        self.year_edit.textChanged.connect(
            lambda: self._handle_record_change(refresh_list=True)
        )
        self.number_edit.textChanged.connect(
            lambda: self._handle_record_change(refresh_list=True)
        )
        self.marriage_place_edit.textChanged.connect(
            lambda: self._handle_record_change()
        )
        self.marriage_date_edit.textChanged.connect(self._date_changed)
        for editor in self._note_edits.values():
            editor.textChanged.connect(self._handle_record_change)
        for side, widgets in self._person_widgets.items():
            widgets["name"].textChanged.connect(
                partial(
                    self._person_field_changed,
                    side,
                    "name",
                    refresh_list=True,
                )
            )
            widgets["birth_date"].textChanged.connect(
                partial(self._person_field_changed, side, "birth_date")
            )
            widgets["birth_place"].textChanged.connect(
                partial(
                    self._person_field_changed,
                    side,
                    "birth_place",
                    refresh_list=True,
                )
            )
            search_button, new_button = self._person_buttons[side]
            search_button.clicked.connect(partial(self._search_person, side))
            new_button.clicked.connect(partial(self._create_person, side))
        self.finish_button.clicked.connect(self.finish_record)
        self.reopen_button.clicked.connect(self.reopen_record)
        self.cancel_button.clicked.connect(self.cancel_entry)
        self.next_record_button.clicked.connect(self._start_next_record)

    @staticmethod
    def _integer_validator() -> QRegularExpressionValidator:
        return QRegularExpressionValidator(QRegularExpression("[0-9]*"))

    def refresh_records(self, select_record_id: int | None = None) -> None:
        """Reload the year-filtered certificate list in date/number order."""
        records = self._marriages.list_all()
        current_year = self._parse_integer(self.year_edit.text())
        if not self.all_years_checkbox.isChecked() and current_year is not None:
            records = [record for record in records if record.year == current_year]
        records.sort(key=self._record_sort_key)
        people = {
            person.id: person
            for person in self._persons_service.search()
            if person.id is not None
        }
        self.records_table.setRowCount(len(records))
        selected_row = -1
        for row, record in enumerate(records):
            husband = people.get(record.husb_person_id)
            wife = people.get(record.wife_person_id)
            values = (
                "" if record.year is None else str(record.year),
                "" if record.number is None else str(record.number),
                "" if husband is None else husband.name,
                "" if wife is None else wife.name,
                local_date_for_display(
                    record.marriage_date_raw,
                    record.marriage_date_gedcom,
                ),
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(_RECORD_ID_ROLE, record.id)
                self.records_table.setItem(row, column, item)
            if record.id == select_record_id:
                selected_row = row
        if selected_row >= 0:
            self.records_table.selectRow(selected_row)
        else:
            self.records_table.clearSelection()

    @staticmethod
    def _record_sort_key(record: MarriageRecord) -> tuple[bool, date, bool, int, int]:
        date_text = local_date_for_display(
            record.marriage_date_raw,
            record.marriage_date_gedcom,
        )
        parsed_date = parse_local_date(date_text)
        return (
            parsed_date is None,
            date.max if parsed_date is None else parsed_date,
            record.number is None,
            0 if record.number is None else record.number,
            0 if record.id is None else record.id,
        )

    def _all_years_toggled(self, checked: bool) -> None:
        del checked
        self.refresh_records()

    def _selected_record_id(self) -> int | None:
        selected_items = self.records_table.selectedItems()
        if not selected_items:
            return None
        record_id = selected_items[0].data(_RECORD_ID_ROLE)
        return record_id if isinstance(record_id, int) else None

    def _start_new_from_button(self, checked: bool = False) -> None:
        del checked
        previous_id = self._selected_record_id()
        if previous_id is None and self._record is not None:
            previous_id = self._record.id
        self.start_new_record(previous_selection_id=previous_id)

    def _start_next_record(self, checked: bool = False) -> None:
        del checked
        previous_id = None if self._record is None else self._record.id
        self.start_new_record(previous_selection_id=previous_id)

    def start_new_record(
        self,
        *,
        prefill_husband: Person | None = None,
        prefill_wife: Person | None = None,
        previous_selection_id: int | None = None,
    ) -> None:
        """Reset the form with latest-record defaults and optional spouses."""
        latest = self._latest_record()
        self._loading = True
        self._record = None
        self._baseline_record = None
        self._dirty = False
        self._created_person_ids = []
        self._previous_selection_id = previous_selection_id
        self._validation_attempted = False
        self._people = {"husband": prefill_husband, "wife": prefill_wife}
        self._person_editable = {"husband": False, "wife": False}
        self.year_edit.setText(
            "" if latest is None or latest.year is None else str(latest.year)
        )
        self.number_edit.clear()
        self.marriage_place_edit.setText(
            self._project_service.get_meta_value("marriage_place_default") or ""
        )
        self.marriage_date_edit.setText(
            ""
            if latest is None
            else local_date_for_display(
                latest.marriage_date_raw,
                latest.marriage_date_gedcom,
            )
        )
        for editor in self._note_edits.values():
            editor.clear()
        self._load_person("husband", prefill_husband, editable=False)
        self._load_person("wife", prefill_wife, editable=False)
        self._loading = False
        self.records_table.clearSelection()
        self._update_date_display()
        self._set_record_controls()
        self._update_existing_marriage_hint()
        self.refresh_records()
        QTimer.singleShot(0, self.number_edit.setFocus)

    def finish_record(self) -> bool:
        """Validate required data and explicitly set the workflow to Fertig."""
        if not self._can_edit():
            return False
        self._validation_attempted = True
        errors = self._required_field_errors()
        self._show_required_field_errors(errors)
        if errors:
            QMessageBox.warning(
                self,
                "Urkunde unvollständig",
                "Die Urkunde kann noch nicht abgeschlossen werden:\n\n"
                + "\n".join(errors.values()),
            )
            return False
        if not self._persist_record(refresh_list=True):
            return False
        if self._record is None:
            return False
        updated = replace(
            self._record,
            workflow_status=MarriageRecordStatus.FERTIG,
            modified_at=datetime.now(),
        )
        try:
            saved = self._marriages.update(updated)
        except sqlite3.Error as error:
            self._show_persistence_error(error)
            return False
        if saved is None:
            self._show_persistence_error(
                sqlite3.DatabaseError("Die Urkunde konnte nicht gespeichert werden.")
            )
            return False
        self._record = saved
        self._baseline_record = saved
        self._previous_selection_id = saved.id
        self._dirty = False
        self._created_person_ids = []
        self.refresh_records(saved.id)
        self._set_record_controls()
        return True

    def reopen_record(self) -> bool:
        """Move a finished record back to In Bearbeitung."""
        if (
            self._record is None
            or self._record.export_status is MarriageRecordExportStatus.EXPORTIERT
        ):
            return False
        updated = replace(
            self._record,
            workflow_status=MarriageRecordStatus.IN_BEARBEITUNG,
            modified_at=datetime.now(),
        )
        try:
            saved = self._marriages.update(updated)
        except sqlite3.Error as error:
            self._show_persistence_error(error)
            return False
        if saved is None:
            self._show_persistence_error(
                sqlite3.DatabaseError("Die Urkunde konnte nicht gespeichert werden.")
            )
            return False
        self._record = saved
        self._baseline_record = saved
        self._previous_selection_id = saved.id
        self._dirty = False
        self._created_person_ids = []
        self._validation_attempted = False
        self.refresh_records(saved.id)
        self._set_record_controls()
        return True

    def cancel_entry(self) -> bool:
        """Discard the active entry session and restore its previous selection."""
        if self._dirty:
            answer = QMessageBox.question(
                self,
                "Erfassung abbrechen",
                "Nicht gespeicherte Änderungen verwerfen?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return False

            connection = self._project_service.connection
            if connection is None:
                self._show_cancel_error(
                    sqlite3.DatabaseError("Es ist kein Projekt geöffnet.")
                )
                return False
            marriages = MarriageRecordRepository(connection)
            persons = PersonRepository(connection)
            try:
                with connection:
                    if self._baseline_record is None:
                        if (
                            self._record is not None
                            and self._record.id is not None
                            and not marriages.delete(self._record.id)
                        ):
                            raise sqlite3.DatabaseError(
                                "Die neue Urkunde konnte nicht zurückgesetzt werden."
                            )
                    elif marriages.update(self._baseline_record) is None:
                        raise sqlite3.DatabaseError(
                            "Die vorherige Urkunde konnte nicht wiederhergestellt werden."
                        )
                    for person_id in self._created_person_ids:
                        if not persons.delete(person_id):
                            raise sqlite3.DatabaseError(
                                "Eine neu angelegte Person konnte nicht entfernt werden."
                            )
            except sqlite3.Error as error:
                self._show_cancel_error(error)
                return False

        previous_id = self._previous_selection_id
        previous = (
            None if previous_id is None else self._marriages.get_by_id(previous_id)
        )
        if previous is not None:
            self._load_record(previous)
            self.refresh_records(previous.id)
        else:
            self.start_new_record()
        return True

    def _latest_record(self) -> MarriageRecord | None:
        records = self._marriages.list_all()
        if not records:
            return None
        return max(records, key=lambda record: (record.created_at, record.id or 0))

    def _open_record_at_row(self, row: int, column: int) -> None:
        if not 0 <= column < self.records_table.columnCount():
            return
        item = self.records_table.item(row, 0)
        if item is None:
            return
        record_id = item.data(_RECORD_ID_ROLE)
        if not isinstance(record_id, int):
            return
        record = self._marriages.get_by_id(record_id)
        if record is not None:
            if record.year is None or record.number is None:
                self.start_new_record(
                    prefill_husband=self._persons_service.get_by_id(
                        record.husb_person_id
                    ),
                    prefill_wife=self._persons_service.get_by_id(
                        record.wife_person_id
                    ),
                    previous_selection_id=record.id,
                )
            else:
                self._load_record(record)

    def _load_record(self, record: MarriageRecord) -> None:
        self._loading = True
        self._record = record
        self._baseline_record = record
        self._dirty = False
        self._created_person_ids = []
        self._previous_selection_id = record.id
        self._validation_attempted = False
        self.year_edit.setText("" if record.year is None else str(record.year))
        self.number_edit.setText(
            "" if record.number is None else str(record.number)
        )
        self.marriage_place_edit.setText(record.marriage_place or "")
        self.marriage_date_edit.setText(
            local_date_for_display(
                record.marriage_date_raw,
                record.marriage_date_gedcom,
            )
        )
        for field_name, editor in self._note_edits.items():
            editor.setPlainText(getattr(record, field_name) or "")
        self._load_person(
            "husband",
            self._persons_service.get_by_id(record.husb_person_id),
            editable=False,
        )
        self._load_person(
            "wife",
            self._persons_service.get_by_id(record.wife_person_id),
            editable=False,
        )
        self._loading = False
        self._update_date_display()
        self._show_required_field_errors({})
        self._set_record_controls()
        self._update_existing_marriage_hint()
        self.refresh_records(record.id)

    def _load_person(
        self,
        side: str,
        person: Person | None,
        *,
        editable: bool,
    ) -> None:
        was_loading = self._loading
        self._loading = True
        self._people[side] = person
        self._person_editable[side] = editable
        widgets = self._person_widgets[side]
        widgets["name"].setText("" if person is None else person.name)
        widgets["sex"].setText(
            "" if person is None or person.sex is None else person.sex
        )
        widgets["birth_date"].setText(
            ""
            if person is None or person.birth_date_raw is None
            else person.birth_date_raw
        )
        widgets["birth_place"].setText(
            ""
            if person is None or person.birth_place is None
            else person.birth_place
        )
        self._set_person_widget_editability(side)
        self._loading = was_loading

    def _search_person(self, side: str, checked: bool = False) -> None:
        del checked
        if not self._can_edit():
            return
        dialog = PersonSearchDialog(
            self._persons_service,
            required_sex=self._default_sex[side],
            parent=self,
        )
        if dialog.exec() == PersonSearchDialog.DialogCode.Accepted:
            person = dialog.selected_person
            if person is not None:
                self._load_person(side, person, editable=False)
                self._handle_record_change(refresh_list=True)
                self._update_existing_marriage_hint()

    def _create_person(self, side: str, checked: bool = False) -> None:
        del checked
        if not self._can_edit():
            return
        now = datetime.now()
        try:
            person = self._persons_service.create(
                Person(
                    id=None,
                    gedcom_xref=None,
                    name="",
                    sex=self._default_sex[side],
                    created_at=now,
                    modified_at=now,
                )
            )
        except sqlite3.Error as error:
            self._show_persistence_error(error)
            return
        if person.id is not None:
            self._created_person_ids.append(person.id)
        self._dirty = True
        self._load_person(side, person, editable=True)
        self._handle_record_change(refresh_list=True)
        self._update_existing_marriage_hint()
        self._person_widgets[side]["name"].setFocus()

    def _person_field_changed(
        self,
        side: str,
        field_name: str,
        value: str,
        *,
        refresh_list: bool = False,
    ) -> None:
        if self._person_widgets[side][field_name].text() != value:
            return
        self._person_changed(side, refresh_list=refresh_list)

    def _person_changed(self, side: str, *, refresh_list: bool = False) -> None:
        if self._loading or not self._can_edit():
            return
        person = self._people[side]
        if person is None or not self._person_editable[side]:
            return
        self._dirty = True
        widgets = self._person_widgets[side]
        updated = replace(
            person,
            name=widgets["name"].text(),
            modified_at=datetime.now(),
            birth_date_raw=widgets["birth_date"].text() or None,
            birth_place=widgets["birth_place"].text() or None,
        )
        try:
            saved_person = self._persons_service.update(updated)
        except sqlite3.Error as error:
            self._show_persistence_error(error)
            return
        if saved_person is None:
            self._show_persistence_error(
                sqlite3.DatabaseError("Die Person konnte nicht gespeichert werden.")
            )
            return
        self._people[side] = saved_person
        self._handle_record_change(refresh_list=refresh_list)

    def _date_changed(self) -> None:
        if self._loading:
            return
        self._update_date_display()
        self._handle_record_change(refresh_list=True)

    def _update_date_display(self) -> None:
        value = parse_local_date(self.marriage_date_edit.text())
        if value is None:
            self.marriage_date_gedcom_edit.clear()
            if self.marriage_date_edit.text():
                self.marriage_date_error_label.setText(
                    "Ungültiges Datum. Bitte TT.MM.JJJJ eingeben."
                )
                self.marriage_date_error_label.show()
                self._mark_invalid(self.marriage_date_edit, True)
            else:
                self.marriage_date_error_label.clear()
                self.marriage_date_error_label.hide()
                self._mark_invalid(self.marriage_date_edit, False)
            return
        self.marriage_date_gedcom_edit.setText(to_gedcom_date(value))
        self.marriage_date_error_label.clear()
        self.marriage_date_error_label.hide()
        self._mark_invalid(self.marriage_date_edit, False)

    def _handle_record_change(self, *, refresh_list: bool = False) -> None:
        if self._loading or not self._can_edit():
            return
        self._dirty = True
        if not self._persist_record(refresh_list=refresh_list):
            return
        if self._validation_attempted:
            self._show_required_field_errors(self._required_field_errors())
        self._update_existing_marriage_hint()

    def _persist_record(self, *, refresh_list: bool) -> bool:
        record = self._build_record()
        try:
            if self._record is None:
                self._record = self._marriages.create(record)
            else:
                saved = self._marriages.update(record)
                if saved is None:
                    self._show_persistence_error(
                        sqlite3.DatabaseError(
                            "Die Urkunde konnte nicht gespeichert werden."
                        )
                    )
                    return False
                self._record = saved
        except sqlite3.Error as error:
            self._show_persistence_error(error)
            return False
        if refresh_list:
            self.refresh_records(self._record.id)
        self.workflow_status_label.setText(self._record.workflow_status.value)
        self._set_record_controls()
        return True

    def _build_record(self) -> MarriageRecord:
        now = datetime.now()
        current = self._record
        parsed_date = parse_local_date(self.marriage_date_edit.text())
        return MarriageRecord(
            id=None if current is None else current.id,
            year=self._parse_integer(self.year_edit.text()),
            number=self._parse_positive_integer(self.number_edit.text()),
            display_number=self._display_number(),
            workflow_status=(
                MarriageRecordStatus.IN_BEARBEITUNG
                if current is None
                else current.workflow_status
            ),
            created_at=now if current is None else current.created_at,
            modified_at=now,
            husb_person_id=self._person_id("husband"),
            wife_person_id=self._person_id("wife"),
            marriage_date_raw=self.marriage_date_edit.text() or None,
            marriage_date_gedcom=(
                None if parsed_date is None else to_gedcom_date(parsed_date)
            ),
            marriage_place=self.marriage_place_edit.text() or None,
            note_origin_husband=self._note_value("note_origin_husband"),
            note_origin_wife=self._note_value("note_origin_wife"),
            note_death_husband=self._note_value("note_death_husband"),
            note_death_wife=self._note_value("note_death_wife"),
            note_legitimation=self._note_value("note_legitimation"),
            note_marginal=self._note_value("note_marginal"),
            note_comments=self._note_value("note_comments"),
            gedcom_xref=None if current is None else current.gedcom_xref,
            source_snapshot=None if current is None else current.source_snapshot,
            export_status=(
                MarriageRecordExportStatus.NICHT_EXPORTIERT
                if current is None
                else current.export_status
            ),
        )

    def _display_number(self) -> str:
        year = self._parse_integer(self.year_edit.text())
        number = self._parse_positive_integer(self.number_edit.text())
        return "" if year is None or number is None else f"{number}/{year}"

    @staticmethod
    def _parse_integer(value: str) -> int | None:
        text = value.strip()
        if not text or not text.isdecimal():
            return None
        try:
            parsed = int(text)
        except ValueError:
            return None
        return parsed if 0 < parsed <= 2**63 - 1 else None

    @classmethod
    def _parse_positive_integer(cls, value: str) -> int | None:
        return cls._parse_integer(value)

    def _person_id(self, side: str) -> int | None:
        person = self._people[side]
        return None if person is None else person.id

    def _note_value(self, field_name: str) -> str | None:
        return self._note_edits[field_name].toPlainText() or None

    def _required_field_errors(self) -> dict[str, str]:
        errors: dict[str, str] = {}
        if self._parse_integer(self.year_edit.text()) is None:
            errors["year_edit"] = "Jahrgang muss eine positive Ganzzahl sein."
        if self._parse_positive_integer(self.number_edit.text()) is None:
            errors["number_edit"] = (
                "Registriernummer muss eine positive Ganzzahl sein."
            )
        if parse_local_date(self.marriage_date_edit.text()) is None:
            errors["marriage_date_edit"] = (
                "Heiratsdatum muss ein gültiges Datum im Format TT.MM.JJJJ sein."
            )
        if not self.marriage_place_edit.text().strip():
            errors["marriage_place_edit"] = "Heiratsort fehlt."
        for side, label in (("husband", "Ehemann"), ("wife", "Ehefrau")):
            person = self._people[side]
            if person is None or person.id is None:
                errors[f"{side}_person"] = f"{label} fehlt."
            elif not self._person_widgets[side]["name"].text().strip():
                errors[f"{side}_name_edit"] = f"Name {label} fehlt."
        return errors

    def _show_required_field_errors(self, errors: dict[str, str]) -> None:
        fields = {
            "year_edit": self.year_edit,
            "number_edit": self.number_edit,
            "marriage_date_edit": self.marriage_date_edit,
            "marriage_place_edit": self.marriage_place_edit,
            "husband_name_edit": self._person_widgets["husband"]["name"],
            "wife_name_edit": self._person_widgets["wife"]["name"],
        }
        for field_name, widget in fields.items():
            self._mark_invalid(widget, field_name in errors)
        for side in ("husband", "wife"):
            self._mark_invalid(
                self._person_buttons[side][0],
                f"{side}_person" in errors,
            )
        if "marriage_date_edit" in errors:
            self.marriage_date_error_label.setText(
                errors["marriage_date_edit"]
            )
            self.marriage_date_error_label.show()
        elif parse_local_date(self.marriage_date_edit.text()) is not None:
            self.marriage_date_error_label.clear()
            self.marriage_date_error_label.hide()

    @staticmethod
    def _mark_invalid(widget: QWidget, invalid: bool) -> None:
        widget.setStyleSheet(
            "background-color: #ffe8e8;" if invalid else ""
        )

    def _update_existing_marriage_hint(self) -> None:
        husband = self._people["husband"]
        wife = self._people["wife"]
        found = (
            husband is not None
            and wife is not None
            and husband.id is not None
            and wife.id is not None
            and self._marriages.has_spouse_pair(
                husband.id,
                wife.id,
                excluding_record_id=(
                    None if self._record is None else self._record.id
                ),
            )
        )
        self._existing_marriage_hint.setVisible(found)

    def _set_record_controls(self) -> None:
        self.workflow_status_label.setText(
            MarriageRecordStatus.IN_BEARBEITUNG.value
            if self._record is None
            else self._record.workflow_status.value
        )
        can_edit = self._can_edit()
        for widget in (
            self.year_edit,
            self.number_edit,
            self.marriage_place_edit,
            self.marriage_date_edit,
            *self._note_edits.values(),
        ):
            widget.setEnabled(can_edit)
        for side in ("husband", "wife"):
            for button in self._person_buttons[side]:
                button.setEnabled(can_edit)
            self._set_person_widget_editability(side)
        self.finish_button.setEnabled(can_edit)
        is_exported = (
            self._record is not None
            and self._record.export_status is MarriageRecordExportStatus.EXPORTIERT
        )
        self.exported_read_only_label.setVisible(is_exported)
        is_finished = (
            self._record is not None
            and self._record.workflow_status is MarriageRecordStatus.FERTIG
        )
        self.reopen_button.setEnabled(is_finished and not is_exported)
        self.next_record_button.setEnabled(is_finished)

    def _set_person_widget_editability(self, side: str) -> None:
        can_edit_person = self._can_edit() and self._person_editable[side]
        for field_name, widget in self._person_widgets[side].items():
            if field_name == "sex":
                continue
            widget.setReadOnly(not can_edit_person)
            widget.setEnabled(self._can_edit())

    def _can_edit(self) -> bool:
        return (
            self._record is None
            or (
                self._record.export_status
                is not MarriageRecordExportStatus.EXPORTIERT
                and self._record.workflow_status
                is MarriageRecordStatus.IN_BEARBEITUNG
            )
        )

    def _show_persistence_error(self, error: sqlite3.Error) -> None:
        logger.error("Could not save marriage entry: %s", error)
        QMessageBox.critical(
            self,
            "Speichern fehlgeschlagen",
            f"Die Erfassungsdaten konnten nicht gespeichert werden:\n{error}",
        )

    def _show_cancel_error(self, error: sqlite3.Error) -> None:
        logger.error("Could not discard marriage entry changes: %s", error)
        QMessageBox.critical(
            self,
            "Abbrechen fehlgeschlagen",
            f"Die Änderungen konnten nicht verworfen werden:\n{error}",
        )

