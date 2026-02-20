from pydantic import BaseModel

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
