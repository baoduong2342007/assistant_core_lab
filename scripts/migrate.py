#!/usr/bin/env python3
"""Apply SQL migrations in order with atomic transaction rollback and version tracking.

Usage:
    python scripts/migrate.py [database_path] [migrations_dir]
"""

import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


def split_statements(sql: str) -> list[str]:
    """Split a SQL script into individual statements using sqlite3.complete_statement."""
    statements: list[str] = []
    buffer = ""
    for line in sql.splitlines(keepends=True):
        buffer += line
        if sqlite3.complete_statement(buffer):
            stmt = buffer.strip()
            if stmt:
                statements.append(stmt)
            buffer = ""
    trailing = buffer.strip()
    if trailing:
        statements.append(trailing)
    return statements


def apply_migration(con: sqlite3.Connection, migration_file: Path) -> None:
    """Apply a single migration file atomically.

    Executes statements within an explicit transaction (BEGIN IMMEDIATE ... COMMIT).
    If any statement fails, the transaction is rolled back (ROLLBACK) so that
    no partial DDL/DML changes persist and schema_version remains unchanged.
    """
    sql_text = migration_file.read_text(encoding="utf-8")
    statements = split_statements(sql_text)

    prev_isolation = con.isolation_level
    con.isolation_level = None
    try:
        con.execute("BEGIN IMMEDIATE")
        for stmt in statements:
            con.execute(stmt)
        applied_at = datetime.now(timezone.utc).isoformat()
        con.execute(
            "INSERT INTO schema_version (name, applied_at) VALUES (?, ?)",
            (migration_file.name, applied_at),
        )
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    finally:
        con.isolation_level = prev_isolation


def run_migrations(db_path: str = "assistant.db", migrations_dir: Path | None = None) -> list[tuple[str, str]]:
    """Run all pending migrations in migrations_dir against db_path.

    Returns a list of (action, migration_name) tuples,
    e.g. [('apply', '001_init.sql'), ('skip', '002_add_faq.sql')].
    """
    if migrations_dir is None:
        migrations_dir = Path(__file__).resolve().parents[1] / "sql" / "migrations"

    con = sqlite3.connect(db_path)
    try:
        con.execute("CREATE TABLE IF NOT EXISTS schema_version (name TEXT PRIMARY KEY, applied_at TEXT NOT NULL)")
        done = {row[0] for row in con.execute("SELECT name FROM schema_version")}

        results: list[tuple[str, str]] = []
        for f in sorted(migrations_dir.glob("*.sql")):
            if f.name in done:
                print(f"skip  {f.name}")
                results.append(("skip", f.name))
                continue
            apply_migration(con, f)
            print(f"apply {f.name}")
            results.append(("apply", f.name))
        return results
    finally:
        con.close()


if __name__ == "__main__":
    target_db = sys.argv[1] if len(sys.argv) > 1 else "assistant.db"
    target_folder = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    run_migrations(target_db, target_folder)
