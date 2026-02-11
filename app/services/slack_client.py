import os
import requests
from typing import Dict
from app.utils.logger import logger


class SlackClient:
    def __init__(self):
        self.bot_token = os.getenv("SLACK_BOT_TOKEN")
        self.channel_id = os.getenv("SLACK_CHANNEL_ID")
        self.api_url = "https://slack.com/api/chat.postMessage"

        if not self.bot_token:
            raise ValueError("SLACK_BOT_TOKEN environment variable is not set")
        if not self.channel_id:
            raise ValueError("SLACK_CHANNEL_ID environment variable is not set")

    def post_message(self, text: str) -> Dict:

        try:
            headers = {
                "Authorization": f"Bearer {self.bot_token}",
                "Content-Type": "application/json",
            }

            payload = {
                "channel": self.channel_id,
                "text": text,
                "mrkdwn": True,
            }

            logger.info(f"Posting message to Slack channel: {self.channel_id}")
            response = requests.post(
                self.api_url, json=payload, headers=headers, timeout=30
            )
            response.raise_for_status()

            result = response.json()

            if not result.get("ok"):
                error_msg = result.get("error", "Unknown error")
                logger.error(f"Slack API error: {error_msg}")
                raise Exception(f"Slack API error: {error_msg}")

            logger.info("Message posted to Slack successfully")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Error posting to Slack: {e}")
            raise Exception(f"Failed to post to Slack: {str(e)}")
