import sqlite3
from pathlib import Path

import pytest

from scripts.migrate import apply_migration, run_migrations, split_statements


def test_split_statements():
    sql = """
    -- Comment line
    CREATE TABLE t1 (
        id INT PRIMARY KEY,
        val TEXT
    );

    /* Multiline
       comment */
    INSERT INTO t1 (id, val) VALUES (1, 'hello; world');
    """
    statements = split_statements(sql)
    assert len(statements) == 2
    assert "CREATE TABLE t1" in statements[0]
    assert "INSERT INTO t1" in statements[1]
    assert "'hello; world'" in statements[1]


def test_run_migrations_success_and_idempotent(tmp_path: Path):
    db_file = tmp_path / "test_migration.db"

    # First run: should apply all migrations
    results1 = run_migrations(str(db_file))
    assert len(results1) == 2
    assert results1[0] == ("apply", "001_init.sql")
    assert results1[1] == ("apply", "002_add_faq.sql")

    # Verify tables exist
    con = sqlite3.connect(str(db_file))
    tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    con.close()
    assert {"schema_version", "chat_session", "interaction", "feedback", "faq"}.issubset(tables)

    # Second run: should skip all migrations
    results2 = run_migrations(str(db_file))
    assert len(results2) == 2
    assert results2[0] == ("skip", "001_init.sql")
    assert results2[1] == ("skip", "002_add_faq.sql")


def test_migration_atomic_rollback_on_failure(tmp_path: Path):
    db_file = tmp_path / "test_atomic.db"
    mig_dir = tmp_path / "migrations"
    mig_dir.mkdir()

    # Create a broken migration file: table creation succeeds, then a syntax error occurs
    bad_migration = mig_dir / "001_broken.sql"
    bad_migration.write_text(
        """
        CREATE TABLE should_be_rolled_back (id INT PRIMARY KEY);
        INSERT INTO should_be_rolled_back VALUES (100);
        THIS IS INVALID SQL STATEMENT SYNTAX;
        """,
        encoding="utf-8",
    )

    con = sqlite3.connect(str(db_file))
    con.execute("CREATE TABLE IF NOT EXISTS schema_version (name TEXT PRIMARY KEY, applied_at TEXT NOT NULL)")

    with pytest.raises(sqlite3.OperationalError):
        apply_migration(con, bad_migration)

    # Verify that should_be_rolled_back does NOT exist because transaction rolled back atomically
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {r[0] for r in cur.fetchall()}
    assert "should_be_rolled_back" not in tables

    # Verify that schema_version does NOT contain 001_broken.sql
    cur.execute("SELECT COUNT(*) FROM schema_version WHERE name = '001_broken.sql'")
    assert cur.fetchone()[0] == 0

    con.close()
