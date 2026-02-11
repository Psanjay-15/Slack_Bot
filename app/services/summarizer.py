# app/services/summarizer.py
from typing import Dict, List
from datetime import datetime
import requests
import json
from app.utils.logger import logger


class UserReplySummarizer:
    def __init__(
        self,
        model_name: str = "llama3.2:1b",
        ollama_url: str = "http://localhost:11434",
    ):
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.api_endpoint = f"{ollama_url}/api/generate"

    def _group_messages_by_user(self, replies: List[Dict]) -> Dict[str, List[Dict]]:
        user_groups = {}
        for reply in replies:
            user_name = reply["user_name"]
            if user_name not in user_groups:
                user_groups[user_name] = []
            user_groups[user_name].append(reply)
        return user_groups

    def _create_system_prompt(self) -> str:
        return """You are a project manager assistant. Your task is to analyze user messages and create a concise, professional summary for each user.

For each user, provide a brief summary covering:
1. What they worked on yesterday (if mentioned)
2. What they're working on today (if mentioned)
3. Any blockers or dependencies (if mentioned)
4. Any other relevant updates

Keep the summary concise (2-4 sentences max per user). Be factual and professional. If information is not mentioned, don't make assumptions."""

    def _format_user_messages(self, user_name: str, messages: List[Dict]) -> str:
        formatted = f"Messages from {user_name}:\n"
        for msg in sorted(messages, key=lambda x: x["timestamp"]):
            timestamp = datetime.fromisoformat(msg["timestamp"].replace("Z", "+00:00"))
            formatted += (
                f"- [{timestamp.strftime('%Y-%m-%d %H:%M')}] {msg['message']}\n"
            )
        return formatted

    def _call_ollama(self, prompt: str) -> str:
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 300},
            }

            response = requests.post(
                self.api_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60,
            )
            response.raise_for_status()

            result = response.json()
            return result.get("response", "").strip()

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {e}")
            raise Exception(f"Failed to generate summary: {str(e)}")

    def _summarize_user(self, user_name: str, messages: List[Dict]) -> str:
        system_prompt = self._create_system_prompt()
        user_messages = self._format_user_messages(user_name, messages)

        full_prompt = f"""{system_prompt}

{user_messages}

Provide a concise summary for {user_name}:"""

        summary = self._call_ollama(full_prompt)
        return summary

    def summarize(self, replies_data: Dict) -> Dict:

        try:
            if not replies_data.get("replies"):
                return {
                    "status": "success",
                    "message": "No replies to summarize",
                    "summaries": {},
                    "total_users": 0,
                    "total_messages": 0,
                }

            user_groups = self._group_messages_by_user(replies_data["replies"])

            summaries = {}
            logger.info(f"Generating summaries for {len(user_groups)} users...")

            for user_name, messages in user_groups.items():
                logger.info(f"Summarizing messages for {user_name}...")
                try:
                    summary = self._summarize_user(user_name, messages)
                    summaries[user_name] = {
                        "summary": summary,
                        "message_count": len(messages),
                    }
                except Exception as e:
                    logger.error(f"Error summarizing for {user_name}: {e}")
                    summaries[user_name] = {
                        "summary": "Error generating summary",
                        "message_count": len(messages),
                        "error": str(e),
                    }

            return {
                "status": "success",
                "summaries": summaries,
                "total_users": len(user_groups),
                "total_messages": replies_data["count"],
            }

        except Exception as e:
            logger.error(f"Error during summarization: {e}")
            raise Exception(f"Summarization failed: {str(e)}")

    def format_for_slack(self, summary_data: Dict, time_range_hours: int = 24) -> str:

        if not summary_data.get("summaries"):
            return f"📊 *Daily Summary Report* ({time_range_hours}h)\n\n_No updates to report._"

        slack_message = f"📊 *Daily Summary Report* (Last {time_range_hours} hours)\n"
        slack_message += f"_Total Users: {summary_data['total_users']} | Total Messages: {summary_data['total_messages']}_\n"
        slack_message += "─" * 50 + "\n\n"

        for user_name, data in summary_data["summaries"].items():
            slack_message += f"👤 *{user_name}*\n"
            slack_message += f"{data['summary']}\n\n"
            # slack_message += f"_Messages: {data['message_count']}_\n\n"

        slack_message += "─" * 50 + "\n"
        # slack_message += (
        #     f"_Generated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}_"
        # )

        return slack_message
