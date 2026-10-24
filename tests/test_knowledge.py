"""Unit tests for knowledge sources (offices and handbook)."""

import pytest

from assistant_core.errors import DataError
from assistant_core.knowledge import Handbook, OfficeDirectory


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
