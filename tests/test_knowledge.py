"""Unit tests for knowledge sources (offices and handbook)."""

import json

import pytest

from assistant_core.errors import DataError
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.models import Rule


def test_office_directory_load_and_find(sample_offices):
    assert len(sample_offices.names) == 4
    library = sample_offices.find("where is the library?")
    assert library is not None
    assert library.room == "B.201"
    assert library.hours == "Mon-Sat 07:00-20:00"


def test_office_directory_case_insensitive(sample_offices):
    o1 = sample_offices.find("STUDENT AFFAIRS")
    assert o1 is not None
    assert o1.room == "I.102"


def test_office_directory_not_found(sample_offices):
    assert sample_offices.find("cafeteria") is None


def test_office_directory_missing_file(tmp_path):
    with pytest.raises(DataError, match="office file not found"):
        OfficeDirectory.from_csv(tmp_path / "nonexistent.csv")


def test_office_directory_invalid_csv_headers(tmp_path):
    bad_csv = tmp_path / "bad_offices.csv"
    bad_csv.write_text("wrong,columns,here\na,b,c", encoding="utf-8")
    with pytest.raises(DataError):
        OfficeDirectory.from_csv(bad_csv)


def test_handbook_load_and_search(sample_handbook):
    assert len(sample_handbook.rules) == 5
    rule = sample_handbook.search("can I register my thesis with 118 credits")
    assert rule is not None
    assert rule.id == "H26-5.3"
    assert "120 accumulated credits" in rule.text


def test_handbook_search_no_match(sample_handbook):
    assert sample_handbook.search("completely unrelated query xyz123") is None


def test_handbook_get_by_id(sample_handbook):
    rule = sample_handbook.get_by_id("H26-4.2")
    assert rule is not None
    assert rule.title == "Retaking a course"
    assert sample_handbook.get_by_id("NONEXISTENT") is None


def test_handbook_missing_file(tmp_path):
    with pytest.raises(DataError, match="handbook file not found"):
        Handbook.from_json(tmp_path / "missing.json")


def test_handbook_malformed_json(tmp_path):
    bad_json = tmp_path / "malformed.json"
    bad_json.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(DataError):
        Handbook.from_json(bad_json)


@pytest.mark.parametrize(
    "row",
    [
        "Library\n",
        "Library,B.201\n",
        ",B.201,09-17\n",
        "Library, ,09-17\n",
        "Library,B.201,\n",
        "Library,B.201,09-17,extra\n",
    ],
)
def test_invalid_csv_rows_raise_data_error_with_location(tmp_path, row):
    path = tmp_path / "offices.csv"
    path.write_text("name,room,hours\n" + row, encoding="utf-8")
    with pytest.raises(DataError, match="Invalid office row") as caught:
        OfficeDirectory.from_csv(path)
    assert str(path) in str(caught.value)
    assert ":2" in str(caught.value)


def test_malformed_csv_quotes_raise_data_error(tmp_path):
    path = tmp_path / "offices.csv"
    path.write_text('name,room,hours\n"Library,B.201,09-17\n', encoding="utf-8")
    with pytest.raises(DataError, match="Error reading office CSV"):
        OfficeDirectory.from_csv(path)


@pytest.mark.parametrize("kind", ["office", "handbook"])
def test_invalid_utf8_is_data_error(tmp_path, kind):
    path = tmp_path / "invalid-data"
    path.write_bytes(b"\xff\xfe\xff")
    loader = OfficeDirectory.from_csv if kind == "office" else Handbook.from_json
    with pytest.raises(DataError):
        loader(path)


@pytest.mark.parametrize("field", ["id", "title", "text"])
@pytest.mark.parametrize("value", [None, 42, False, [], {}, "   "])
def test_handbook_rejects_wrong_field_types_and_blank_values(tmp_path, field, value):
    path = tmp_path / "handbook.json"
    record = {"id": "R1", "title": "Title", "text": "Rule text"}
    record[field] = value
    path.write_text(json.dumps([record]), encoding="utf-8")
    with pytest.raises(DataError, match="non-empty strings") as caught:
        Handbook.from_json(path)
    assert str(path) in str(caught.value)
    assert "record 1" in str(caught.value)


@pytest.mark.parametrize("field", ["id", "title", "text"])
def test_handbook_missing_field_is_data_error(tmp_path, field):
    path = tmp_path / "handbook.json"
    record = {"id": "R1", "title": "Title", "text": "Rule text"}
    del record[field]
    path.write_text(json.dumps([record]), encoding="utf-8")
    with pytest.raises(DataError, match="missing required fields"):
        Handbook.from_json(path)


@pytest.mark.parametrize("data", [{}, [None], ["not a record"]])
def test_handbook_rejects_wrong_container_schema(tmp_path, data):
    path = tmp_path / "handbook.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(DataError):
        Handbook.from_json(path)


def test_handbook_ties_preserve_first_rule_and_zero_overlap_returns_none():
    first = Rule(id="R1", title="First", text="alpha thesis")
    second = Rule(id="R2", title="Second", text="alpha thesis")
    handbook = Handbook([first, second])
    assert handbook.search("ALPHA thesis") is first
    assert handbook.search("zzz qqq") is None


def test_load_once_office_order_and_handbook_search_survive_file_removal(tmp_path):
    office_path = tmp_path / "offices.csv"
    office_path.write_text("name,room,hours\nLibrary,B.201,09-17\nIT Helpdesk,C.101,08-16\n", encoding="utf-8")
    handbook_path = tmp_path / "handbook.json"
    handbook_path.write_text(json.dumps([{"id": "R1", "title": "Title", "text": "alpha thesis"}]), encoding="utf-8")
    offices = OfficeDirectory.from_csv(office_path)
    handbook = Handbook.from_json(handbook_path)
    office_path.unlink()
    handbook_path.unlink()
    assert offices.find("IT HELPDESK or LIBRARY").name == "Library"
    assert handbook.search("thesis").id == "R1"
