from dotenv import load_dotenv
import os

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
DATABASE_URL = os.getenv("DATABASE_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
CHANNEL_ID = os.getenv("CHANNEL_ID")
