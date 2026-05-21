from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from app.models.alert import (
    StudentAlert, AlertRule, AlertLog, AlertSeverity, AlertType,
    RemediationModule, ReflectionPrompt, EthicalProfile, CurriculumSequence,
    EngagementSnapshot
)
from app.models.moral_fatigue_record import MoralFatigueRecord
from app.models.learning_health_snapshot import LearningHealthSnapshot
from app.models.activity import StudentActivityLog
from app.models.attendance import Attendance
from app.models.student_prediction import StudentPrediction
from app.schemas.alert import (
    AlertRuleCreate, StudentAlertAcknowledge, RemediationModuleCreate,
    ReflectionPromptCreate, ReflectionPromptSubmit
)
from app.services.learning_health_service import compute_learning_health
import logging

logger = logging.getLogger(__name__)


class AlertService:
    """Service for managing student alerts and triggers"""
    
    @staticmethod
    def create_alert_rule(db: Session, rule_data: AlertRuleCreate) -> AlertRule:
        """Create a new alert rule"""
        rule = AlertRule(
            **rule_data.dict()
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        logger.info(f"Created alert rule {rule.id} for student {rule.student_id}")
        return rule
    
    @staticmethod
    def get_active_rules(db: Session, student_id: int, course_id: int) -> List[AlertRule]:
        """Get all active rules for a student-course"""
        return db.query(AlertRule).filter(
            and_(
                AlertRule.student_id == student_id,
                AlertRule.course_id == course_id,
                AlertRule.active == True
            )
        ).all()
    
    @staticmethod
    def check_and_create_alerts(db: Session, student_id: int, course_id: int) -> List[StudentAlert]:
        """Check all rules for a student and create alerts if thresholds are exceeded"""
        alerts_created = []
        rules = AlertService.get_active_rules(db, student_id, course_id)
        
        for rule in rules:
            # Check cooldown: don't spam alerts
            if rule.last_triggered:
                cooldown_end = rule.last_triggered + timedelta(hours=rule.cooldown_hours)
                if datetime.utcnow() < cooldown_end:
                    continue
            
            # Get metric value
            metric_value = AlertService._get_metric_value(db, student_id, course_id, rule.trigger_metric)
            
            if metric_value is None:
                continue
            
            # Check threshold
            should_alert = AlertService._check_threshold(metric_value, rule.threshold, rule.operator)
            
            if should_alert:
                # Create alert
                alert = AlertService._create_alert_from_rule(db, rule, metric_value, student_id)
                alerts_created.append(alert)
                
                # Update last triggered
                rule.last_triggered = datetime.utcnow()
                db.commit()
                
                # Log alert
                AlertService._log_alert_action(db, alert.id, "generated", None, f"Metric: {metric_value}")
                logger.info(f"Created alert {alert.id} for student {student_id}")
        
        return alerts_created
    
    @staticmethod
    def _get_metric_value(db: Session, student_id: int, course_id: int, metric: str) -> Optional[float]:
        """Get current value of a metric"""
        try:
            if metric == "fatigue_score":
                latest = db.query(MoralFatigueRecord).filter(
                    and_(
                        MoralFatigueRecord.student_id == student_id,
                        MoralFatigueRecord.course_id == course_id
                    )
                ).order_by(desc(MoralFatigueRecord.created_at)).first()
                return latest.fatigue_score if latest else None
            
            elif metric == "health_score":
                latest = db.query(LearningHealthSnapshot).filter(
                    LearningHealthSnapshot.student_id == student_id
                ).order_by(desc(LearningHealthSnapshot.created_at)).first()
                return latest.health_index if latest else None
            
            elif metric == "engagement_score":
                week_ago = datetime.utcnow() - timedelta(days=7)
                activities = db.query(StudentActivityLog).filter(
                    and_(
                        StudentActivityLog.student_id == student_id,
                        StudentActivityLog.course_id == course_id,
                        StudentActivityLog.activity_timestamp >= week_ago
                    )
                ).count()
                return float(activities) / 7 if activities > 0 else 0
            
            elif metric == "attendance_rate":
                total_sessions = db.query(Attendance).filter(
                    and_(
                        Attendance.student_id == student_id,
                        Attendance.course_id == course_id
                    )
                ).count()
                attended = db.query(Attendance).filter(
                    and_(
                        Attendance.student_id == student_id,
                        Attendance.course_id == course_id,
                        Attendance.present == True
                    )
                ).count()
                return (attended / total_sessions * 100) if total_sessions > 0 else 0
            
            elif metric == "burnout_risk":
                latest = db.query(StudentPrediction).filter(
                    StudentPrediction.student_id == student_id
                ).order_by(desc(StudentPrediction.created_at)).first()
                return latest.burnout_probability if latest else None
        
        except Exception as e:
            logger.error(f"Error getting metric {metric} for student {student_id}: {e}")
        
        return None
    
    @staticmethod
    def _check_threshold(value: float, threshold: float, operator: str) -> bool:
        """Check if metric triggers alert"""
        if operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == "==":
            return value == threshold
        elif operator == "!=":
            return value != threshold
        return False
    
    @staticmethod
    def _create_alert_from_rule(db: Session, rule: AlertRule, metric_value: float, student_id: int) -> StudentAlert:
        """Create alert instance from rule"""
        message_map = {
            AlertType.FATIGUE: f"High moral fatigue detected (score: {metric_value:.1f}/7). Consider taking a break or reaching out to your educator.",
            AlertType.DISENGAGEMENT: f"Your engagement score is declining ({metric_value:.1f}/10). Try starting with a small activity to re-engage.",
            AlertType.PERFORMANCE: f"Performance trend detected (current: {metric_value:.1f}). Would you like personalized support?",
            AlertType.ATTENDANCE: f"Attendance rate is low ({metric_value:.1f}%). Consistent attendance helps learning outcomes.",
            AlertType.MOTIVATION: f"Motivation trend shows decline. Check your learning goal alignment.",
            AlertType.COGNITIVE_LOAD: f"Cognitive load seems high. Break your work into smaller chunks.",
        }
        
        title_map = {
            AlertType.FATIGUE: "Moral Fatigue Alert",
            AlertType.DISENGAGEMENT: "Disengagement Warning",
            AlertType.PERFORMANCE: "Performance Trend",
            AlertType.ATTENDANCE: "Low Attendance",
            AlertType.MOTIVATION: "Motivation Check-In",
            AlertType.COGNITIVE_LOAD: "Cognitive Load Alert",
        }
        
        alert = StudentAlert(
            rule_id=rule.id,
            student_id=student_id,
            alert_type=rule.alert_type,
            severity=rule.severity,
            title=title_map.get(rule.alert_type, "Alert"),
            message=message_map.get(rule.alert_type, rule.message_template or ""),
            metric_value=metric_value
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert
    
    @staticmethod
    def get_student_alerts(db: Session, student_id: int, unacknowledged_only: bool = False) -> List[StudentAlert]:
        """Get alerts for a student"""
        query = db.query(StudentAlert).filter(StudentAlert.student_id == student_id)
        
        if unacknowledged_only:
            query = query.filter(StudentAlert.acknowledged_at.is_(None))
        
        return query.order_by(desc(StudentAlert.created_at)).all()
    
    @staticmethod
    def acknowledge_alert(db: Session, alert_id: int, ack_data: StudentAlertAcknowledge) -> StudentAlert:
        """Mark alert as acknowledged"""
        alert = db.query(StudentAlert).filter(StudentAlert.id == alert_id).first()
        
        if alert:
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledged_by_id = ack_data.acknowledged_by_id
            alert.dismissal_reason = ack_data.dismissal_reason
            alert.action_taken = ack_data.action_taken
            db.commit()
            db.refresh(alert)
            
            AlertService._log_alert_action(
                db, alert_id, "acknowledged", ack_data.acknowledged_by_id, ack_data.dismissal_reason
            )
            logger.info(f"Alert {alert_id} acknowledged by {ack_data.acknowledged_by_id}")
        
        return alert
    
    @staticmethod
    def _log_alert_action(db: Session, alert_id: int, action: str, action_by_id: Optional[int], details: Optional[str]):
        """Log alert activity"""
        log = AlertLog(
            alert_id=alert_id,
            action=action,
            action_by_id=action_by_id,
            details=details
        )
        db.add(log)
        db.commit()


class RemediationService:
    """Service for managing remedial content and modules"""
    
    @staticmethod
    def create_module(db: Session, module_data: RemediationModuleCreate) -> RemediationModule:
        """Create a new remediation module"""
        module = RemediationModule(
            **module_data.dict(),
            assigned_at=datetime.utcnow()
        )
        db.add(module)
        db.commit()
        db.refresh(module)
        logger.info(f"Created remediation module {module.id}")
        return module
    
    @staticmethod
    def get_student_modules(db: Session, student_id: int, course_id: int) -> List[RemediationModule]:
        """Get all remediation modules for a student"""
        return db.query(RemediationModule).filter(
            and_(
                RemediationModule.student_id == student_id,
                RemediationModule.course_id == course_id
            )
        ).order_by(desc(RemediationModule.assigned_at)).all()
    
    @staticmethod
    def update_module_progress(db: Session, module_id: int, completion_percentage: float, score: Optional[float] = None) -> RemediationModule:
        """Update module progress"""
        module = db.query(RemediationModule).filter(RemediationModule.id == module_id).first()
        
        if module:
            module.completion_percentage = completion_percentage
            if score is not None:
                module.score = score
            if completion_percentage >= 100:
                module.completed_at = datetime.utcnow()
            db.commit()
            db.refresh(module)
        
        return module
    
    @staticmethod
    def create_reflection_prompt(db: Session, prompt_data: ReflectionPromptCreate) -> ReflectionPrompt:
        """Create a reflection prompt"""
        prompt = ReflectionPrompt(
            **prompt_data.dict()
        )
        db.add(prompt)
        db.commit()
        db.refresh(prompt)
        return prompt
    
    @staticmethod
    def submit_reflection(db: Session, prompt_id: int, response_data: ReflectionPromptSubmit) -> ReflectionPrompt:
        """Submit a reflection response"""
        prompt = db.query(ReflectionPrompt).filter(ReflectionPrompt.id == prompt_id).first()
        
        if prompt:
            prompt.response = response_data.response
            prompt.response_submitted_at = datetime.utcnow()
            db.commit()
            db.refresh(prompt)
        
        return prompt
    
    @staticmethod
    def get_student_prompts(db: Session, student_id: int) -> List[ReflectionPrompt]:
        """Get all reflection prompts for a student"""
        return db.query(ReflectionPrompt).filter(
            ReflectionPrompt.student_id == student_id
        ).order_by(desc(ReflectionPrompt.generated_at)).all()


class EthicsService:
    """Service for ethical profile and responsibility tracking"""
    
    @staticmethod
    def get_or_create_profile(db: Session, student_id: int, course_id: int) -> EthicalProfile:
        """Get or create ethical profile"""
        profile = db.query(EthicalProfile).filter(
            EthicalProfile.student_id == student_id
        ).first()
        
        if not profile:
            profile = EthicalProfile(
                student_id=student_id,
                course_id=course_id
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
        
        return profile
    
    @staticmethod
    def flag_integrity_violation(db: Session, student_id: int, violation_type: str = "SUSPICIOUS_PATTERN") -> EthicalProfile:
        """Flag an integrity violation"""
        profile = EthicsService.get_or_create_profile(db, student_id, None)
        
        if violation_type == "COLLABORATION":
            profile.collaboration_violations += 1
        elif violation_type == "PLAGIARISM":
            profile.self_plagiarism_detected = True
        else:
            profile.integrity_flags += 1
        
        profile.last_violation_at = datetime.utcnow()
        profile.academic_integrity_score = max(0, profile.academic_integrity_score - 10)
        
        db.commit()
        db.refresh(profile)
        logger.warning(f"Integrity violation for student {student_id}: {violation_type}")
        return profile
    
    @staticmethod
    def update_responsibility_index(db: Session, student_id: int, adjustment: float) -> EthicalProfile:
        """Update responsibility index"""
        profile = EthicsService.get_or_create_profile(db, student_id, None)
        profile.responsibility_index = max(0, min(100, profile.responsibility_index + adjustment))
        profile.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(profile)
        return profile


class CurriculumService:
    """Service for adaptive curriculum sequencing"""
    
    @staticmethod
    def create_sequence(db: Session, student_id: int, course_id: int, 
                       original_seq: str, adapted_seq: str, reason: str, skill_gaps: str) -> CurriculumSequence:
        """Create curriculum sequence"""
        sequence = CurriculumSequence(
            student_id=student_id,
            course_id=course_id,
            original_sequence=original_seq,
            adapted_sequence=adapted_seq,
            adaptation_reason=reason,
            skill_gaps=skill_gaps
        )
        db.add(sequence)
        db.commit()
        db.refresh(sequence)
        return sequence
    
    @staticmethod
    def get_latest_sequence(db: Session, student_id: int, course_id: int) -> Optional[CurriculumSequence]:
        """Get latest curriculum sequence"""
        return db.query(CurriculumSequence).filter(
            and_(
                CurriculumSequence.student_id == student_id,
                CurriculumSequence.course_id == course_id
            )
        ).order_by(desc(CurriculumSequence.created_at)).first()
    
    @staticmethod
    def apply_sequence(db: Session, sequence_id: int) -> CurriculumSequence:
        """Mark sequence as applied"""
        sequence = db.query(CurriculumSequence).filter(CurriculumSequence.id == sequence_id).first()
        
        if sequence:
            sequence.applied_at = datetime.utcnow()
            db.commit()
            db.refresh(sequence)
        
        return sequence


class EngagementService:
    """Service for real-time engagement tracking"""
    
    @staticmethod
    def create_snapshot(db: Session, student_id: int, course_id: int, 
                       engagement_score: float, activity_count: int, 
                       avg_response_time: float, trend: str) -> EngagementSnapshot:
        """Create engagement snapshot"""
        snapshot = EngagementSnapshot(
            student_id=student_id,
            course_id=course_id,
            engagement_score=engagement_score,
            activity_count=activity_count,
            avg_response_time=avg_response_time,
            engagement_trend=trend
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return snapshot
    
    @staticmethod
    def get_recent_snapshots(db: Session, student_id: int, course_id: int, hours: int = 24) -> List[EngagementSnapshot]:
        """Get recent engagement snapshots"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return db.query(EngagementSnapshot).filter(
            and_(
                EngagementSnapshot.student_id == student_id,
                EngagementSnapshot.course_id == course_id,
                EngagementSnapshot.timestamp >= cutoff
            )
        ).order_by(desc(EngagementSnapshot.timestamp)).all()
    
    @staticmethod
    def get_engagement_trend(db: Session, student_id: int, course_id: int, days: int = 7) -> Dict:
        """Get engagement trend over time"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        snapshots = db.query(EngagementSnapshot).filter(
            and_(
                EngagementSnapshot.student_id == student_id,
                EngagementSnapshot.course_id == course_id,
                EngagementSnapshot.timestamp >= cutoff
            )
        ).order_by(EngagementSnapshot.timestamp).all()
        
        if not snapshots:
            return {}
        
        return {
            "snapshots": snapshots,
            "average_engagement": sum(s.engagement_score for s in snapshots) / len(snapshots),
            "trend": snapshots[-1].engagement_trend if snapshots else "STABLE"
        }
