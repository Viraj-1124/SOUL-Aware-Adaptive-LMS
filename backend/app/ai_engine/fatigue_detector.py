from app.services.feature_engineering import (
    compute_engagement_trend,
    compute_performance_trend,
    compute_attendance_trend,
    compute_academic_mastery,
    compute_emotional_volatility
)

from app.models.reflection_analysis import ReflectionAnalysis
from app.models.assignment import AssignmentSubmission
from sqlalchemy import func


def detect_moral_fatigue(db, student_id, course_id):

    signals = {}

    # 1️⃣ Engagement decline
    engagement_trend = compute_engagement_trend(db, student_id)
    signals["engagement_decline"] = engagement_trend < 0

    # 2️⃣ Performance decline
    performance_trend = compute_performance_trend(db, student_id)
    signals["performance_decline"] = performance_trend < 0

    # 3️⃣ Attendance decline
    attendance_trend = compute_attendance_trend(db, student_id, course_id)
    signals["attendance_decline"] = attendance_trend < 0

    # 4️⃣ Emotional volatility (stored reflection signals)
    volatility = compute_emotional_volatility(db, student_id)
    signals["high_emotional_volatility"] = volatility > 0.4

    # 5️⃣ Low reflection depth trend
    avg_depth = db.query(func.avg(ReflectionAnalysis.reflection_depth_score))\
        .join(AssignmentSubmission)\
        .filter(AssignmentSubmission.student_id == student_id)\
        .scalar() or 0

    signals["low_reflection_depth"] = avg_depth < 0.4

    # 6️⃣ Low cognitive complexity
    avg_complexity = db.query(func.avg(ReflectionAnalysis.cognitive_complexity))\
        .join(AssignmentSubmission)\
        .filter(AssignmentSubmission.student_id == student_id)\
        .scalar() or 0

    signals["low_cognitive_complexity"] = avg_complexity < 0.4

    # 7️⃣ Low mastery
    mastery = compute_academic_mastery(db, student_id)
    signals["low_mastery"] = mastery < 0.4

    # Compute fatigue score
    fatigue_score = sum(signals.values())

    # Classification
    if fatigue_score >= 5:
        fatigue_level = "HIGH"
    elif fatigue_score >= 3:
        fatigue_level = "MODERATE"
    else:
        fatigue_level = "LOW"

    return {
        "fatigue_score": fatigue_score,
        "fatigue_level": fatigue_level,
        "signals": signals
    }