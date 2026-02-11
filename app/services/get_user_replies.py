from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_reply import UserReply
from app.utils.logger import logger


def get_user_replies(
    db: Session = Depends(get_db),
    last_hours: Optional[int] = Query(
        None, ge=1, description="Get replies from the last N hours (positive integer)"
    ),
):
    try:
        query = db.query(UserReply)

        if last_hours is not None:
            start_time = datetime.utcnow() - timedelta(hours=last_hours)
            query = query.filter(UserReply.timestamp >= start_time)
            logger.info(f"Filtering by last {last_hours} hours (from {start_time} UTC)")

        replies = query.all()

        data = [
            {
                "id": reply.id,
                "user_name": reply.user_name,
                "user_id": reply.user_id,
                "message": reply.message,
                "timestamp": reply.timestamp.isoformat() + "Z",
            }
            for reply in replies
        ]

        return {
            "count": len(data),
            "replies": data,
        }

    except Exception as e:
        logger.error(f"Error retrieving user replies: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
