from pydantic import BaseModel

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
