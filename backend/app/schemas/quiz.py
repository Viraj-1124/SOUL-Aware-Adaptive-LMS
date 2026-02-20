from pydantic import BaseModel

class QuizQuestionCreate(BaseModel):
    topic_id: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str


class QuizQuestionOut(BaseModel):
    id: int
    topic_id: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str

    class Config:
        from_attribute = True


class QuizSubmission(BaseModel):
    topic_id: int
    answers: dict  
    time_spent: float


class QuizAttemptOut(BaseModel):
    id: int
    user_id: int
    topic_id: int
    score: float
    total_questions: int
    time_spent: float

    class Config:
        from_attribute = True
