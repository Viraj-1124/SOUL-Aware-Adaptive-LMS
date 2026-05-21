from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.alert_service import (
    AlertService, RemediationService, EthicsService, CurriculumService, EngagementService
)
from app.services.adaptive_sequencing import analyze_and_create_adaptive_curriculum
from app.schemas.alert import (
    AlertRuleCreate, StudentAlertResponse, StudentAlertAcknowledge,
    RemediationModuleCreate, RemediationModuleResponse, RemediationModuleUpdate,
    ReflectionPromptCreate, ReflectionPromptResponse, ReflectionPromptSubmit,
    EthicalProfileResponse, CurriculumSequenceResponse, EngagementSnapshotResponse,
    CurriculumAnalyzeRequest
)
from app.auth.dependencies import get_current_user
from typing import List

router = APIRouter(prefix="/api", tags=["alerts"])

# ============================================================================
# ALERT ENDPOINTS
# ============================================================================

@router.post("/alerts/rules", response_model=dict)
async def create_alert_rule(
    rule_data: AlertRuleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new alert rule for a student"""
    rule = AlertService.create_alert_rule(db, rule_data)
    return {
        "id": rule.id,
        "alert_type": rule.alert_type,
        "threshold": rule.threshold,
        "severity": rule.severity,
        "active": rule.active
    }


@router.get("/alerts/student/{student_id}", response_model=List[StudentAlertResponse])
async def get_student_alerts(
    student_id: int,
    unacknowledged_only: bool = False,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get alerts for a student"""
    alerts = AlertService.get_student_alerts(db, student_id, unacknowledged_only)
    return alerts


@router.post("/alerts/check/{student_id}/{course_id}", response_model=dict)
async def check_and_create_alerts(
    student_id: int,
    course_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Manually trigger alert checking"""
    alerts = AlertService.check_and_create_alerts(db, student_id, course_id)
    return {
        "alerts_created": len(alerts),
        "alerts": [
            {
                "id": a.id,
                "alert_type": a.alert_type,
                "severity": a.severity,
                "title": a.title,
                "metric_value": a.metric_value
            }
            for a in alerts
        ]
    }


@router.post("/alerts/{alert_id}/acknowledge", response_model=StudentAlertResponse)
async def acknowledge_alert(
    alert_id: int,
    ack_data: StudentAlertAcknowledge,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Acknowledge an alert"""
    alert = AlertService.acknowledge_alert(db, alert_id, ack_data)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


# ============================================================================
# REMEDIATION MODULE ENDPOINTS
# ============================================================================

@router.post("/remediation/modules", response_model=RemediationModuleResponse)
async def create_remediation_module(
    module_data: RemediationModuleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new remediation module"""
    module = RemediationService.create_module(db, module_data)
    return module


@router.get("/remediation/student/{student_id}/{course_id}", response_model=List[RemediationModuleResponse])
async def get_student_modules(
    student_id: int,
    course_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all remediation modules for a student"""
    modules = RemediationService.get_student_modules(db, student_id, course_id)
    return modules


@router.put("/remediation/modules/{module_id}", response_model=RemediationModuleResponse)
async def update_module_progress(
    module_id: int,
    update_data: RemediationModuleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update remediation module progress"""
    module = RemediationService.update_module_progress(
        db, module_id, 
        update_data.completion_percentage or 0, 
        update_data.score
    )
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return module


# ============================================================================
# REFLECTION PROMPT ENDPOINTS
# ============================================================================

@router.post("/reflection/prompts", response_model=ReflectionPromptResponse)
async def create_reflection_prompt(
    prompt_data: ReflectionPromptCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a reflection prompt"""
    prompt = RemediationService.create_reflection_prompt(db, prompt_data)
    return prompt


@router.get("/reflection/student/{student_id}", response_model=List[ReflectionPromptResponse])
async def get_student_prompts(
    student_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all reflection prompts for a student"""
    prompts = RemediationService.get_student_prompts(db, student_id)
    return prompts


@router.post("/reflection/prompts/{prompt_id}/submit", response_model=ReflectionPromptResponse)
async def submit_reflection(
    prompt_id: int,
    response_data: ReflectionPromptSubmit,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Submit a reflection response"""
    prompt = RemediationService.submit_reflection(db, prompt_id, response_data)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


# ============================================================================
# ETHICS PROFILE ENDPOINTS
# ============================================================================

@router.get("/ethics/profile/{student_id}", response_model=EthicalProfileResponse)
async def get_ethical_profile(
    student_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get ethical profile for a student"""
    profile = EthicsService.get_or_create_profile(db, student_id, None)
    return profile


@router.post("/ethics/flag/{student_id}", response_model=EthicalProfileResponse)
async def flag_violation(
    student_id: int,
    violation_type: str = "SUSPICIOUS_PATTERN",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Flag an integrity violation"""
    profile = EthicsService.flag_integrity_violation(db, student_id, violation_type)
    return profile


@router.put("/ethics/responsibility/{student_id}", response_model=EthicalProfileResponse)
async def update_responsibility(
    student_id: int,
    adjustment: float,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update responsibility index"""
    profile = EthicsService.update_responsibility_index(db, student_id, adjustment)
    return profile


# ============================================================================
# CURRICULUM SEQUENCE ENDPOINTS
# ============================================================================

@router.post("/curriculum/sequence", response_model=CurriculumSequenceResponse)
async def create_curriculum_sequence(
    student_id: int,
    course_id: int,
    original_seq: str,
    adapted_seq: str,
    reason: str,
    skill_gaps: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create curriculum sequence"""
    sequence = CurriculumService.create_sequence(
        db, student_id, course_id, original_seq, adapted_seq, reason, skill_gaps
    )
    return sequence


@router.get("/curriculum/latest/{student_id}/{course_id}", response_model=CurriculumSequenceResponse)
async def get_latest_sequence(
    student_id: int,
    course_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get latest curriculum sequence"""
    sequence = CurriculumService.get_latest_sequence(db, student_id, course_id)
    if not sequence:
        raise HTTPException(status_code=404, detail="No sequence found")
    return sequence


@router.post("/curriculum/apply/{sequence_id}", response_model=CurriculumSequenceResponse)
async def apply_sequence(
    sequence_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Apply curriculum sequence"""
    sequence = CurriculumService.apply_sequence(db, sequence_id)
    if not sequence:
        raise HTTPException(status_code=404, detail="Sequence not found")
    return sequence


# ============================================================================
# ENGAGEMENT TRACKING ENDPOINTS
# ============================================================================

@router.post("/engagement/snapshot", response_model=EngagementSnapshotResponse)
async def create_engagement_snapshot(
    student_id: int,
    course_id: int,
    engagement_score: float,
    activity_count: int,
    avg_response_time: float,
    trend: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create engagement snapshot"""
    snapshot = EngagementService.create_snapshot(
        db, student_id, course_id, engagement_score, activity_count, avg_response_time, trend
    )
    return snapshot


@router.get("/engagement/snapshots/{student_id}/{course_id}", response_model=List[EngagementSnapshotResponse])
async def get_engagement_snapshots(
    student_id: int,
    course_id: int,
    hours: int = 24,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get recent engagement snapshots"""
    snapshots = EngagementService.get_recent_snapshots(db, student_id, course_id, hours)
    return snapshots


@router.get("/engagement/trend/{student_id}/{course_id}", response_model=dict)
async def get_engagement_trend(
    student_id: int,
    course_id: int,
    days: int = 7,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get engagement trend"""
    trend = EngagementService.get_engagement_trend(db, student_id, course_id, days)
    return {
        "average_engagement": trend.get("average_engagement", 0.0),
        "trend": trend.get("trend", "STABLE"),
        "data_points": len(trend.get("snapshots", []))
    }


# ============================================================================
# ADAPTIVE CURRICULUM ENDPOINTS
# ============================================================================

@router.post("/curriculum/analyze/{student_id}/{course_id}", response_model=dict)
async def analyze_and_adapt_curriculum(
    student_id: int,
    course_id: int,
    req_data: CurriculumAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Analyze student and create adaptive curriculum"""
    result = analyze_and_create_adaptive_curriculum(db, student_id, course_id, req_data.current_modules)
    return result
