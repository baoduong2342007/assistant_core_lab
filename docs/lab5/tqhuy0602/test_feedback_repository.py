from datetime import datetime, timezone

import pytest
from feedback_repository import FeedbackRepository
from sqlmodel import Session

from assistant_api.db import Feedback, init_db, make_engine


@pytest.fixture
def repository():
    engine = make_engine("sqlite://")
    try:
        init_db(engine)
        yield FeedbackRepository(engine, "r1-r2-test-salt")
    finally:
        engine.dispose()


def test_r1_rejects_unknown_request_id(repository):
    assert repository.add_feedback("unknown", 1, None) is None
    assert repository.list_feedback() == []


def test_r1_commits_and_returns_feedback(repository):
    repository.record_interaction("test-session", "request", "greeting", None, True, False, 2.0)
    feedback = repository.add_feedback("request", -1, "Synthetic feedback")
    assert feedback is not None and feedback.id is not None and feedback.created_at is not None
    with Session(repository.engine) as session:
        saved = session.get(Feedback, feedback.id)
        assert (saved.request_id, saved.rating, saved.comment) == ("request", -1, "Synthetic feedback")


def test_r2_orders_by_time_then_id_and_limits_results(repository):
    repository.record_interaction("test-session", "request", "greeting", None, True, False, 2.0)
    newer = datetime(2026, 1, 2, tzinfo=timezone.utc)
    older = datetime(2026, 1, 1, tzinfo=timezone.utc)
    with Session(repository.engine) as session:
        session.add_all(
            [
                Feedback(id=1, request_id="request", rating=1, created_at=newer),
                Feedback(id=2, request_id="request", rating=0, created_at=older),
                Feedback(id=3, request_id="request", rating=-1, created_at=newer),
            ]
        )
        session.commit()

    assert [feedback.id for feedback in repository.list_feedback()] == [3, 1, 2]
    assert [feedback.id for feedback in repository.list_feedback(limit=2)] == [3, 1]
    assert repository.list_feedback(limit=0) == []
