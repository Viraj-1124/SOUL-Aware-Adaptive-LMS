from pydantic import BaseModel
from typing import List

class UserCreate(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    role: str

    class Config:
        from_attribute = True


class CourseCreate(BaseModel):
    title: str
    description: str | None = None


class CourseOut(BaseModel):
    id: int
    title: str
    description: str | None

    class Config:
        from_attribute = True


class TopicCreate(BaseModel):
    title: str
    course_id: int


class TopicOut(BaseModel):
    id: int
    title: str
    course_id: int

    class Config:
        from_attribute = True


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


class ActivityCreate(BaseModel):
    user_id: int
    topic_id: int
    event_type: str
    time_spent: float


class ActivityOut(BaseModel):
    id: int
    user_id: int
    topic_id: int
    event_type: str
    time_spent: float

    class Config:
        from_attribute = True


class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
