"""
model4_alignment.py
Pydantic Schemas — Model 4 (Purpose & Skill Alignment)
"""

import json
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class GoalAlignmentRequest(BaseModel):
    """Request body for POST /alignment/analyze"""
    goal_text: str = Field(..., min_length=3, description="Student's goal statement")

    # Skill mastery (0.0 – 1.0)
    html_mastery:   float = Field(0.0, ge=0.0, le=1.0)
    css_mastery:    float = Field(0.0, ge=0.0, le=1.0)
    js_mastery:     float = Field(0.0, ge=0.0, le=1.0)
    react_mastery:  float = Field(0.0, ge=0.0, le=1.0)
    python_mastery: float = Field(0.0, ge=0.0, le=1.0)
    ml_mastery:     float = Field(0.0, ge=0.0, le=1.0)
    dsa_mastery:    float = Field(0.0, ge=0.0, le=1.0)

    # Learning context
    environment:       str   = Field("online", description="online/lab/project/self-study")
    engagement_score:  float = Field(0.5, ge=0.0, le=1.0)
    consistency_score: float = Field(0.5, ge=0.0, le=1.0)
    integrity_score:   float = Field(0.8, ge=0.0, le=1.0)
    anomaly_score:     float = Field(0.0, ge=0.0, le=1.0)


class GoalAlignmentResponse(BaseModel):
    """Full response from the Model 4 pipeline"""
    student_id:               int
    goal_text:                str
    goal_type:                str
    goal_specificity_score:   float
    collaboration_score:      float

    alignment_score:          float
    predicted_domain:         str
    all_domain_scores:        Dict[str, float]

    skill_gap:                float
    skill_gap_vector:         Dict[str, float]
    weakest_topics:           List[str]

    context_adjustment_score: float
    learning_mode_hint:       str
    integrity_flag:           bool
    scaffold_level:           str
    behavior_summary:         str

    recommendation:           str
    learning_path:            List[str]
    resources:                List[str]
    explanation:              str
    confidence_score:         float


class GoalProfileOut(BaseModel):
    """
    Stored goal profile returned by GET /alignment/profile/{student_id}.
    JSON string columns (weakest_topics, learning_path, resources) are
    automatically parsed into proper Python lists on read.
    """
    id:                       int
    student_id:               int
    goal_text:                str
    goal_type:                Optional[str]
    goal_specificity_score:   Optional[float]
    alignment_score:          Optional[float]
    predicted_domain:         Optional[str]
    skill_gap:                Optional[float]
    weakest_topics:           Optional[List[str]]
    scaffold_level:           Optional[str]
    learning_mode_hint:       Optional[str]
    integrity_flag:           Optional[bool]
    recommendation:           Optional[str]
    learning_path:            Optional[List[str]]
    resources:                Optional[List[str]]
    confidence_score:         Optional[float]
    behavior_summary:         Optional[str]
    explanation:              Optional[str]
    created_at:               Optional[datetime]
    updated_at:               Optional[datetime]

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, values):
        """
        SQLAlchemy ORM objects expose attributes, not dict keys.
        Convert the ORM object to a dict first, then parse JSON string columns.
        """
        # Handle both ORM objects and plain dicts
        if not isinstance(values, dict):
            values = {c.key: getattr(values, c.key) for c in values.__table__.columns}

        for field in ("weakest_topics", "learning_path", "resources"):
            raw = values.get(field)
            if isinstance(raw, str):
                try:
                    values[field] = json.loads(raw)
                except (json.JSONDecodeError, ValueError):
                    values[field] = []
        return values

    class Config:
        from_attributes = True


class MasteryPrefillOut(BaseModel):
    """
    Pre-filled skill mastery values derived from knowledge tracing states.
    Returned by GET /alignment/mastery-prefill/{student_id}.
    source_topics shows which topics contributed to each skill score.
    """
    html_mastery:    float
    css_mastery:     float
    js_mastery:      float
    react_mastery:   float
    python_mastery:  float
    ml_mastery:      float
    dsa_mastery:     float
    source_topics:   Dict[str, List[str]]   # skill → list of matched topic titles
    has_data:        bool                   # False if no knowledge states exist yet


class BatchAnalyzeRequest(BaseModel):
    """Request body for POST /alignment/analyze-batch"""
    student_ids: List[int] = Field(..., min_length=1, description="List of student IDs to re-analyze")
