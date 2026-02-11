from app.services.slack_connection import slack_client
from app.utils.logger import logger
from slack_sdk.errors import SlackApiError
from typing import List, Dict, Union


def send_direct_message(user_ids: Union[str, List[str]], message: str) -> Dict:
    if isinstance(user_ids, str):
        user_ids = [user_ids]

    results = {"successful": [], "failed": []}

    for user_id in user_ids:
        try:
            response = slack_client.conversations_open(users=[user_id])
            dm_channel = response["channel"]["id"]

            result = slack_client.chat_postMessage(channel=dm_channel, text=message)

            results["successful"].append({"user_id": user_id, "data": result.data})

        except SlackApiError as e:
            error_msg = e.response["error"]
            logger.error(f"Failed to send message to {user_id}: {error_msg}")
            results["failed"].append({"user_id": user_id, "error": error_msg})

    logger.info(
        f"Message delivery completed: "
        f"{len(results['successful'])} successful, "
        f"{len(results['failed'])} failed"
    )

    return results
