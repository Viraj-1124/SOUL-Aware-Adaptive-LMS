from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class AlertSeverity(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AlertType(str, enum.Enum):
    FATIGUE = "FATIGUE"
    DISENGAGEMENT = "DISENGAGEMENT"
    PERFORMANCE = "PERFORMANCE"
    ATTENDANCE = "ATTENDANCE"
    MOTIVATION = "MOTIVATION"
    COGNITIVE_LOAD = "COGNITIVE_LOAD"


class AlertRule(Base):
    """Trigger rules for automatic alerts"""
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    
    alert_type = Column(Enum(AlertType), nullable=False)
    trigger_metric = Column(String)
    threshold = Column(Float, nullable=False)
    operator = Column(String, default=">=")
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.MEDIUM)
    message_template = Column(Text)
    
    active = Column(Boolean, default=True)
    cooldown_hours = Column(Float, default=24)
    last_triggered = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    student = relationship("User", foreign_keys=[student_id])
    course = relationship("Course", foreign_keys=[course_id])


class StudentAlert(Base):
    """Individual alert instances"""
    __tablename__ = "student_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("alert_rules.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    alert_type = Column(Enum(AlertType), nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    metric_value = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by_id = Column(Integer, nullable=True)
    dismissal_reason = Column(String, nullable=True)
    
    action_taken = Column(String, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    rule = relationship("AlertRule")
    student = relationship("User", foreign_keys=[student_id])


class AlertLog(Base):
    """Audit trail for all alert activities"""
    __tablename__ = "alert_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("student_alerts.id"), nullable=True)
    action = Column(String)
    action_by_id = Column(Integer, nullable=True)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class RemediationModule(Base):
    """Personalized learning modules"""
    __tablename__ = "remediation_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    
    title = Column(String, nullable=False)
    description = Column(Text)
    skill_gap = Column(String)
    difficulty_level = Column(String)  # BEGINNER, INTERMEDIATE, ADVANCED
    content = Column(Text)
    content_type = Column(String)  # TEXT, VIDEO, QUIZ, INTERACTIVE
    
    generated_by = Column(String)  # LLM_OPENAI, LLM_CLAUDE, RULE_BASED
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    assigned_at = Column(DateTime)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    completion_percentage = Column(Float, default=0)
    score = Column(Float, nullable=True)
    
    student = relationship("User", foreign_keys=[student_id])
    course = relationship("Course", foreign_keys=[course_id])


class ReflectionPrompt(Base):
    """Reflection journal prompts"""
    __tablename__ = "reflection_prompts"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("remediation_modules.id"), nullable=True)
    
    prompt_text = Column(Text, nullable=False)
    context = Column(String)  # SKILL_GAP, FATIGUE, MOTIVATION
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    response = Column(Text, nullable=True)
    response_submitted_at = Column(DateTime, nullable=True)
    
    reflection_depth_score = Column(Float, nullable=True)
    sentiment = Column(Float, nullable=True)
    
    student = relationship("User", foreign_keys=[student_id])


class EthicalProfile(Base):
    """Ethical learning index and tracking"""
    __tablename__ = "ethical_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    
    academic_integrity_score = Column(Float, default=100)  # 0-100
    collaboration_fairness_score = Column(Float, default=100)
    self_regulation_score = Column(Float, default=100)
    responsibility_index = Column(Float, default=100)
    
    # Violations and flags
    integrity_flags = Column(Integer, default=0)
    collaboration_violations = Column(Integer, default=0)
    self_plagiarism_detected = Column(Boolean, default=False)
    
    last_violation_at = Column(DateTime, nullable=True)
    intervention_sent = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    student = relationship("User", foreign_keys=[student_id])


class CurriculumSequence(Base):
    """Tracks adaptive curriculum sequencing"""
    __tablename__ = "curriculum_sequences"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    
    original_sequence = Column(String)  # JSON: original module order
    adapted_sequence = Column(String)  # JSON: recommended order
    
    adaptation_reason = Column(String)  # SKILL_GAP, FATIGUE, PACE_ADJUSTMENT
    skill_gaps = Column(String)  # JSON: identified gaps
    
    applied_at = Column(DateTime, nullable=True)
    effectiveness_score = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    student = relationship("User", foreign_keys=[student_id])
    course = relationship("Course", foreign_keys=[course_id])


class EngagementSnapshot(Base):
    """Real-time engagement tracking snapshots"""
    __tablename__ = "engagement_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    
    engagement_score = Column(Float)
    activity_count = Column(Integer)
    avg_response_time = Column(Float)
    
    engagement_trend = Column(String)  # INCREASING, STABLE, DECREASING
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("User", foreign_keys=[student_id])
    course = relationship("Course", foreign_keys=[course_id])
