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