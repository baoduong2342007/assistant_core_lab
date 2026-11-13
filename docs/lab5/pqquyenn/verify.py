"""Reproduce personal Lab05 evidence using a local copy of the pinned public lab05."""

import argparse
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from contextlib import closing
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def run(args, cwd, env, log):
    result = subprocess.run(
        [sys.executable, *map(str, args)], cwd=cwd, env=env, text=True, encoding="utf-8", capture_output=True
    )
    output = result.stdout + result.stderr
    clean_output = "\n".join(line.rstrip() for line in output.splitlines()) + "\n"
    (HERE / log).write_text(clean_output, encoding="utf-8")
    print(output, end="")
    result.check_returncode()
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lab05", type=Path, help="lab05 directory at public_materials commit d795a1a")
    parser.add_argument("--db-source", type=Path, help="Optional team db.py for compatibility verification")
    args = parser.parse_args()
    source = args.lab05.resolve()
    db_source = args.db_source or source / "starter/src/assistant_api/db.py"
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    with tempfile.TemporaryDirectory(prefix="quyen-lab05-") as temporary:
        work = Path(temporary)
        school = work / "practice"
        school.mkdir()
        for name in ("check.py", "expected.json", "school.sql", "make_school_db.py", "test_school_repo.py"):
            shutil.copy2(source / "practice" / name, school / name)
        shutil.copy2(ROOT / "practice/my_answers.sql", school / "my_answers.sql")
        shutil.copy2(HERE / "school_repo.py", school / "school_repo.py")
        run([school / "make_school_db.py"], school, env, "school-db.txt")
        score = run([school / "check.py"], school, env, "sql-check.txt")
        if "Score: 15/15" not in score:
            raise RuntimeError("The public checker must report 15/15")
        run(["-m", "pytest", "-q", school / "test_school_repo.py"], school, env, "practice-tests.txt")

        package = work / "assistant_api"
        package.mkdir()
        (package / "__init__.py").touch()
        shutil.copy2(db_source, package / "db.py")
        for name in ("feedback_repository.py", "test_feedback_repository.py"):
            shutil.copy2(HERE / name, work / name)
        env["PYTHONPATH"] = str(work)
        run(["-m", "pytest", "-q", work / "test_feedback_repository.py"], work, env, "r1-r2-tests.txt")

        shutil.copytree(source / "starter/sql/migrations", work / "sql/migrations")
        (work / "scripts").mkdir()
        shutil.copy2(source / "starter/scripts/migrate.py", work / "scripts/migrate.py")
        database = work / "analysis.db"
        run([work / "scripts/migrate.py", database], work, env, "migrate-first.txt")
        run([work / "scripts/migrate.py", database], work, env, "migrate-second.txt")
        # Complete the starter's R1/R2 through the personal subclass, then run
        # the unchanged public seed algorithm (random.seed(7), 300 interactions).
        seed_runner = work / "run_seed.py"
        seed_runner.write_text(
            "import runpy, sys\n"
            "from assistant_api import db\n"
            "from feedback_repository import FeedbackRepository\n"
            "db.Repository = FeedbackRepository\n"
            "sys.argv = sys.argv[1:]\n"
            "runpy.run_path(sys.argv[0], run_name='__main__')\n",
            encoding="utf-8",
        )
        run([seed_runner, source / "starter/scripts/seed.py", database, "300"], work, env, "seed.txt")
        with closing(sqlite3.connect(database)) as con:
            counts = {
                table: con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in ("chat_session", "interaction", "feedback")
            }
            if counts["interaction"] != 300:
                raise RuntimeError("Seed must create exactly 300 interactions")
            parts = re.split(
                r"^--\s+(Q\d+|H2)\b.*$", (ROOT / "sql/my_queries.sql").read_text(encoding="utf-8"), flags=re.M
            )
            results = {}
            for index in range(1, len(parts), 2):
                cursor = con.execute(parts[index + 1])
                results[parts[index]] = {"columns": [item[0] for item in cursor.description], "rows": cursor.fetchall()}
        evidence = {"counts": counts, "queries": results}
        (HERE / "query-results.json").write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(evidence, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
