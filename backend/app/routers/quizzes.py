from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal,get_db
from app.auth.dependencies import admin_only, get_current_user, require_role
from .. import models, schemas
from app.models.knowledge_tracing import StudentQuestionInteraction
from app.knowledge_tracing import KnowledgeService
import logging

router = APIRouter(prefix="/quiz", tags=["Quiz"])

@router.post("/question", response_model=schemas.QuizQuestionOut, dependencies=[Depends(require_role(["ADMIN", "INSTRUCTOR"]))])
def add_question(question: schemas.QuizQuestionCreate, db: Session = Depends(get_db)):
    new_question = models.QuizQuestion(**question.dict())
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question


@router.get("/topic/{topic_id}", response_model=list[schemas.QuizQuestionOut])
def get_questions(topic_id: int, db: Session = Depends(get_db)):
    return db.query(models.QuizQuestion).filter(
        models.QuizQuestion.topic_id == topic_id
    ).all()


@router.post("/submit", response_model=schemas.QuizAttemptOut)
def submit_quiz(
    submission: schemas.QuizSubmission,
    db: Session = Depends(get_db), 
    user = Depends(get_current_user)
):
    questions = db.query(models.QuizQuestion).filter(
        models.QuizQuestion.topic_id == submission.topic_id
    ).all()

    if not questions:
        raise HTTPException(status_code=404, detail="No questions found")

    score = 0
    for q in questions:
        if str(q.id) in submission.answers:
            is_correct = submission.answers[str(q.id)] == q.correct_option
            if is_correct:
                score += 1
            
            # Record the interaction for Knowledge Tracing
            previous_attempts = db.query(StudentQuestionInteraction).filter(
                StudentQuestionInteraction.student_id == user.id,
                StudentQuestionInteraction.question_id == q.id
            ).count()
            
            interaction = StudentQuestionInteraction(
                student_id=user.id,
                topic_id=submission.topic_id,
                question_id=q.id,
                attempt_number=previous_attempts + 1,
                correct=is_correct
            )
            db.add(interaction)

    attempt = models.QuizAttempt(
        user_id=user.id,
        topic_id=submission.topic_id,
        score=score,
        total_questions=len(questions),
        time_spent=submission.time_spent
    )

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    # Trigger Knowledge Tracing Engine
    try:
        KnowledgeService.process_quiz_submission(db, user.id, submission.topic_id)
    except Exception as e:
        logging.error(f"Knowledge Tracing update failed for user {user.id}, topic {submission.topic_id}: {e}")

    return attempt
