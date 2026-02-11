from fastapi import Request, HTTPException
from slack_sdk import WebClient
from app.config import SLACK_BOT_TOKEN
from app.services.user_reply_service import store_user_reply
from app.utils.logger import logger
import ssl

ssl_context = ssl._create_unverified_context()

slack_client = WebClient(token=SLACK_BOT_TOKEN, ssl=ssl_context)


async def handle_slack_connection(request: Request):
    try:
        payload = await request.json()

        if payload.get("type") == "url_verification":
            return {"challenge": payload.get("challenge")}

        if payload.get("type") == "event_callback":
            event = payload.get("event", {})
            event_type = event.get("type")

            if event_type == "message":
                if event.get("bot_id") or event.get("subtype"):
                    return {"status": "ignored"}

                if event.get("channel_type") == "im":
                    user_id = event["user"]
                    text = event.get("text", "").strip()
                    ts = event["ts"]
                    channel_id = event["channel"]

                    if text:
                        store_user_reply(
                            user_id=user_id,
                            message=text,
                            ts=ts,
                            channel_id=channel_id,
                        )

            return {"status": "ok"}
        return {"status": "ignored"}

    except Exception as e:
        logger.exception("Slack handler failed")
        raise HTTPException(status_code=500, detail=str(e))
