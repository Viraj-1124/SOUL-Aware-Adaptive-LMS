from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database import Base

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    topic_id = Column(Integer, index=True)
    event_type = Column(String)
    time_spent = Column(Float)  # seconds
    timestamp = Column(DateTime, default=datetime.utcnow)
