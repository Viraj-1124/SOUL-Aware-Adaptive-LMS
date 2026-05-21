from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AlertSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AlertType(str, Enum):
    FATIGUE = "FATIGUE"
    DISENGAGEMENT = "DISENGAGEMENT"
    PERFORMANCE = "PERFORMANCE"
    ATTENDANCE = "ATTENDANCE"
    MOTIVATION = "MOTIVATION"
    COGNITIVE_LOAD = "COGNITIVE_LOAD"


# Alert Rule Schemas
class AlertRuleCreate(BaseModel):
    student_id: int
    course_id: int
    alert_type: AlertType
    trigger_metric: str
    threshold: float
    operator: str = ">="
    severity: AlertSeverity = AlertSeverity.MEDIUM
    cooldown_hours: float = 24


class AlertRuleResponse(BaseModel):
    id: int
    alert_type: AlertType
    threshold: float
    severity: AlertSeverity
    active: bool
    last_triggered: Optional[datetime]
    
    class Config:
        from_attributes = True


# Student Alert Schemas
class StudentAlertResponse(BaseModel):
    id: int
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    metric_value: Optional[float]
    created_at: datetime
    acknowledged_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class StudentAlertAcknowledge(BaseModel):
    acknowledged_by_id: int
    dismissal_reason: Optional[str] = None
    action_taken: Optional[str] = None


# Remediation Module Schemas
class RemediationModuleCreate(BaseModel):
    student_id: int
    course_id: int
    title: str
    description: Optional[str]
    skill_gap: str
    difficulty_level: str
    content: str
    content_type: str
    generated_by: str = "LLM_OPENAI"


class RemediationModuleResponse(BaseModel):
    id: int
    student_id: int
    title: str
    description: Optional[str]
    skill_gap: str
    difficulty_level: str
    content: str
    content_type: str
    completion_percentage: float
    score: Optional[float]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class RemediationModuleUpdate(BaseModel):
    completion_percentage: Optional[float] = None
    score: Optional[float] = None
    completed_at: Optional[datetime] = None


# Reflection Prompt Schemas
class ReflectionPromptCreate(BaseModel):
    student_id: int
    module_id: Optional[int] = None
    prompt_text: str
    context: str


class ReflectionPromptResponse(BaseModel):
    id: int
    prompt_text: str
    context: str
    generated_at: datetime
    response: Optional[str]
    response_submitted_at: Optional[datetime]
    reflection_depth_score: Optional[float]
    sentiment: Optional[float]
    
    class Config:
        from_attributes = True


class ReflectionPromptSubmit(BaseModel):
    response: str


# Ethical Profile Schemas
class EthicalProfileResponse(BaseModel):
    id: int
    student_id: int
    academic_integrity_score: float
    collaboration_fairness_score: float
    self_regulation_score: float
    responsibility_index: float
    integrity_flags: int
    collaboration_violations: int
    self_plagiarism_detected: bool
    last_violation_at: Optional[datetime]
    intervention_sent: bool
    
    class Config:
        from_attributes = True


class CurriculumAnalyzeRequest(BaseModel):
    current_modules: List[int]


# Curriculum Sequence Schemas
class CurriculumSequenceResponse(BaseModel):
    id: int
    student_id: int
    adaptation_reason: str
    skill_gaps: str
    adapted_sequence: Optional[str]
    applied_at: Optional[datetime]
    effectiveness_score: Optional[float]
    
    class Config:
        from_attributes = True


# Engagement Snapshot Schemas
class EngagementSnapshotResponse(BaseModel):
    id: int
    student_id: int
    engagement_score: float
    activity_count: int
    engagement_trend: str
    timestamp: datetime
    
    class Config:
        from_attributes = True
