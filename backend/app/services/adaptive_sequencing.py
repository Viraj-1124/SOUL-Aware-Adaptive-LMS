import logging
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
import json
from datetime import datetime

from app.models.alert import CurriculumSequence
from app.models.knowledge_tracing import StudentKnowledgeState
from app.models.student_prediction import StudentPrediction
from app.models.moral_fatigue_record import MoralFatigueRecord
from app.models.learning_health_snapshot import LearningHealthSnapshot

logger = logging.getLogger(__name__)


class AdaptiveSequencingService:
    """Service for adaptive curriculum sequencing based on student needs"""
    
    @staticmethod
    def analyze_skill_gaps(db: Session, student_id: int, course_id: int) -> Dict:
        """Analyze student's skill gaps"""
        try:
            # Get student's knowledge states for all skills
            knowledge_states = db.query(StudentKnowledgeState).filter(
                StudentKnowledgeState.student_id == student_id
            ).all()
            
            # Identify gaps: skills with low mastery probability
            gaps = []
            for state in knowledge_states:
                if hasattr(state, 'p_known') and state.p_known < 0.6:
                    gaps.append({
                        "skill_id": state.skill_id,
                        "skill_name": getattr(state, 'skill_name', f"Skill {state.skill_id}"),
                        "mastery_prob": state.p_known,
                        "priority": 1 - state.p_known  # Higher number = higher priority
                    })
            
            # Sort by priority
            gaps.sort(key=lambda x: x['priority'], reverse=True)
            return {
                "skill_gaps": gaps,
                "total_gaps": len(gaps),
                "critical_gaps": len([g for g in gaps if g['priority'] > 0.7])
            }
        except Exception as e:
            logger.error(f"Error analyzing skill gaps: {e}")
            return {"skill_gaps": [], "total_gaps": 0, "critical_gaps": 0}
    
    @staticmethod
    def detect_cognitive_overload(db: Session, student_id: int, course_id: int) -> bool:
        """Detect if student is experiencing cognitive overload"""
        try:
            # Check fatigue level
            latest_fatigue = db.query(MoralFatigueRecord).filter(
                and_(
                    MoralFatigueRecord.student_id == student_id,
                    MoralFatigueRecord.course_id == course_id
                )
            ).order_by(desc(MoralFatigueRecord.created_at)).first()
            
            if latest_fatigue and latest_fatigue.fatigue_score >= 5:
                return True
            
            # Check if multiple high-difficulty tasks assigned
            # (This would need task assignment tracking)
            
            return False
        except Exception as e:
            logger.error(f"Error detecting cognitive overload: {e}")
            return False
    
    @staticmethod
    def check_prerequisite_mastery(db: Session, student_id: int, skill_id: int) -> bool:
        """Check if student has mastered prerequisite skills"""
        try:
            # Get this skill's prerequisites (mock implementation)
            prerequisites = {
                1: [],  # Introduction has no prerequisites
                2: [1],  # Intermediate requires Introduction
                3: [1, 2],  # Advanced requires Intro + Intermediate
            }
            
            required_prereqs = prerequisites.get(skill_id, [])
            
            for prereq_id in required_prereqs:
                prereq_state = db.query(StudentKnowledgeState).filter(
                    and_(
                        StudentKnowledgeState.student_id == student_id,
                        StudentKnowledgeState.skill_id == prereq_id
                    )
                ).first()
                
                if not prereq_state or prereq_state.p_known < 0.7:
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking prerequisites: {e}")
            return False
    
    @staticmethod
    def get_optimal_sequence(db: Session, student_id: int, course_id: int, 
                           current_sequence: List[int]) -> Tuple[List[int], str]:
        """Calculate optimal curriculum sequence for student"""
        try:
            # Get student's current state
            skill_analysis = AdaptiveSequencingService.analyze_skill_gaps(db, student_id, course_id)
            is_overloaded = AdaptiveSequencingService.detect_cognitive_overload(db, student_id, course_id)
            
            # Get burnout risk
            latest_prediction = db.query(StudentPrediction).filter(
                StudentPrediction.student_id == student_id
            ).order_by(desc(StudentPrediction.created_at)).first()
            
            burnout_risk = latest_prediction.burnout_probability if latest_prediction else 0
            
            # Determine adaptation reason
            adaptation_reason = "STANDARD"
            recommended_sequence = list(current_sequence)
            
            # 1. If critical skill gaps exist, prioritize remedial content
            if skill_analysis['critical_gaps'] > 0:
                adaptation_reason = "SKILL_GAP"
                gaps = skill_analysis['skill_gaps'][:3]  # Top 3 gaps
                gap_ids = [g['skill_id'] for g in gaps]
                
                # Move remedial skills to front
                recommended_sequence = gap_ids + [s for s in current_sequence if s not in gap_ids]
            
            # 2. If fatigued, reduce workload
            elif is_overloaded:
                adaptation_reason = "FATIGUE"
                # Reduce sequence to easier, shorter modules
                # Take every other module or reduce total count
                recommended_sequence = current_sequence[::2]  # Every other module
            
            # 3. If high burnout risk, adjust pacing
            elif burnout_risk > 0.7:
                adaptation_reason = "PACE_ADJUSTMENT"
                # Spread out the sequence over more time
                # Interleave with breaks/reflections
                recommended_sequence = AdaptiveSequencingService._interleave_reflections(current_sequence)
            
            return recommended_sequence, adaptation_reason
        
        except Exception as e:
            logger.error(f"Error calculating optimal sequence: {e}")
            return current_sequence, "ERROR"
    
    @staticmethod
    def _interleave_reflections(sequence: List[int]) -> List[int]:
        """Interleave reflection prompts into sequence"""
        result = []
        for i, item in enumerate(sequence):
            result.append(item)
            if (i + 1) % 3 == 0:  # After every 3 items, add reflection marker (999)
                result.append(999)  # Special marker for reflection
        return result
    
    @staticmethod
    def create_adaptive_sequence(
        db: Session,
        student_id: int,
        course_id: int,
        current_modules: List[int]
    ) -> Optional[CurriculumSequence]:
        """Create and store adaptive curriculum sequence"""
        try:
            # Get optimal sequence
            adapted_seq, reason = AdaptiveSequencingService.get_optimal_sequence(
                db, student_id, course_id, current_modules
            )
            
            # Get skill gaps analysis
            gaps_analysis = AdaptiveSequencingService.analyze_skill_gaps(db, student_id, course_id)
            
            # Create sequence record
            sequence = CurriculumSequence(
                student_id=student_id,
                course_id=course_id,
                original_sequence=json.dumps(current_modules),
                adapted_sequence=json.dumps(adapted_seq),
                adaptation_reason=reason,
                skill_gaps=json.dumps(gaps_analysis['skill_gaps'])
            )
            
            db.add(sequence)
            db.commit()
            db.refresh(sequence)
            
            logger.info(f"Created adaptive sequence {sequence.id} for student {student_id}")
            return sequence
        
        except Exception as e:
            logger.error(f"Error creating adaptive sequence: {e}")
            return None
    
    @staticmethod
    def evaluate_sequence_effectiveness(db: Session, sequence_id: int, 
                                       performance_improvement: float) -> bool:
        """Evaluate how effective the adaptive sequence was"""
        try:
            sequence = db.query(CurriculumSequence).filter(
                CurriculumSequence.id == sequence_id
            ).first()
            
            if sequence:
                sequence.effectiveness_score = performance_improvement
                db.commit()
                logger.info(f"Updated sequence {sequence_id} effectiveness: {performance_improvement}")
                return True
            return False
        
        except Exception as e:
            logger.error(f"Error evaluating sequence effectiveness: {e}")
            return False
    
    @staticmethod
    def should_readapt_sequence(db: Session, student_id: int, course_id: int) -> bool:
        """Determine if curriculum should be readapted"""
        try:
            # Get latest sequence
            latest = db.query(CurriculumSequence).filter(
                and_(
                    CurriculumSequence.student_id == student_id,
                    CurriculumSequence.course_id == course_id
                )
            ).order_by(desc(CurriculumSequence.created_at)).first()
            
            if not latest:
                return True  # No sequence yet
            
            # Check if it's been more than 7 days
            days_since = (datetime.utcnow() - latest.created_at).days
            if days_since >= 7:
                return True
            
            # Check if student's situation has changed significantly
            # (e.g., fatigue increased, burnout risk increased)
            latest_prediction = db.query(StudentPrediction).filter(
                StudentPrediction.student_id == student_id
            ).order_by(desc(StudentPrediction.created_at)).first()
            
            if latest_prediction and latest_prediction.burnout_probability > 0.8:
                return True
            
            # Check fatigue level
            latest_fatigue = db.query(MoralFatigueRecord).filter(
                and_(
                    MoralFatigueRecord.student_id == student_id,
                    MoralFatigueRecord.course_id == course_id
                )
            ).order_by(desc(MoralFatigueRecord.created_at)).first()
            
            if latest_fatigue and latest_fatigue.fatigue_score >= 6:
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error checking if should readapt sequence: {e}")
            return False


# ============================================================================
# Exposed Functions for API
# ============================================================================

def analyze_and_create_adaptive_curriculum(
    db: Session,
    student_id: int,
    course_id: int,
    current_modules: List[int]
) -> Dict:
    """Main function to analyze student and create adaptive curriculum"""
    try:
        # Check if readaptation is needed
        if not AdaptiveSequencingService.should_readapt_sequence(db, student_id, course_id):
            latest = db.query(CurriculumSequence).filter(
                and_(
                    CurriculumSequence.student_id == student_id,
                    CurriculumSequence.course_id == course_id
                )
            ).order_by(desc(CurriculumSequence.created_at)).first()
            
            if latest:
                return {
                    "status": "using_existing",
                    "sequence_id": latest.id,
                    "adapted_sequence": json.loads(latest.adapted_sequence),
                    "reason": latest.adaptation_reason
                }
        
        # Create new sequence
        sequence = AdaptiveSequencingService.create_adaptive_sequence(
            db, student_id, course_id, current_modules
        )
        
        if sequence:
            return {
                "status": "created",
                "sequence_id": sequence.id,
                "adapted_sequence": json.loads(sequence.adapted_sequence),
                "reason": sequence.adaptation_reason,
                "skill_gaps": json.loads(sequence.skill_gaps)
            }
        
        return {
            "status": "error",
            "message": "Failed to create sequence"
        }
    
    except Exception as e:
        logger.error(f"Error in analyze_and_create_adaptive_curriculum: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
