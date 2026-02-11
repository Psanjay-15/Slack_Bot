from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.database import Base


class UserReply(Base):
    __tablename__ = "user_replies"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, index=True)
    user_id = Column(String, index=True)
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
