from sqlalchemy.orm import Session
from app.services.attendance_service import calculate_attendance_rate
from app.services.academic_service import calculate_academic_mastery
from app.models.assignment import AssignmentSubmission
from app.models.learning_health_snapshot import LearningHealthSnapshot
from app.services.risk_engine import classify_risk
from sqlalchemy import func


def calculate_avg_sentiment(db: Session, student_id: int):
    avg = db.query(func.avg(AssignmentSubmission.sentiment_score)).filter(
        AssignmentSubmission.student_id == student_id
    ).scalar()

    return round(avg or 0, 2)


def calculate_avg_reflection_depth(db: Session, student_id: int):
    avg = db.query(func.avg(AssignmentSubmission.reflection_depth)).filter(
        AssignmentSubmission.student_id == student_id
    ).scalar()

    return round(avg or 0, 2)


def normalize_sentiment(sentiment: float):
    # convert -1 to +1 range into 0 to 100
    return round((sentiment + 1) * 50, 2)


def compute_learning_health(db: Session, student_id: int, course_id: int):

    attendance_rate = calculate_attendance_rate(db, student_id, course_id)
    academic_mastery = calculate_academic_mastery(db, student_id)
    engagement_score = 70  # placeholder (use activity log later)

    avg_sentiment = calculate_avg_sentiment(db, student_id)
    normalized_sentiment = normalize_sentiment(avg_sentiment)

    reflection_depth = calculate_avg_reflection_depth(db, student_id)

    # 🎯 Weighted Score
    health_index = round(
        (0.25 * attendance_rate) +
        (0.25 * academic_mastery) +
        (0.2 * engagement_score) +
        (0.15 * normalized_sentiment) +
        (0.15 * reflection_depth),
        2
    )

    risk_level = classify_risk(health_index)

    snapshot = LearningHealthSnapshot(
        student_id=student_id,
        attendance_rate=attendance_rate,
        academic_mastery=academic_mastery,
        engagement_score=engagement_score,
        sentiment_score=normalized_sentiment,
        reflection_depth=reflection_depth,
        health_index=health_index,
        risk_level=risk_level
    )

    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    return snapshot