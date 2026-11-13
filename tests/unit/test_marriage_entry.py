from dataclasses import replace
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QListWidget,
    QLineEdit,
    QMessageBox,
    QPushButton,
)

from ged_editor.database.connection import DatabaseConnection
from ged_editor.models import (
    MarriageRecord,
    MarriageRecordExportStatus,
    MarriageRecordStatus,
    Person,
)
from ged_editor.repositories.marriage_record_repository import (
    MarriageRecordRepository,
)
from ged_editor.services.marriage_record_service import MarriageRecordService
from ged_editor.services.person_service import PersonService
from ged_editor.services.project_service import ProjectService
from ged_editor.ui.main_window import MainWindow
from ged_editor.ui.dialogs.person_search_dialog import PersonSearchDialog
from ged_editor.ui.views.entry_workspace import (
    MarriageDateEdit,
    MarriageEntryWorkspace,
)
from ged_editor.utils.marriage_dates import (
    local_date_for_display,
    parse_local_date,
    step_local_date,
    to_gedcom_date,
)


def _application() -> QApplication:
    application = QApplication.instance()
    return application if application is not None else QApplication([])


def _open_project(tmp_path) -> ProjectService:
    service = ProjectService()
    result = service.create_new_project(tmp_path / "entry.edg", "Entry")
    assert result.succeeded
    return service


def _make_record(
    *,
    year: int | None,
    number: int | None,
    created_at: datetime,
    husb_person_id: int | None = None,
    wife_person_id: int | None = None,
    marriage_date_raw: str | None = None,
    marriage_date_gedcom: str | None = None,
    marriage_place: str | None = None,
) -> MarriageRecord:
    return MarriageRecord(
        id=None,
        year=year,
        number=number,
        display_number=(
            "" if year is None or number is None else f"{number}/{year}"
        ),
        workflow_status=MarriageRecordStatus.IN_BEARBEITUNG,
        created_at=created_at,
        modified_at=created_at,
        husb_person_id=husb_person_id,
        wife_person_id=wife_person_id,
        marriage_date_raw=marriage_date_raw,
        marriage_date_gedcom=marriage_date_gedcom,
        marriage_place=marriage_place,
        note_origin_husband=None,
        note_origin_wife=None,
        note_death_husband=None,
        note_death_wife=None,
        note_legitimation=None,
        note_marginal=None,
        note_comments=None,
    )


def test_local_marriage_date_validation_and_gedcom_display() -> None:
    assert parse_local_date("29.02.1900") is None
    parsed = parse_local_date("29.02.1904")
    assert parsed is not None
    assert to_gedcom_date(parsed) == "29 FEB 1904"
    assert local_date_for_display("12 MAY 1887", "12 MAY 1887") == "12.05.1887"
    assert local_date_for_display("12.05.1887", "12 MAY 1887") == "12.05.1887"


def test_date_stepping_clamps_month_and_year_end_dates() -> None:
    assert step_local_date("31.01.1887", months=1) == "28.02.1887"
    assert step_local_date("29.02.1904", years=1) == "28.02.1905"
    assert step_local_date("01.01.1900", days=-1) == "31.12.1899"
    assert step_local_date("31.02.1900", months=1) is None


def test_date_edit_arrow_keys_adjust_days_months_and_years() -> None:
    application = _application()
    editor = MarriageDateEdit()
    editor.setText("31.01.1887")
    editor.show()
    editor.setFocus()
    application.processEvents()

    QTest.keyClick(editor, Qt.Key.Key_Up, Qt.KeyboardModifier.ShiftModifier)
    assert editor.text() == "28.02.1887"
    QTest.keyClick(editor, Qt.Key.Key_Up, Qt.KeyboardModifier.ControlModifier)
    assert editor.text() == "28.02.1888"
    QTest.keyClick(editor, Qt.Key.Key_Down)
    assert editor.text() == "27.02.1888"
    editor.close()


def test_new_entry_uses_latest_record_and_project_place_default(tmp_path) -> None:
    application = _application()
    project = _open_project(tmp_path)
    connection = project.connection
    assert connection is not None
    connection.execute(
        'UPDATE meta SET "value" = ? WHERE "key" = ?',
        ("Sulzbach", "marriage_place_default"),
    )
    records = MarriageRecordService(connection)
    now = datetime.now()
    records.create(
        _make_record(
            year=1888,
            number=10,
            created_at=now - timedelta(days=1),
            marriage_date_raw="01.01.1888",
            marriage_date_gedcom="1 JAN 1888",
        )
    )
    records.create(
        _make_record(
            year=1887,
            number=5,
            created_at=now,
            marriage_date_raw="12 MAY 1887",
            marriage_date_gedcom="12 MAY 1887",
        )
    )

    workspace = MarriageEntryWorkspace(project)
    workspace.show()
    application.processEvents()

    assert workspace.year_edit.text() == "1887"
    assert workspace.number_edit.text() == ""
    assert workspace.marriage_date_edit.text() == "12.05.1887"
    assert workspace.marriage_date_gedcom_edit.text() == "12 MAY 1887"
    assert workspace.marriage_place_edit.text() == "Sulzbach"
    assert workspace.number_edit.hasFocus()
    assert not workspace.marriage_place_edit.hasFocus()
    project.close_project()


def test_opening_project_displays_entry_workspace(tmp_path) -> None:
    _application()
    project_path = tmp_path / "opened.edg"
    creator = ProjectService()
    assert creator.create_new_project(project_path, "Opened").succeeded
    creator.close_project()
    service = ProjectService()
    window = MainWindow(service)

    with patch.object(
        QFileDialog,
        "getOpenFileName",
        return_value=(str(project_path), "GED Editor-Projekt (*.edg)"),
    ):
        window._open_project()

    assert isinstance(window.centralWidget(), MarriageEntryWorkspace)
    window.close()


def test_marriage_records_are_sorted_by_year_then_number(tmp_path) -> None:
    database = DatabaseConnection(tmp_path / "sorted.edg")
    connection = database.connect(create=True)
    database.initialize_schema()
    repository = MarriageRecordRepository(connection)
    now = datetime.now()
    repository.create(_make_record(year=1890, number=3, created_at=now))
    repository.create(_make_record(year=1887, number=10, created_at=now))
    repository.create(_make_record(year=1887, number=2, created_at=now))
    repository.create(_make_record(year=None, number=None, created_at=now))

    records = repository.list_all()

    assert [(record.year, record.number) for record in records] == [
        (1887, 2),
        (1887, 10),
        (1890, 3),
        (None, None),
    ]
    database.close()


def test_person_search_and_spouse_pair_check_use_existing_records(tmp_path) -> None:
    database = DatabaseConnection(tmp_path / "matching.edg")
    connection = database.connect(create=True)
    database.initialize_schema()
    persons = PersonService(connection)
    husband = persons.create(
        Person(
            None,
            None,
            "Max Beispiel",
            "M",
            datetime.now(),
            datetime.now(),
            birth_date_raw="01.01.1860",
            birth_date_gedcom="1 JAN 1860",
            birth_place="Sulzbach",
        )
    )
    wife = persons.create(
        Person(None, None, "Eva Beispiel", "F", datetime.now(), datetime.now())
    )
    assert [person.name for person in persons.search("MAX")] == ["Max Beispiel"]

    records = MarriageRecordService(connection)
    existing = records.create(
        _make_record(
            year=1887,
            number=1,
            created_at=datetime.now(),
            husb_person_id=husband.id,
            wife_person_id=wife.id,
        )
    )

    assert records.has_spouse_pair(husband.id, wife.id)
    assert not records.has_spouse_pair(wife.id, husband.id)
    assert not records.has_spouse_pair(
        husband.id,
        wife.id,
        excluding_record_id=existing.id,
    )
    database.close()


def test_person_search_matches_all_terms_across_name_date_and_place(tmp_path) -> None:
    database = DatabaseConnection(tmp_path / "multi-search.edg")
    connection = database.connect(create=True)
    database.initialize_schema()
    people = PersonService(connection)
    target = people.create(
        Person(
            None,
            None,
            "Horst Müller",
            "M",
            datetime.now(),
            datetime.now(),
            birth_date_raw="06.05.1878",
            birth_place="Hamburg",
        )
    )
    people.create(
        Person(
            None,
            None,
            "Hugo Müller",
            "M",
            datetime.now(),
            datetime.now(),
            birth_date_raw="06.05.1879",
            birth_place="Berlin",
        )
    )

    assert [person.name for person in people.search("mÜll")] == [
        "Horst Müller",
        "Hugo Müller",
    ]
    assert [person.id for person in people.search("Mü ho 78", sex="M")] == [
        target.id
    ]
    assert [person.name for person in people.search("187")] == [
        "Horst Müller",
        "Hugo Müller",
    ]
    assert [person.id for person in people.search("hamb")] == [target.id]
    assert people.search("Mü Paris") == []
    database.close()


def test_person_search_keeps_husband_and_wife_context_filters(tmp_path) -> None:
    database = DatabaseConnection(tmp_path / "sex-search.edg")
    connection = database.connect(create=True)
    database.initialize_schema()
    people = PersonService(connection)
    husband = people.create(
        Person(
            None,
            None,
            "Horst Müller",
            "M",
            datetime.now(),
            datetime.now(),
            birth_date_raw="06.05.1878",
            birth_place="Hamburg",
        )
    )
    wife = people.create(
        Person(
            None,
            None,
            "Hortense Müller",
            "F",
            datetime.now(),
            datetime.now(),
            birth_date_raw="06.05.1878",
            birth_place="Hamburg",
        )
    )

    assert [person.id for person in people.search("Mü ho 78", sex="M")] == [
        husband.id
    ]
    assert [person.id for person in people.search("Mü ho 78", sex="F")] == [
        wife.id
    ]
    database.close()


def test_invalid_date_is_marked_and_cannot_finish_record(tmp_path) -> None:
    _application()
    project = _open_project(tmp_path)
    workspace = MarriageEntryWorkspace(project)
    workspace.marriage_date_edit.setText("31.02.1900")

    assert workspace.marriage_date_gedcom_edit.text() == ""
    assert not workspace.marriage_date_error_label.isHidden()
    assert workspace.marriage_date_edit.styleSheet()
    with patch.object(QMessageBox, "warning") as warning:
        assert not workspace.finish_record()
    warning.assert_called_once()
    assert workspace._record is not None
    assert (
        workspace._record.workflow_status is MarriageRecordStatus.IN_BEARBEITUNG
    )
    project.close_project()


def test_finish_requires_all_required_fields_and_marks_missing_values(
    tmp_path,
) -> None:
    _application()
    project = _open_project(tmp_path)
    workspace = MarriageEntryWorkspace(project)
    workspace.year_edit.setText("1901")
    workspace.number_edit.setText("0")
    workspace.marriage_date_edit.setText("01.02.1901")
    workspace.marriage_place_edit.setText("Sulzbach")

    with patch.object(QMessageBox, "warning"):
        assert not workspace.finish_record()

    assert workspace._record is not None
    assert workspace._record.workflow_status is MarriageRecordStatus.IN_BEARBEITUNG
    assert "background-color" in workspace.number_edit.styleSheet()
    project.close_project()


def test_new_people_use_role_sex_and_finish_can_be_reopened(tmp_path) -> None:
    _application()
    project = _open_project(tmp_path)
    workspace = MarriageEntryWorkspace(project)
    workspace.year_edit.setText("1901")
    workspace.number_edit.setText("2")
    workspace.marriage_date_edit.setText("01.02.1901")
    workspace.marriage_place_edit.setText("Sulzbach")
    workspace.findChild(QPushButton, "husband_new_button").click()
    workspace.findChild(QLineEdit, "husband_name_edit").setText("Max Beispiel")
    workspace.findChild(QPushButton, "wife_new_button").click()
    workspace.findChild(QLineEdit, "wife_name_edit").setText("Eva Beispiel")

    assert workspace._people["husband"] is not None
    assert workspace._people["husband"].sex == "M"
    assert workspace._people["wife"] is not None
    assert workspace._people["wife"].sex == "F"
    assert workspace.finish_record()
    assert workspace._record is not None
    assert workspace._record.workflow_status is MarriageRecordStatus.FERTIG
    assert workspace._record.export_status is MarriageRecordExportStatus.NICHT_EXPORTIERT
    assert workspace.next_record_button.isEnabled()

    assert workspace.reopen_record()
    assert workspace._record.workflow_status is MarriageRecordStatus.IN_BEARBEITUNG
    assert workspace.finish_button.isEnabled()
    project.close_project()


def test_existing_marriage_hint_is_informational_only(tmp_path) -> None:
    _application()
    project = _open_project(tmp_path)
    connection = project.connection
    assert connection is not None
    persons = PersonService(connection)
    husband = persons.create(
        Person(
            None,
            None,
            "Max Beispiel",
            "M",
            datetime.now(),
            datetime.now(),
            birth_date_raw="01.01.1860",
            birth_date_gedcom="1 JAN 1860",
            birth_place="Sulzbach",
        )
    )
    wife = persons.create(
        Person(None, None, "Eva Beispiel", "F", datetime.now(), datetime.now())
    )
    marriages = MarriageRecordService(connection)
    existing = marriages.create(
        _make_record(
            year=1887,
            number=1,
            created_at=datetime.now(),
            husb_person_id=husband.id,
            wife_person_id=wife.id,
        )
    )
    workspace = MarriageEntryWorkspace(project)
    workspace._load_person("husband", husband, editable=False)
    workspace._load_person("wife", wife, editable=False)
    assert workspace._person_widgets["husband"]["name"].text() == "Max Beispiel"
    assert workspace._person_widgets["husband"]["birth_date"].text() == "01.01.1860"
    assert workspace._person_widgets["husband"]["birth_place"].text() == "Sulzbach"
    assert workspace._person_widgets["husband"]["sex"].text() == "M"
    workspace._handle_record_change(refresh_list=True)

    table_names = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' "
            "AND name NOT LIKE 'sqlite_%'"
        )
    }
    assert table_names == {"project", "meta", "person", "marriage_record", "source"}
    assert not workspace._existing_marriage_hint.isHidden()
    assert workspace._existing_marriage_hint.text() == (
        "Diese Ehe ist bereits im Projekt vorhanden."
    )
    assert workspace._record is not None
    assert workspace._record.workflow_status is MarriageRecordStatus.IN_BEARBEITUNG
    assert workspace._record.id != existing.id
    assert workspace._record.marriage_date_raw is None
    project.close_project()


def test_cancel_discards_record_edits_and_restores_selection(tmp_path) -> None:
    _application()
    project = _open_project(tmp_path)
    connection = project.connection
    assert connection is not None
    original = MarriageRecordService(connection).create(
        _make_record(
            year=1887,
            number=1,
            created_at=datetime.now(),
            marriage_place="Sulzbach",
            marriage_date_raw="01.01.1887",
        )
    )
    workspace = MarriageEntryWorkspace(project)
    workspace._load_record(original)
    workspace.marriage_place_edit.setText("Anders")
    assert workspace._record is not None
    assert workspace._record.marriage_place == "Anders"

    with patch.object(
        QMessageBox,
        "question",
        return_value=QMessageBox.StandardButton.No,
    ):
        assert not workspace.cancel_entry()
    assert workspace.marriage_place_edit.text() == "Anders"

    with patch.object(
        QMessageBox,
        "question",
        return_value=QMessageBox.StandardButton.Yes,
    ) as question:
        assert workspace.cancel_entry()
    question.assert_called_once()
    restored = MarriageRecordService(connection).get_by_id(original.id)
    assert restored is not None
    assert restored.marriage_place == "Sulzbach"
    assert workspace._record == restored
    assert workspace._selected_record_id() == original.id
    project.close_project()


def test_cancel_removes_new_draft_and_person(tmp_path) -> None:
    _application()
    project = _open_project(tmp_path)
    connection = project.connection
    assert connection is not None
    original = MarriageRecordService(connection).create(
        _make_record(year=1887, number=1, created_at=datetime.now())
    )
    workspace = MarriageEntryWorkspace(project)
    workspace._load_record(original)
    workspace.start_new_record(previous_selection_id=original.id)
    workspace.findChild(QPushButton, "husband_new_button").click()
    new_person = workspace._people["husband"]
    assert new_person is not None and new_person.id is not None
    new_record_id = workspace._record.id if workspace._record is not None else None
    assert new_record_id is not None

    with patch.object(
        QMessageBox,
        "question",
        return_value=QMessageBox.StandardButton.Yes,
    ):
        assert workspace.cancel_entry()

    assert MarriageRecordService(connection).get_by_id(new_record_id) is None
    assert PersonService(connection).get_by_id(new_person.id) is None
    assert workspace._record is not None
    assert workspace._record.id == original.id
    project.close_project()


def test_person_search_dialog_filters_by_required_sex(tmp_path) -> None:
    _application()
    project = _open_project(tmp_path)
    connection = project.connection
    assert connection is not None
    people = PersonService(connection)
    for name, sex in (("Max Mann", "M"), ("Eva Frau", "F"), ("Unbekannt", None)):
        people.create(Person(None, None, name, sex, datetime.now(), datetime.now()))

    husband_dialog = PersonSearchDialog(people, required_sex="M")
    wife_dialog = PersonSearchDialog(people, required_sex="F")
    husband_list = husband_dialog.findChild(QListWidget)
    wife_list = wife_dialog.findChild(QListWidget)
    assert husband_list is not None and wife_list is not None
    assert [husband_list.item(i).text() for i in range(husband_list.count())] == [
        "Max Mann — M"
    ]
    assert [wife_list.item(i).text() for i in range(wife_list.count())] == [
        "Eva Frau — F"
    ]
    project.close_project()


def test_family_list_filters_marriage_date_year_and_sorts_by_date_then_number(
    tmp_path,
) -> None:
    application = _application()
    project = _open_project(tmp_path)
    records = MarriageRecordService(project.connection)
    now = datetime.now()
    same_date_higher_number = records.create(
        _make_record(
            year=1887,
            number=3,
            created_at=now - timedelta(days=2),
            marriage_date_raw="01.01.1887",
        )
    )
    other_year = records.create(
        _make_record(
            year=1888,
            number=2,
            created_at=now - timedelta(days=1),
            marriage_date_raw="01.01.1888",
        )
    )
    same_date_lower_number = records.create(
        _make_record(
            year=1887,
            number=1,
            created_at=now,
            marriage_date_raw="01.01.1887",
        )
    )

    workspace = MarriageEntryWorkspace(project)
    application.processEvents()
    assert workspace.year_edit.text() == "1887"
    visible_ids = [
        workspace.records_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        for row in range(workspace.records_table.rowCount())
    ]
    assert visible_ids == [same_date_lower_number.id, same_date_higher_number.id]

    workspace.all_years_checkbox.setChecked(True)
    visible_ids = [
        workspace.records_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        for row in range(workspace.records_table.rowCount())
    ]
    assert visible_ids == [
        same_date_lower_number.id,
        same_date_higher_number.id,
        other_year.id,
    ]
    project.close_project()


def test_family_list_filters_by_marriage_date_not_registration_year(
    tmp_path,
) -> None:
    _application()
    project = _open_project(tmp_path)
    connection = project.connection
    assert connection is not None
    records = MarriageRecordService(connection)
    now = datetime.now()
    marriage_in_context = records.create(
        _make_record(
            year=1886,
            number=4,
            created_at=now - timedelta(days=2),
            marriage_date_raw="12.05.1887",
        )
    )
    gedcom_date_in_context = records.create(
        _make_record(
            year=1887,
            number=8,
            created_at=now - timedelta(days=1),
            marriage_date_gedcom="1 JAN 1887",
        )
    )
    marriage_out_of_context = records.create(
        _make_record(
            year=1887,
            number=9,
            created_at=now,
            marriage_date_raw="01.01.1888",
        )
    )
    workspace = MarriageEntryWorkspace(project)

    assert workspace.year_edit.text() == "1887"
    assert [
        workspace.records_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        for row in range(workspace.records_table.rowCount())
    ] == [marriage_in_context.id, gedcom_date_in_context.id]
    workspace.all_years_checkbox.setChecked(True)
    assert workspace.records_table.rowCount() == 3
    assert marriage_out_of_context.id in [
        workspace.records_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        for row in range(workspace.records_table.rowCount())
    ]
    project.close_project()


@pytest.mark.parametrize(
    ("column", "ascending_ids"),
    [
        (0, (3, 2, 1)),
        (1, (3, 1, 2)),
        (2, (2, 3, 1)),
        (3, (1, 3, 2)),
        (4, (2, 1, 3)),
        (5, (2, 3, 1)),
        (6, (2, 3, 1)),
    ],
)
def test_family_table_headers_sort_each_column_and_toggle_order(
    tmp_path,
    column: int,
    ascending_ids: tuple[int, ...],
) -> None:
    _application()
    project = _open_project(tmp_path)
    connection = project.connection
    assert connection is not None
    persons = PersonService(connection)
    zed = persons.create(
        Person(None, None, "Zed", "M", datetime.now(), datetime.now())
    )
    anna = persons.create(
        Person(None, None, "Anna", "M", datetime.now(), datetime.now())
    )
    berta = persons.create(
        Person(None, None, "Berta", "F", datetime.now(), datetime.now())
    )
    yvonne = persons.create(
        Person(None, None, "Yvonne", "F", datetime.now(), datetime.now())
    )
    marriages = MarriageRecordService(connection)
    now = datetime.now()
    marriages.create(
        _make_record(
            year=1888,
            number=2,
            created_at=now - timedelta(days=2),
            husb_person_id=zed.id,
            wife_person_id=berta.id,
            marriage_date_raw="02.01.1887",
        )
    )
    marriages.create(
        replace(
            _make_record(
                year=1887,
                number=10,
                created_at=now - timedelta(days=1),
                husb_person_id=anna.id,
                wife_person_id=yvonne.id,
                marriage_date_raw="01.01.1887",
            ),
            workflow_status=MarriageRecordStatus.FERTIG,
            export_status=MarriageRecordExportStatus.EXPORTIERT,
        )
    )
    marriages.create(
        replace(
            _make_record(
                year=1887,
                number=1,
                created_at=now,
                husb_person_id=anna.id,
                wife_person_id=berta.id,
                marriage_date_raw="03.01.1887",
            ),
            workflow_status=MarriageRecordStatus.FERTIG,
            export_status=MarriageRecordExportStatus.KONFLIKT,
        )
    )
    workspace = MarriageEntryWorkspace(project)
    header = workspace.records_table.horizontalHeader()
    header.sectionClicked.emit(column)
    ascending = tuple(
        workspace.records_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        for row in range(workspace.records_table.rowCount())
    )
    assert ascending == ascending_ids
    assert header.sortIndicatorSection() == column
    assert header.sortIndicatorOrder() is Qt.SortOrder.AscendingOrder

    header.sectionClicked.emit(column)
    descending = tuple(
        workspace.records_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        for row in range(workspace.records_table.rowCount())
    )
    assert descending == tuple(reversed(ascending_ids))
    assert header.sortIndicatorOrder() is Qt.SortOrder.DescendingOrder

    header.sectionClicked.emit(column)
    ascending_again = tuple(
        workspace.records_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        for row in range(workspace.records_table.rowCount())
    )
    assert ascending_again == ascending_ids

    other_column = (column + 1) % 7
    header.sectionClicked.emit(other_column)
    assert header.sortIndicatorOrder() is Qt.SortOrder.AscendingOrder
    header.sectionClicked.emit(column)
    assert header.sortIndicatorOrder() is Qt.SortOrder.AscendingOrder
    project.close_project()


def test_double_click_loads_complete_record_and_starts_new_for_incomplete_family(
    tmp_path,
) -> None:
    _application()
    project = _open_project(tmp_path)
    connection = project.connection
    assert connection is not None
    people = PersonService(connection)
    husband = people.create(
        Person(None, None, "Max", "M", datetime.now(), datetime.now())
    )
    wife = people.create(
        Person(None, None, "Eva", "F", datetime.now(), datetime.now())
    )
    marriages = MarriageRecordService(connection)
    incomplete = marriages.create(
        _make_record(
            year=None,
            number=None,
            created_at=datetime.now() - timedelta(days=1),
            husb_person_id=husband.id,
            wife_person_id=wife.id,
        )
    )
    complete = marriages.create(
        _make_record(
            year=1887,
            number=2,
            created_at=datetime.now(),
            marriage_date_raw="01.01.1887",
        )
    )
    workspace = MarriageEntryWorkspace(project)

    complete_row = next(
        row
        for row in range(workspace.records_table.rowCount())
        if workspace.records_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        == complete.id
    )
    workspace._open_record_at_row(complete_row, 0)
    assert workspace._record is not None and workspace._record.id == complete.id

    workspace.all_years_checkbox.setChecked(True)
    incomplete_row = next(
        row
        for row in range(workspace.records_table.rowCount())
        if workspace.records_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        == incomplete.id
    )
    workspace._open_record_at_row(incomplete_row, 0)
    assert workspace._record is None
    assert workspace._people["husband"] == husband
    assert workspace._people["wife"] == wife
    assert workspace.workflow_status_label.text() == "In Bearbeitung"
    project.close_project()


def test_exported_record_is_read_only(tmp_path) -> None:
    _application()
    project = _open_project(tmp_path)
    connection = project.connection
    assert connection is not None
    exported = MarriageRecordService(connection).create(
        replace(
            _make_record(year=1887, number=1, created_at=datetime.now()),
            workflow_status=MarriageRecordStatus.FERTIG,
            export_status=MarriageRecordExportStatus.EXPORTIERT,
        )
    )
    workspace = MarriageEntryWorkspace(project)
    workspace._load_record(exported)

    assert not workspace.year_edit.isEnabled()
    assert not workspace.finish_button.isEnabled()
    assert not workspace.reopen_button.isEnabled()
    assert workspace.exported_read_only_label.text() == (
        "Diese Urkunde wurde bereits exportiert und kann nicht mehr bearbeitet werden."
    )
    assert not workspace.exported_read_only_label.isHidden()
    assert not workspace.reopen_record()
    project.close_project()
