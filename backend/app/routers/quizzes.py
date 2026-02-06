from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal,get_db
from .. import models, schemas

router = APIRouter(prefix="/quiz", tags=["Quiz"])

@router.post("/question", response_model=schemas.QuizQuestionOut)
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
def submit_quiz(submission: schemas.QuizSubmission, db: Session = Depends(get_db)):
    questions = db.query(models.QuizQuestion).filter(
        models.QuizQuestion.topic_id == submission.topic_id
    ).all()

    if not questions:
        raise HTTPException(status_code=404, detail="No questions found")

    score = 0
    for q in questions:
        if str(q.id) in submission.answers:
            if submission.answers[str(q.id)] == q.correct_option:
                score += 1

    attempt = models.QuizAttempt(
        user_id=submission.user_id,
        topic_id=submission.topic_id,
        score=score,
        total_questions=len(questions),
        time_spent=submission.time_spent
    )

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return attempt
