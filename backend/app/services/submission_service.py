from sqlalchemy.orm import Session
from app.models import AssignmentSubmission
from app.services.reflection_service import analyze_reflection
from fastapi import HTTPException
from datetime import datetime
from app.models import Assignment


def submit_assignment(db: Session, student_id: int, data):

    assignment = db.query(Assignment).filter(
        Assignment.id == data.assignment_id
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if datetime.utcnow() > assignment.due_date:
        raise HTTPException(
            status_code=400,
            detail="Submission deadline has passed"
        )

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