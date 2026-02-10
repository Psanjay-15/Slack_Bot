from pydantic import BaseModel
from datetime import datetime
from typing import List


class SendMessageRequest(BaseModel):
    user_ids: List[str]
    message: str


class UserReplyMessage(BaseModel):
    user_name: str
    user_id: str
    message: str
    timestamp: datetime
