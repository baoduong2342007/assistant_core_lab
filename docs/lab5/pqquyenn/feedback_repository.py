"""Personal R1-R2 exercise; reuse the public starter's models and engine."""

from sqlmodel import Session, select

from assistant_api.db import Feedback, Interaction, Repository


class FeedbackRepository(Repository):
    def add_feedback(self, request_id: str, rating: int, comment: str | None) -> Feedback | None:
        with Session(self.engine) as db:
            if db.exec(select(Interaction.id).where(Interaction.request_id == request_id)).first() is None:
                return None
            feedback = Feedback(request_id=request_id, rating=rating, comment=comment)
            db.add(feedback)
            db.commit()
            db.refresh(feedback)
            return feedback

    def list_feedback(self, limit: int = 100) -> list[Feedback]:
        with Session(self.engine) as db:
            query = select(Feedback).order_by(Feedback.created_at.desc(), Feedback.id.desc()).limit(limit)
            return list(db.exec(query).all())
