from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app.models.user_reply import UserReply
from app.database import SessionLocal
from app.utils.logger import logger


def store_user_reply(
    user_id: str, message: str, ts: str, channel_id: str | None = None
):
    db = SessionLocal()
    try:
        from slack_sdk.errors import SlackApiError
        from app.services.slack_connection import slack_client

        try:
            user_info = slack_client.users_info(user=user_id)
            if user_info.get("ok"):
                profile = user_info["user"]["profile"]
                user_name = (
                    profile.get("display_name_normalized")
                    or profile.get("real_name_normalized")
                    or user_info["user"].get("name", "Unknown")
                )
            else:
                user_name = "Unknown"
                logger.warning(
                    f"Slack users_info failed for {user_id}: {user_info.get('error')}"
                )
        except SlackApiError as e:
            logger.error(
                f"Failed to fetch user info for {user_id}: {e.response.get('error')}"
            )
            user_name = "Unknown"

        try:
            message_timestamp = datetime.utcfromtimestamp(float(ts))
        except (ValueError, TypeError):
            message_timestamp = datetime.utcnow()

        reply = UserReply(
            user_name=user_name,
            user_id=user_id,
            message=message,
            timestamp=message_timestamp,
        )
        db.add(reply)
        db.commit()
        logger.info(f"Stored reply from user {user_id} ({user_name}): '{message}'")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error storing reply for user {user_id}: {e}")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error storing reply for user {user_id}: {e}")
    finally:
        db.close()
