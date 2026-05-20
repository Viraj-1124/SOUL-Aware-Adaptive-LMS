"""
model4_goal_profile.py
DB Model — Student Goal Profile (Model 4: Purpose & Skill Alignment)
──────────────────────────────────────────────────────────────────────
Stores the full output of the Model 4 pipeline per student.
One row per student (upserted on each new goal submission).
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from datetime import datetime
from app.database import Base


class StudentGoalProfile(Base):
    __tablename__ = "student_goal_profiles"

    id         = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # ── Goal inputs ───────────────────────────────────────────────────────────
    goal_text              = Column(Text, nullable=False)
    goal_type              = Column(String(20))          # career/project/learning/vague
    goal_specificity_score = Column(Float)
    goal_embedding         = Column(Text)                # JSON string (384-dim vector)

    # ── Skill mastery inputs ──────────────────────────────────────────────────
    html_mastery    = Column(Float)
    css_mastery     = Column(Float)
    js_mastery      = Column(Float)
    react_mastery   = Column(Float)
    python_mastery  = Column(Float)
    ml_mastery      = Column(Float)
    dsa_mastery     = Column(Float)

    # ── Behavior inputs ───────────────────────────────────────────────────────
    environment       = Column(String(20))   # online/lab/project/self-study
    engagement_score  = Column(Float)
    consistency_score = Column(Float)
    integrity_score   = Column(Float)
    anomaly_score     = Column(Float)
    collaboration_score = Column(Float)

    # ── Alignment outputs ─────────────────────────────────────────────────────
    alignment_score   = Column(Float)
    predicted_domain  = Column(String(30))
    all_domain_scores = Column(Text)         # JSON string {domain: score}

    # ── Skill gap outputs ─────────────────────────────────────────────────────
    skill_gap        = Column(Float)
    skill_gap_vector = Column(Text)          # JSON string {skill: gap}
    weakest_topics   = Column(Text)          # JSON string [topic, ...]

    # ── Context outputs ───────────────────────────────────────────────────────
    context_adjustment_score = Column(Float)
    learning_mode_hint       = Column(String(20))
    integrity_flag           = Column(Boolean)
    scaffold_level           = Column(String(10))
    behavior_summary         = Column(Text)

    # ── Decision outputs ──────────────────────────────────────────────────────
    recommendation   = Column(Text)
    learning_path    = Column(Text)          # JSON string [step, ...]
    resources        = Column(Text)          # JSON string [resource, ...]
    explanation      = Column(Text)
    confidence_score = Column(Float)

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
