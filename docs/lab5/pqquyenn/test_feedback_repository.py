from datetime import datetime, timezone

import pytest
from feedback_repository import FeedbackRepository
from sqlmodel import Session

from assistant_api.db import Feedback, init_db, make_engine


@pytest.fixture
def repository():
    engine = make_engine("sqlite://")
    init_db(engine)
    try:
        yield FeedbackRepository(engine, "personal-test-salt")
    finally:
        engine.dispose()


def test_unknown_request_writes_nothing(repository):
    assert repository.add_feedback("missing", -1, None) is None
    assert repository.list_feedback() == []


def test_feedback_commits_and_refreshes(repository):
    repository.record_interaction("synthetic-session", "req-1", "rule", "H26-5.3", True, False, 10)
    feedback = repository.add_feedback("req-1", -1, "Synthetic comment")
    assert feedback.id is not None and feedback.created_at is not None
    with Session(repository.engine) as db:
        saved = db.get(Feedback, feedback.id)
        assert (saved.request_id, saved.rating, saved.comment) == ("req-1", -1, "Synthetic comment")


def test_time_order_ties_and_limit(repository):
    repository.record_interaction("synthetic-session", "req-1", "greeting", None, True, False, 2)
    with Session(repository.engine) as db:
        db.add_all(
            [
                Feedback(id=1, request_id="req-1", rating=1, created_at=datetime(2026, 1, 2, tzinfo=timezone.utc)),
                Feedback(id=2, request_id="req-1", rating=0, created_at=datetime(2026, 1, 1, tzinfo=timezone.utc)),
                Feedback(id=3, request_id="req-1", rating=-1, created_at=datetime(2026, 1, 2, tzinfo=timezone.utc)),
            ]
        )
        db.commit()
    assert [item.id for item in repository.list_feedback()] == [3, 1, 2]
    assert [item.id for item in repository.list_feedback(limit=2)] == [3, 1]
    assert repository.list_feedback(limit=0) == []


def test_feedback_survives_engine_restart(tmp_path):
    url = f"sqlite:///{tmp_path / 'restart.db'}"
    first = make_engine(url)
    try:
        init_db(first)
        repository = FeedbackRepository(first, "personal-test-salt")
        repository.record_interaction("synthetic-session", "req-1", "greeting", None, True, False, 2)
        repository.add_feedback("req-1", 1, None)
    finally:
        first.dispose()
    second = make_engine(url)
    try:
        saved = FeedbackRepository(second, "personal-test-salt").list_feedback()
        assert [(item.request_id, item.rating) for item in saved] == [("req-1", 1)]
    finally:
        second.dispose()
