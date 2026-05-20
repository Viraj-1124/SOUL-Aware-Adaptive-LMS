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
