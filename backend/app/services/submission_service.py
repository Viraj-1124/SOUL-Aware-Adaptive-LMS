from sqlalchemy.orm import Session
from app.models import AssignmentSubmission
from app.services.reflection_service import analyze_reflection
from fastapi import HTTPException
from datetime import datetime
from app.ai_engine.reflection_analyzer import analyze_reflection_advanced
from app.models.reflection_analysis import ReflectionAnalysis
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
    analysis = analyze_reflection_advanced(data.reflection_text)

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

    if analysis:
        reflection_record = ReflectionAnalysis(
            submission_id=submission.id,
            sentiment_polarity=analysis["sentiment_polarity"],
            sentiment_intensity=analysis["sentiment_intensity"],
            lexical_diversity=analysis["lexical_diversity"],
            self_reference_ratio=analysis["self_reference_ratio"],
            cognitive_complexity=analysis["cognitive_complexity"],
            reflection_depth_score=analysis["reflection_depth_score"]
        )
    db.add(reflection_record)
    db.commit()

    return submission