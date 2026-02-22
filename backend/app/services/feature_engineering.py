# app/services/feature_engineering.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from collections import defaultdict

from app.models.activity import StudentActivityLog
from app.models.assignment import AssignmentSubmission
from app.models.attendance import Attendance


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

def compute_academic_mastery(db: Session, student_id: int):

    avg_score = db.query(func.avg(AssignmentSubmission.score)).filter(
        AssignmentSubmission.student_id == student_id
    ).scalar()

    avg_score = avg_score or 0

    # assuming max score 100
    return minmax_scale(avg_score, 0, 100)


# =========================================================
# 2️⃣ Engagement Score
# engagement = 0.7 * total_clicks + 0.3 * login_frequency
# =========================================================

def compute_engagement_score(db: Session, student_id: int):

    total_clicks = db.query(func.sum(StudentActivityLog.duration_seconds)).filter(
        StudentActivityLog.student_id == student_id
    ).scalar() or 0

    login_freq = db.query(func.count(StudentActivityLog.id)).filter(
        StudentActivityLog.student_id == student_id,
        StudentActivityLog.activity_type == "login"
    ).scalar() or 0

    # normalize roughly
    clicks_scaled = minmax_scale(total_clicks, 0, 10000)
    login_scaled = minmax_scale(login_freq, 0, 100)

    engagement = 0.7 * clicks_scaled + 0.3 * login_scaled

    return round(engagement, 4)


# =========================================================
# 3️⃣ Attendance Rate
# =========================================================

def compute_attendance_rate(db: Session, student_id: int, course_id: int):

    total_days = db.query(func.count(Attendance.id)).filter(
        Attendance.student_id == student_id,
        Attendance.course_id == course_id
    ).scalar() or 0

    present_days = db.query(func.count(Attendance.id)).filter(
        Attendance.student_id == student_id,
        Attendance.course_id == course_id,
        Attendance.present == True
    ).scalar() or 0

    if total_days == 0:
        return 0

    rate = present_days / total_days

    return round(rate, 4)


# =========================================================
# Helper: Weekly Aggregation
# =========================================================

def get_week_number(dt):
    return dt.isocalendar()[1]


# =========================================================
# 4️⃣ Engagement Trend
# trend = (last - first) / count
# =========================================================

def compute_engagement_trend(db: Session, student_id: int):

    logs = db.query(
        StudentActivityLog.activity_timestamp,
        StudentActivityLog.duration_seconds
    ).filter(
        StudentActivityLog.student_id == student_id
    ).all()

    if not logs:
        return 0

    weekly_data = defaultdict(float)

    for log in logs:
        week = get_week_number(log.activity_timestamp)
        weekly_data[week] += log.duration_seconds or 0

    weeks = sorted(weekly_data.keys())

    if len(weeks) < 2:
        return 0

    first = weekly_data[weeks[0]]
    last = weekly_data[weeks[-1]]
    count = len(weeks)

    trend = (last - first) / count

    # normalize to small range
    return round(minmax_scale(trend, -1000, 1000), 4)


# =========================================================
# 5️⃣ Performance Trend
# =========================================================

def compute_performance_trend(db: Session, student_id: int):

    submissions = db.query(
        AssignmentSubmission.submitted_at,
        AssignmentSubmission.score
    ).filter(
        AssignmentSubmission.student_id == student_id
    ).all()

    if not submissions:
        return 0

    weekly_scores = defaultdict(list)

    for sub in submissions:
        week = get_week_number(sub.submitted_at)
        weekly_scores[week].append(sub.score or 0)

    weekly_avg = {}

    for week, scores in weekly_scores.items():
        weekly_avg[week] = sum(scores) / len(scores)

    weeks = sorted(weekly_avg.keys())

    if len(weeks) < 2:
        return 0

    first = weekly_avg[weeks[0]]
    last = weekly_avg[weeks[-1]]
    count = len(weeks)

    trend = (last - first) / count

    return round(minmax_scale(trend, -50, 50), 4)


# =========================================================
# 6️⃣ Attendance Trend
# =========================================================

def compute_attendance_trend(db: Session, student_id: int, course_id: int):

    records = db.query(
        Attendance.date,
        Attendance.present
    ).filter(
        Attendance.student_id == student_id,
        Attendance.course_id == course_id
    ).all()

    if not records:
        return 0

    weekly_presence = defaultdict(int)

    for rec in records:
        week = get_week_number(rec.date)
        if rec.present:
            weekly_presence[week] += 1

    weeks = sorted(weekly_presence.keys())

    if len(weeks) < 2:
        return 0

    first = weekly_presence[weeks[0]]
    last = weekly_presence[weeks[-1]]
    count = len(weeks)

    trend = (last - first) / count

    return round(minmax_scale(trend, -10, 10), 4)


# =========================================================
# FINAL FEATURE VECTOR (ORDER MATTERS!)
# =========================================================

def build_feature_vector(db: Session, student_id: int, course_id: int):

    academic_mastery = compute_academic_mastery(db, student_id)
    engagement_score = compute_engagement_score(db, student_id)
    attendance_rate = compute_attendance_rate(db, student_id, course_id)

    engagement_trend = compute_engagement_trend(db, student_id)
    performance_trend = compute_performance_trend(db, student_id)
    attendance_trend = compute_attendance_trend(db, student_id, course_id)

    return [
        academic_mastery,
        engagement_score,
        attendance_rate,
        engagement_trend,
        performance_trend,
        attendance_trend
    ]