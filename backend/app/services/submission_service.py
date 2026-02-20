from sqlalchemy.orm import Session
from app.models import AssignmentSubmission
from app.services.reflection_service import analyze_reflection


def submit_assignment(db: Session, student_id: int, data):
    sentiment, depth = analyze_reflection(data.reflection_text)

    submission = AssignmentSubmission(
        assignment_id=data.assignment_id,
        student_id=student_id,
        submission_text=data.submission_text,
        reflection_text=data.reflection_text,
        sentiment_score=sentiment,
        reflection_depth=depth
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    return submission