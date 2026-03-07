# app/services/feature_engineering.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from collections import defaultdict

from app.models.activity import StudentActivityLog
from app.models.assignment import AssignmentSubmission
from app.models.attendance import Attendance
from app.models.quiz import QuizAttempt
from app.models.reflection_analysis import ReflectionAnalysis


# =========================================================
# Utility: Safe Min-Max Scaling (bounded version)
# =========================================================

def minmax_scale(value: float, min_val: float, max_val: float):
    if max_val - min_val == 0:
        return 0
    scaled = (value - min_val) / (max_val - min_val)
    return max(0, min(1, scaled))  # clamp between 0 and 1


# =========================================================
# 1️⃣ Academic Mastery
# =========================================================

def compute_academic_mastery(db, student_id):

    avg_assignment = db.query(func.avg(AssignmentSubmission.score)).filter(
        AssignmentSubmission.student_id == student_id
    ).scalar() or 0

    avg_quiz = db.query(func.avg(QuizAttempt.score)).filter(
        QuizAttempt.student_id == student_id
    ).scalar() or 0

    mastery = (avg_assignment + avg_quiz) / 2

    return mastery / 100


# =========================================================
# 2️⃣ Engagement Score
# engagement = 0.7 * total_clicks + 0.3 * login_frequency
# =========================================================

def compute_engagement_score(db, student_id):

    clicks = db.query(func.count(StudentActivityLog.id)).filter(
        StudentActivityLog.student_id == student_id
    ).scalar() or 0

    login_freq = db.query(func.count(StudentActivityLog.id)).filter(
        StudentActivityLog.student_id == student_id,
        StudentActivityLog.activity_type == "login"
    ).scalar() or 0

    engagement = (0.7 * clicks) + (0.3 * login_freq)

    return minmax_scale(engagement, 0, 200)


def compute_assignment_score(db, student_id):

    avg_score = db.query(func.avg(AssignmentSubmission.score)).filter(
        AssignmentSubmission.student_id == student_id
    ).scalar()

    if avg_score is None:
        return 0

    return avg_score / 100


def compute_attempt_count(db, student_id):

    attempts = db.query(func.count(AssignmentSubmission.id)).filter(
        AssignmentSubmission.student_id == student_id
    ).scalar()

    return attempts or 0

# =========================================================
# 3️⃣ Attendance Rate
# =========================================================
def compute_attendance_rate(db, student_id, course_id):

    total = db.query(func.count(Attendance.id)).filter(
        Attendance.student_id == student_id,
        Attendance.course_id == course_id
    ).scalar() or 0

    present = db.query(func.count(Attendance.id)).filter(
        Attendance.student_id == student_id,
        Attendance.course_id == course_id,
        Attendance.present == True
    ).scalar() or 0

    if total == 0:
        return 0

    return present / total


# =========================================================
# Helper: Weekly Aggregation
# =========================================================

def get_week_number(dt):
    return dt.isocalendar()[1]


# =========================================================
# 4️⃣ Engagement Trend
# trend = (last - first) / count
# =========================================================

def compute_engagement_trend(db, student_id):

    logs = db.query(
        StudentActivityLog.activity_timestamp,
        StudentActivityLog.duration_seconds
    ).filter(
        StudentActivityLog.student_id == student_id
    ).all()

    weekly = defaultdict(float)

    for log in logs:
        week = log.activity_timestamp.isocalendar()[1]
        weekly[week] += log.duration_seconds or 0

    weeks = sorted(weekly.keys())

    if len(weeks) < 2:
        return 0

    first = weekly[weeks[0]]
    last = weekly[weeks[-1]]

    return (last - first) / len(weeks)

# =========================================================
# 5️⃣ Performance Trend
# =========================================================

def compute_performance_trend(db, student_id):

    submissions = db.query(
        AssignmentSubmission.submitted_at,
        AssignmentSubmission.score
    ).filter(
        AssignmentSubmission.student_id == student_id
    ).all()

    weekly = defaultdict(list)

    for sub in submissions:
        week = sub.submitted_at.isocalendar()[1]
        weekly[week].append(sub.score)

    weekly_avg = {
        week: sum(scores) / len(scores)
        for week, scores in weekly.items()
    }

    weeks = sorted(weekly_avg.keys())

    if len(weeks) < 2:
        return 0

    first = weekly_avg[weeks[0]]
    last = weekly_avg[weeks[-1]]

    return (last - first) / len(weeks)

# =========================================================
# 6️⃣ Attendance Trend
# =========================================================

def compute_attendance_trend(db, student_id, course_id):

    records = db.query(
        Attendance.date,
        Attendance.present
    ).filter(
        Attendance.student_id == student_id,
        Attendance.course_id == course_id
    ).all()

    weekly = defaultdict(int)

    for rec in records:
        week = rec.date.isocalendar()[1]
        if rec.present:
            weekly[week] += 1

    weeks = sorted(weekly.keys())

    if len(weeks) < 2:
        return 0

    first = weekly[weeks[0]]
    last = weekly[weeks[-1]]

    return (last - first) / len(weeks)

def build_feature_vector(db, student_id, course_id):

    academic_mastery = compute_academic_mastery(db, student_id)

    assignment_score = compute_assignment_score(db, student_id)

    attempt_count = compute_attempt_count(db, student_id)

    engagement_score = compute_engagement_score(db, student_id)

    attendance_rate = compute_attendance_rate(db, student_id, course_id)

    engagement_trend = compute_engagement_trend(db, student_id)

    performance_trend = compute_performance_trend(db, student_id)

    attendance_trend = compute_attendance_trend(db, student_id, course_id)

    return [
        academic_mastery,
        assignment_score,
        attempt_count,
        engagement_score,
        attendance_rate,
        engagement_trend,
        performance_trend,
        attendance_trend
    ]

def compute_emotional_volatility(db, student_id):

    reflections = db.query(ReflectionAnalysis.sentiment_polarity)\
        .join(AssignmentSubmission)\
        .filter(AssignmentSubmission.student_id == student_id)\
        .order_by(ReflectionAnalysis.created_at)\
        .all()

    sentiments = [r[0] for r in reflections]

    if len(sentiments) < 2:
        return 0

    changes = [abs(sentiments[i] - sentiments[i-1]) for i in range(1, len(sentiments))]

    return sum(changes) / len(changes)