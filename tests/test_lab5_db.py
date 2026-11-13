"""Unit tests for Lab 5 database models and Repository (in-memory SQLite)."""

from sqlmodel import Session, select

from assistant_api.db import ChatSession, Interaction, Repository, hash_session, init_db, make_engine


def make_repo() -> tuple[Repository, any]:
    engine = make_engine("sqlite://")
    init_db(engine)
    return Repository(engine, "test-salt"), engine


def test_session_id_is_hashed():
    repo, engine = make_repo()
    repo.record_interaction("student-42", "r1", "fee", None, True, False, 3.0)
    with Session(engine) as db:
        s = db.exec(select(ChatSession)).one()
    assert s.id == hash_session("student-42", "test-salt")
    assert "student-42" not in s.id


def test_one_session_many_interactions():
    repo, engine = make_repo()
    for i in range(3):
        repo.record_interaction("session-xyz", f"r{i}", "rule", "H26-5.3", True, False, 10.0)
    with Session(engine) as db:
        sessions = db.exec(select(ChatSession)).all()
        interactions = db.exec(select(Interaction)).all()
    assert len(sessions) == 1
    assert len(interactions) == 3
    assert all(it.session_id == sessions[0].id for it in interactions)


def test_feedback_requires_existing_interaction():
    repo, _ = make_repo()
    assert repo.add_feedback("missing-req", 1, None) is None

    repo.record_interaction("session-abc", "req-001", "fee", None, True, False, 1.5)
    fb = repo.add_feedback("req-001", -1, "incorrect amount")
    assert fb is not None
    assert fb.id == 1
    assert fb.request_id == "req-001"
    assert fb.rating == -1
    assert fb.comment == "incorrect amount"
    assert fb.created_at is not None


def test_feedback_ordering_and_limit():
    repo, engine = make_repo()
    assert repo.list_feedback() == []

    repo.record_interaction("s", "r1", "fee", None, True, False, 2.0)
    repo.record_interaction("s", "r2", "greeting", None, True, False, 1.0)
    repo.record_interaction("s", "r3", "rule", None, True, False, 3.0)

    fb1 = repo.add_feedback("r1", 1, "first")
    fb2 = repo.add_feedback("r2", 0, "second")
    fb3 = repo.add_feedback("r3", -1, "third")

    all_fb = repo.list_feedback()
    assert len(all_fb) == 3
    # Newest first
    assert all_fb[0].id == fb3.id
    assert all_fb[1].id == fb2.id
    assert all_fb[2].id == fb1.id

    limited = repo.list_feedback(limit=2)
    assert len(limited) == 2
    assert limited[0].id == fb3.id
    assert limited[1].id == fb2.id


def test_intent_stats():
    repo, _ = make_repo()
    repo.record_interaction("s1", "r1", "fee", None, True, False, 10.0)
    repo.record_interaction("s1", "r2", "fee", None, True, True, 20.0)
    repo.record_interaction("s2", "r3", "greeting", None, True, False, 5.0)
    repo.record_interaction("s3", "r4", "unknown", None, False, False, 8.0)

    stats = repo.intent_stats()
    assert len(stats) == 3

    fee_stat = next(s for s in stats if s["intent"] == "fee")
    assert fee_stat["requests"] == 2
    assert fee_stat["avg_latency_ms"] == 15.0
    assert fee_stat["unresolved"] == 0

    unknown_stat = next(s for s in stats if s["intent"] == "unknown")
    assert unknown_stat["requests"] == 1
    assert unknown_stat["avg_latency_ms"] == 8.0
    assert unknown_stat["unresolved"] == 1


def test_record_interaction_fields():
    repo, engine = make_repo()
    repo.record_interaction("s-detail", "req-det", "rule", "H26-4.2", True, True, 42.5)

    with Session(engine) as db:
        it = db.exec(select(Interaction).where(Interaction.request_id == "req-det")).one()
    assert it.request_id == "req-det"
    assert it.intent == "rule"
    assert it.topic == "H26-4.2"
    assert it.resolved is True
    assert it.degraded is True
    assert it.latency_ms == 42.5
