"""Check aggregation semantics that the public sample data does not exercise."""

import re
import sqlite3
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def queries(path):
    parts = re.split(r"^--\s+(Q\d+|H2)\b.*$", path.read_text(encoding="utf-8"), flags=re.M)
    return {parts[index]: parts[index + 1] for index in range(1, len(parts), 2)}


@pytest.fixture
def analysis():
    con = sqlite3.connect(":memory:")
    con.executescript(
        """
        CREATE TABLE interaction (
            request_id TEXT PRIMARY KEY, intent TEXT, topic TEXT,
            resolved INTEGER, degraded INTEGER, latency_ms REAL
        );
        CREATE TABLE feedback (request_id TEXT, rating INTEGER);
        INSERT INTO interaction VALUES
            ('a', 'rule', 'A', 0, 0, 10),
            ('b', 'rule', 'B', 1, 1, 30),
            ('c', 'fee', NULL, 1, 0, 2),
            ('d', 'fee', NULL, 1, 0, 4),
            ('e', 'unknown', NULL, 0, 0, 8);
        INSERT INTO feedback VALUES
            ('a', -1), ('a', -1), ('a', 1), ('a', 0),
            ('b', -1), ('b', -1), ('e', -1);
        """
    )
    try:
        yield con, queries(ROOT / "sql/my_queries.sql")
    finally:
        con.close()


def test_f1_counts_requests_without_feedback_multiplication(analysis):
    con, sql = analysis
    cursor = con.execute(sql["Q1"])
    assert [column[0] for column in cursor.description] == ["intent", "request_count"]
    assert cursor.fetchall() == [("fee", 2), ("rule", 2), ("unknown", 1)]


def test_f2_average_is_per_interaction_in_milliseconds(analysis):
    con, sql = analysis
    cursor = con.execute(sql["Q2"])
    assert [column[0] for column in cursor.description] == ["intent", "avg_latency_ms"]
    assert cursor.fetchall() == [("rule", 20.0), ("unknown", 8.0), ("fee", 3.0)]


def test_f3_counts_negative_events_excludes_null_and_breaks_ties(analysis):
    con, sql = analysis
    cursor = con.execute(sql["Q3"])
    assert [column[0] for column in cursor.description] == ["topic", "thumbs_down_count"]
    assert cursor.fetchall() == [("A", 2), ("B", 2)]


def test_h2_percent_denominator_and_degraded_are_independent(analysis):
    con, sql = analysis
    cursor = con.execute(sql["H2"])
    assert [column[0] for column in cursor.description] == [
        "intent",
        "request_count",
        "unresolved_count",
        "unresolved_rate_pct",
        "degraded_count",
        "avg_latency_ms",
    ]
    assert cursor.fetchall() == [
        ("unknown", 1, 1, 100.0, 0, 8.0),
        ("rule", 2, 1, 50.0, 1, 20.0),
        ("fee", 2, 0, 0.0, 0, 3.0),
    ]
    assert sql["H2"].strip() == (ROOT / "docs/lab5/pqquyenn/h2.sql").read_text(encoding="utf-8").strip()


def test_empty_analysis_database(analysis):
    con, sql = analysis
    con.execute("DELETE FROM feedback")
    con.execute("DELETE FROM interaction")
    assert all(con.execute(statement).fetchall() == [] for statement in sql.values())


def test_school_left_joins_and_student_identity():
    con = sqlite3.connect(":memory:")
    try:
        con.executescript(
            """
            CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT, year INTEGER, program TEXT);
            CREATE TABLE courses (code TEXT PRIMARY KEY, title TEXT, credits INTEGER);
            CREATE TABLE enrollments (student_id INTEGER, course_code TEXT, grade REAL);
            INSERT INTO students VALUES (1, 'An', 1, 'CS'), (2, 'An', 2, 'CS'), (3, 'Binh', 1, 'SE');
            INSERT INTO courses VALUES ('CSC10014', 'Thinking', 3), ('EMPTY', 'Empty', 4);
            INSERT INTO enrollments VALUES (1, 'CSC10014', 4), (2, 'CSC10014', 3);
            """
        )
        sql = queries(ROOT / "practice/my_answers.sql")
        assert set(sql) == {f"Q{number}" for number in range(1, 16)}
        assert con.execute(sql["Q12"]).fetchall() == [("Thinking", 2), ("Empty", 0)]
        assert con.execute(sql["Q13"]).fetchall() == [("An",), ("An",)]
        assert con.execute(sql["Q14"]).fetchall() == [("An", 3), ("An", 3), ("Binh", 0)]
        assert con.execute(sql["Q15"]).fetchall() == [("Binh",)]
        assert con.execute(sql["Q9"]).fetchall() == [(None,)]
    finally:
        con.close()
