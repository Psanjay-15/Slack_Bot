from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.send_message import send_direct_message
from app.services.slack_connection import handle_slack_connection
from app.services.get_user_replies import get_user_replies
from app.schemas.schemas import SendMessageRequest
from app.services.summarizer import UserReplySummarizer
from app.database import get_db
from sqlalchemy.orm import Session
from typing import Optional
from app.utils.logger import logger
from app.services.slack_client import SlackClient


router = APIRouter(prefix="/slack", tags=["Slack"])

summarizer = UserReplySummarizer()
slack_client = SlackClient()


router.post("/connect")(handle_slack_connection)
router.get("/user-replies")(get_user_replies)


@router.post("/send-message")
async def send_message_endpoint(request: SendMessageRequest):
    if not request.user_ids:
        raise HTTPException(status_code=400, detail="user_ids cannot be empty")

    results = send_direct_message(request.user_ids, request.message)

    if len(results["failed"]) == len(request.user_ids):
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send message to all users",
            headers={"X-Details": str(results["failed"])},
        )

    return results


@router.get("/summarize")
def get_summary(
    db: Session = Depends(get_db),
    last_hours: Optional[int] = Query(
        24, ge=1, description="Get replies from the last N hours (default: 24)"
    ),
):
    try:
        replies_data = get_user_replies(db=db, last_hours=last_hours)
        summary_result = summarizer.summarize(replies_data)
        slack_message = summarizer.format_for_slack(summary_result, last_hours)

        slack_response = slack_client.post_message(slack_message)

        return {
            "status": "success",
            "time_range_hours": last_hours,
            "slack_message": slack_message,
            "slack_posted": True,
            "slack_timestamp": slack_response.get("ts"),
            **summary_result,
        }

    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate summary: {str(e)}"
        )
