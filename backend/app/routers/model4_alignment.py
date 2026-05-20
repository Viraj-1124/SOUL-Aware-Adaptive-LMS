"""
model4_alignment.py
FastAPI Router — Model 4 (Purpose & Skill Alignment)
──────────────────────────────────────────────────────
Endpoints:
    POST /alignment/analyze/{student_id}
        → Run full Model 4 pipeline for a student, save result, return output
        → Students can only analyze their own profile
        → Instructors/Admins can analyze any student

    GET  /alignment/profile/{student_id}
        → Fetch the stored goal profile for a student
        → Students can only fetch their own profile
        → Instructors/Admins can fetch any student's profile

    GET  /alignment/all
        → List all stored goal profiles (instructor/admin view)

    GET  /alignment/mastery-prefill/{student_id}
        → Derive skill mastery scores from knowledge tracing states
        → Returns pre-filled mastery values for the goal alignment form

    POST /alignment/analyze-batch
        → Bulk-analyze all students in a course (instructor/admin only)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.auth.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.model4_alignment import (
    GoalAlignmentRequest,
    GoalAlignmentResponse,
    GoalProfileOut,
    MasteryPrefillOut,
    ContextPrefillOut,
    BatchAnalyzeRequest,
)
from app.model4_alignment.model4_service import run_alignment_pipeline, get_goal_profile

router = APIRouter(prefix="/alignment", tags=["Goal Alignment (Model 4)"])


@router.post("/analyze/{student_id}", response_model=GoalAlignmentResponse)
def analyze_goal_alignment(
    student_id: int,
    request: GoalAlignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Run the full Model 4 pipeline for a student.
    Accepts goal text + skill mastery + behavior context.
    Returns alignment score, predicted domain, skill gaps, recommendation, and learning path.
    Students can only analyze their own profile; instructors/admins can analyze any student.
    """
    # Students can only submit their own goal
    if current_user.role == "STUDENT" and current_user.id != student_id:
        raise HTTPException(
            status_code=403,
            detail="Students can only analyze their own goal alignment."
        )

    # Verify target student exists
    student = db.query(User).filter(User.id == student_id, User.role == "STUDENT").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    result = run_alignment_pipeline(
        db                = db,
        student_id        = student_id,
        goal_text         = request.goal_text,
        html_mastery      = request.html_mastery,
        css_mastery       = request.css_mastery,
        js_mastery        = request.js_mastery,
        react_mastery     = request.react_mastery,
        python_mastery    = request.python_mastery,
        ml_mastery        = request.ml_mastery,
        dsa_mastery       = request.dsa_mastery,
        environment       = request.environment,
        engagement_score  = request.engagement_score,
        consistency_score = request.consistency_score,
        integrity_score   = request.integrity_score,
        anomaly_score     = request.anomaly_score,
    )
    return result


@router.get("/profile/{student_id}", response_model=GoalProfileOut)
def get_student_goal_profile(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Fetch the stored goal alignment profile for a student.
    Returns 404 if the student hasn't submitted a goal yet.
    Students can only fetch their own profile; instructors/admins can fetch any.
    """
    # Students can only view their own profile
    if current_user.role == "STUDENT" and current_user.id != student_id:
        raise HTTPException(
            status_code=403,
            detail="Students can only view their own goal profile."
        )

    profile = get_goal_profile(db, student_id)
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="No goal profile found for this student. Submit a goal first."
        )
    return profile


@router.get("/context-prefill/{student_id}", response_model=ContextPrefillOut)
def get_context_prefill(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Auto-fetch ALL Model 4 inputs for a student from the DB:
      - Skill mastery   → from Knowledge Tracing (BKT/LSTM per topic)
      - Engagement      → from StudentActivityLog (clicks + logins)
      - Consistency     → from assignment submission frequency
      - Integrity       → from ReflectionAnalysis sentiment avg
      - Anomaly         → from emotional volatility across reflections
      - Environment     → inferred from most frequent activity type
      - Goal text       → from saved StudentGoalProfile (if exists)

    Instructors/Admins can fetch any student. Students fetch their own only.
    """
    if current_user.role == "STUDENT" and current_user.id != student_id:
        raise HTTPException(status_code=403, detail="Students can only prefill their own data.")

    from app.models.knowledge_tracing import StudentKnowledgeState
    from app.models.course import Topic
    from app.models.activity import StudentActivityLog
    from app.models.assignment import AssignmentSubmission
    from app.models.reflection_analysis import ReflectionAnalysis
    from app.models.model4_goal_profile import StudentGoalProfile
    from app.model4_alignment.model4_service import derive_mastery_from_knowledge_states
    from app.services.feature_engineering import (
        compute_engagement_score,
        compute_emotional_volatility,
        minmax_scale,
    )
    from sqlalchemy import func

    # ── 1. Skill mastery from knowledge tracing ───────────────────────────────
    states = db.query(StudentKnowledgeState).filter(
        StudentKnowledgeState.student_id == student_id
    ).all()
    enriched = []
    for state in states:
        topic = db.query(Topic).filter(Topic.id == state.topic_id).first()
        enriched.append({
            "topic_title":      topic.title if topic else "",
            "bkt_probability":  state.bkt_probability or 0.0,
            "lstm_probability": state.lstm_probability or 0.0,
        })
    mastery = derive_mastery_from_knowledge_states(enriched)
    has_mastery_data = mastery["has_data"]

    # ── 2. Engagement score from activity logs ────────────────────────────────
    engagement_score = compute_engagement_score(db, student_id)
    total_logs = db.query(func.count(StudentActivityLog.id)).filter(
        StudentActivityLog.student_id == student_id
    ).scalar() or 0
    has_activity_data = total_logs > 0

    # ── 3. Consistency score from submission regularity ───────────────────────
    # Count weeks with at least one submission vs total weeks active
    submissions = db.query(AssignmentSubmission.submitted_at).filter(
        AssignmentSubmission.student_id == student_id
    ).all()
    if submissions:
        weeks_with_submission = len(set(s.submitted_at.isocalendar()[1] for s in submissions))
        all_logs = db.query(StudentActivityLog.activity_timestamp).filter(
            StudentActivityLog.student_id == student_id
        ).all()
        total_weeks = len(set(l.activity_timestamp.isocalendar()[1] for l in all_logs if l.activity_timestamp)) or 1
        consistency_score = round(min(weeks_with_submission / total_weeks, 1.0), 4)
    else:
        consistency_score = 0.5  # neutral default

    # ── 4. Integrity score from avg reflection sentiment ─────────────────────
    avg_sentiment = db.query(func.avg(ReflectionAnalysis.sentiment_polarity))\
        .join(AssignmentSubmission)\
        .filter(AssignmentSubmission.student_id == student_id)\
        .scalar()
    if avg_sentiment is not None:
        # Convert -1..+1 sentiment to 0..1 integrity proxy
        integrity_score = round(float((avg_sentiment + 1) / 2), 4)
    else:
        integrity_score = 0.8  # neutral default

    # ── 5. Anomaly score from emotional volatility ────────────────────────────
    volatility = compute_emotional_volatility(db, student_id)
    # Volatility is 0..1+ range, clip to 0..1
    anomaly_score = round(min(float(volatility), 1.0), 4)

    # ── 6. Environment from most frequent activity type ───────────────────────
    activity_counts = db.query(
        StudentActivityLog.activity_type,
        func.count(StudentActivityLog.id).label("cnt")
    ).filter(
        StudentActivityLog.student_id == student_id
    ).group_by(StudentActivityLog.activity_type).all()

    environment = "online"  # default
    if activity_counts:
        most_common = max(activity_counts, key=lambda x: x.cnt).activity_type or ""
        if "lab" in most_common.lower():
            environment = "lab"
        elif "project" in most_common.lower():
            environment = "project"
        elif "self" in most_common.lower():
            environment = "self-study"
        else:
            environment = "online"

    # ── 7. Goal text from saved profile ──────────────────────────────────────
    saved_profile = db.query(StudentGoalProfile).filter(
        StudentGoalProfile.student_id == student_id
    ).first()
    goal_text = saved_profile.goal_text if saved_profile else ""
    has_saved_goal = saved_profile is not None

    return ContextPrefillOut(
        html_mastery     = mastery["html_mastery"],
        css_mastery      = mastery["css_mastery"],
        js_mastery       = mastery["js_mastery"],
        react_mastery    = mastery["react_mastery"],
        python_mastery   = mastery["python_mastery"],
        ml_mastery       = mastery["ml_mastery"],
        dsa_mastery      = mastery["dsa_mastery"],
        environment      = environment,
        engagement_score = engagement_score,
        consistency_score= consistency_score,
        integrity_score  = integrity_score,
        anomaly_score    = anomaly_score,
        goal_text        = goal_text,
        has_activity_data= has_activity_data,
        has_mastery_data = has_mastery_data,
        has_saved_goal   = has_saved_goal,
    )


@router.get("/mastery-prefill/{student_id}", response_model=MasteryPrefillOut)
def get_mastery_prefill(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Derive skill mastery scores from the student's knowledge tracing states.
    Maps topic-level BKT/LSTM probabilities to the 7 Model 4 skill dimensions.
    Returns pre-filled mastery values ready to populate the goal alignment form.
    Students can only prefill their own data; instructors/admins can prefill any student.
    """
    if current_user.role == "STUDENT" and current_user.id != student_id:
        raise HTTPException(
            status_code=403,
            detail="Students can only prefill their own mastery data."
        )

    from app.models.knowledge_tracing import StudentKnowledgeState
    from app.models.course import Topic
    from app.model4_alignment.model4_service import derive_mastery_from_knowledge_states

    states = db.query(StudentKnowledgeState).filter(
        StudentKnowledgeState.student_id == student_id
    ).all()

    # Enrich with topic titles for keyword matching
    enriched = []
    for state in states:
        topic = db.query(Topic).filter(Topic.id == state.topic_id).first()
        enriched.append({
            "topic_title": topic.title if topic else "",
            "bkt_probability": state.bkt_probability or 0.0,
            "lstm_probability": state.lstm_probability or 0.0,
        })

    mastery = derive_mastery_from_knowledge_states(enriched)
    return mastery


@router.post("/analyze-batch", response_model=List[GoalAlignmentResponse])
def analyze_batch(
    request: BatchAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["INSTRUCTOR", "ADMIN"])),
):
    """
    Bulk-analyze goal alignment for multiple students at once.
    Each student must have a saved goal profile to be re-analyzed.
    Instructors/Admins only.
    """
    from app.models.model4_goal_profile import StudentGoalProfile

    results = []
    errors = []

    for student_id in request.student_ids:
        profile = db.query(StudentGoalProfile).filter(
            StudentGoalProfile.student_id == student_id
        ).first()

        if not profile:
            errors.append(student_id)
            continue

        result = run_alignment_pipeline(
            db                = db,
            student_id        = student_id,
            goal_text         = profile.goal_text,
            html_mastery      = profile.html_mastery or 0.0,
            css_mastery       = profile.css_mastery or 0.0,
            js_mastery        = profile.js_mastery or 0.0,
            react_mastery     = profile.react_mastery or 0.0,
            python_mastery    = profile.python_mastery or 0.0,
            ml_mastery        = profile.ml_mastery or 0.0,
            dsa_mastery       = profile.dsa_mastery or 0.0,
            environment       = profile.environment or "online",
            engagement_score  = profile.engagement_score or 0.5,
            consistency_score = profile.consistency_score or 0.5,
            integrity_score   = profile.integrity_score or 0.8,
            anomaly_score     = profile.anomaly_score or 0.0,
        )
        results.append(result)

    return results


@router.get("/all", response_model=List[GoalProfileOut])
def get_all_goal_profiles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["INSTRUCTOR", "ADMIN"])),
):
    """
    List all stored goal profiles.
    Accessible by INSTRUCTOR and ADMIN only.
    """
    from app.models.model4_goal_profile import StudentGoalProfile
    profiles = db.query(StudentGoalProfile).all()
    return profiles
