"""Personal R1 and R2 implementation using the Lab05 starter models."""

from sqlmodel import Session, select

from assistant_api.db import Feedback, Interaction
from assistant_api.db import Repository as StarterRepository


class FeedbackRepository(StarterRepository):
    def add_feedback(self, request_id: str, rating: int, comment: str | None) -> Feedback | None:
        with Session(self.engine) as db:
            request = select(Interaction.id).where(Interaction.request_id == request_id)
            if db.exec(request).first() is None:
                return None

            feedback = Feedback(request_id=request_id, rating=rating, comment=comment)
            db.add(feedback)
            db.commit()
            db.refresh(feedback)
            return feedback

    def list_feedback(self, limit: int = 100) -> list[Feedback]:
        statement = select(Feedback).order_by(Feedback.created_at.desc(), Feedback.id.desc()).limit(limit)
        with Session(self.engine) as db:
            return list(db.exec(statement).all())
