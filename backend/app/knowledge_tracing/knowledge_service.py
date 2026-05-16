from sqlalchemy.orm import Session
from datetime import datetime
from app.models.knowledge_tracing import StudentQuestionInteraction, StudentKnowledgeState, KnowledgeStateHistory
from app.knowledge_tracing.bkt_predictor import bkt_predictor
from app.knowledge_tracing.lstm_predictor import lstm_predictor
from app.knowledge_tracing.recommendation_engine import determine_mastery_level, get_recommendation

class KnowledgeService:
    @staticmethod
    def process_quiz_submission(db: Session, student_id: int, topic_id: int):
        """
        Updates the knowledge state for a given student and topic based on recent interactions.
        """
        # Fetch all interactions for this topic to feed BKT
        topic_interactions = db.query(StudentQuestionInteraction).filter(
            StudentQuestionInteraction.student_id == student_id,
            StudentQuestionInteraction.topic_id == topic_id
        ).order_by(StudentQuestionInteraction.created_at.asc()).all()

        correctness_history = [1 if inter.correct else 0 for inter in topic_interactions]
        bkt_prob = bkt_predictor.predict(correctness_history)

        # Fetch last 10 interactions for LSTM
        last_10_interactions = db.query(StudentQuestionInteraction).filter(
            StudentQuestionInteraction.student_id == student_id
        ).order_by(StudentQuestionInteraction.created_at.desc()).limit(10).all()

        # LSTM expects chronological order for sequence, so reverse the descending list
        last_10_interactions.reverse()
        
        lstm_input = [
            [inter.topic_id, inter.attempt_number, 1 if inter.correct else 0]
            for inter in last_10_interactions
        ]
        
        lstm_prob = lstm_predictor.predict(lstm_input)
        
        mastery_level = determine_mastery_level(bkt_prob, lstm_prob)

        # Update or create the latest snapshot
        state = db.query(StudentKnowledgeState).filter(
            StudentKnowledgeState.student_id == student_id,
            StudentKnowledgeState.topic_id == topic_id
        ).first()

        if not state:
            state = StudentKnowledgeState(
                student_id=student_id,
                topic_id=topic_id,
                bkt_probability=bkt_prob,
                lstm_probability=lstm_prob,
                mastery_level=mastery_level
            )
            db.add(state)
        else:
            state.bkt_probability = bkt_prob
            state.lstm_probability = lstm_prob
            state.mastery_level = mastery_level
            state.last_updated = datetime.utcnow()

        # Append to history
        history = KnowledgeStateHistory(
            student_id=student_id,
            topic_id=topic_id,
            bkt_probability=bkt_prob,
            lstm_probability=lstm_prob,
            mastery_level=mastery_level
        )
        db.add(history)
        
        db.commit()

    @staticmethod
    def get_knowledge_state(db: Session, student_id: int):
        states = db.query(StudentKnowledgeState).filter(
            StudentKnowledgeState.student_id == student_id
        ).all()
        return states

    @staticmethod
    def get_recommendation(db: Session, student_id: int, topic_id: int):
        state = db.query(StudentKnowledgeState).filter(
            StudentKnowledgeState.student_id == student_id,
            StudentKnowledgeState.topic_id == topic_id
        ).first()
        
        if not state:
            return {
                "student_id": student_id,
                "topic_id": topic_id,
                "recommendation": "Normal",
                "action_item": "No data available yet. Continue with standard progression."
            }

        avg_prob = (state.bkt_probability + state.lstm_probability) / 2.0
        rec, action = get_recommendation(avg_prob)

        return {
            "student_id": student_id,
            "topic_id": topic_id,
            "recommendation": rec,
            "action_item": action
        }
