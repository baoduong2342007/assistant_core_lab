"""Tests for file-backed SQLite persistence across restarts."""

from sqlmodel import Session, select

from assistant_api.db import ChatSession, Interaction, Repository, init_db, make_engine


def test_feedback_persists_across_restart(tmp_path):
    db_file = tmp_path / "test_persistence.db"
    db_url = f"sqlite:///{db_file}"

    # --- Phase 1: First "process" writes interactions and feedback ---
    engine1 = make_engine(db_url)
    init_db(engine1)
    repo1 = Repository(engine1, "persist-salt-2026")

    repo1.record_interaction("student-1", "req-persist-1", "fee", None, True, False, 12.0)
    repo1.record_interaction("student-2", "req-persist-2", "rule", "H26-5.3", True, False, 25.0)

    fb1 = repo1.add_feedback("req-persist-1", 1, "very helpful")
    fb2 = repo1.add_feedback("req-persist-2", -1, "did not answer clearly")

    assert fb1 is not None and fb2 is not None
    assert len(repo1.list_feedback()) == 2

    # Simulate shutdown
    engine1.dispose()

    # --- Phase 2: Second "process" / restarted app opens the same file ---
    engine2 = make_engine(db_url)
    repo2 = Repository(engine2, "persist-salt-2026")

    loaded_fb = repo2.list_feedback()
    assert len(loaded_fb) == 2

    # Newest first
    assert loaded_fb[0].id == fb2.id
    assert loaded_fb[0].request_id == "req-persist-2"
    assert loaded_fb[0].rating == -1
    assert loaded_fb[0].comment == "did not answer clearly"
    assert loaded_fb[0].created_at == fb2.created_at

    assert loaded_fb[1].id == fb1.id
    assert loaded_fb[1].request_id == "req-persist-1"
    assert loaded_fb[1].rating == 1
    assert loaded_fb[1].comment == "very helpful"
    assert loaded_fb[1].created_at == fb1.created_at

    engine2.dispose()


def test_intent_stats_persists_across_restart(tmp_path):
    db_file = tmp_path / "test_stats_persistence.db"
    db_url = f"sqlite:///{db_file}"

    engine1 = make_engine(db_url)
    init_db(engine1)
    repo1 = Repository(engine1, "stats-salt")

    repo1.record_interaction("s1", "r1", "fee", None, True, False, 10.0)
    repo1.record_interaction("s2", "r2", "fee", None, False, False, 20.0)
    repo1.record_interaction("s3", "r3", "greeting", None, True, False, 5.0)

    stats1 = repo1.intent_stats()
    engine1.dispose()

    engine2 = make_engine(db_url)
    repo2 = Repository(engine2, "stats-salt")
    stats2 = repo2.intent_stats()

    assert stats1 == stats2
    fee_stat = next(s for s in stats2 if s["intent"] == "fee")
    assert fee_stat["requests"] == 2
    assert fee_stat["unresolved"] == 1
    assert fee_stat["avg_latency_ms"] == 15.0

    engine2.dispose()


def test_chat_session_reuse_across_restart(tmp_path):
    db_file = tmp_path / "test_session_reuse.db"
    db_url = f"sqlite:///{db_file}"

    # First run
    engine1 = make_engine(db_url)
    init_db(engine1)
    repo1 = Repository(engine1, "shared-salt")
    repo1.record_interaction("same-user-session", "req-A", "greeting", None, True, False, 3.0)
    engine1.dispose()

    # Second run after restart
    engine2 = make_engine(db_url)
    repo2 = Repository(engine2, "shared-salt")
    repo2.record_interaction("same-user-session", "req-B", "fee", None, True, False, 7.0)

    with Session(engine2) as db:
        sessions = db.exec(select(ChatSession)).all()
        interactions = db.exec(select(Interaction)).all()

    # Still exactly one session hashed, with 2 interactions
    assert len(sessions) == 1
    assert len(interactions) == 2
    assert all(it.session_id == sessions[0].id for it in interactions)

    engine2.dispose()
