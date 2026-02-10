# Slack Daily Standup Bot

A Slack bot that collects daily standup updates from team members and generates AI-powered summaries.

## Overview

This Slack bot automates the daily standup process by:

1. Sending scheduled questions to team members via direct messages
2. Collecting their responses and storing them in a PostgreSQL database
3. Generating comprehensive summaries using an Ollama language model
4. Posting the summaries to a designated Slack channel

### Components

1. **Slack Bot Integration**: Handles incoming messages from users and sends questions
2. **FastAPI Server**: REST API endpoints for handling Slack events and manual triggers
3. **PostgreSQL Database**: Stores user replies with timestamps and metadata
4. **Ollama Integration**: Generates natural language summaries from user responses

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL database
- Ollama installed and running
- Slack workspace with bot permissions

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Psanjay-15/Slack_Bot.git
   cd slack-daily-standup-bot
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file with the following variables:

   ```
   SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
   SLACK_SIGNING_SECRET=your-slack-signing-secret
   DATABASE_URL=postgresql://user:password@localhost:5432/standup_bot
   OLLAMA_MODEL=llama3.2:1b
   SLACK_CHANNEL_ID=C012AB3CD  # Channel to post summaries
   ```

4. Initialize the database:
   ```bash
   python app/init_db.py
   ```

### Running the Application

1. Start the FastAPI server:

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. Ensure Ollama is running:

   ```bash
   ollama serve
   ```

3. Pull the required model (if not already present):
   ```bash
   ollama pull llama3.2:1b
   ```

## Usage

### Slack Integration Setup

1. Create a Slack bot in your workspace
2. Add the bot to your desired channels
3. Configure the bot's Event Subscriptions to point to your server's `/slack/connect` endpoint
4. Subscribe to `message.im` events to receive direct messages

### Collecting Responses

Team members will receive direct messages from the bot asking standup questions like:

- What did you work on yesterday?
- What are you working on today?
- Are there any blockers or dependencies?

Users can respond directly to these messages, and their responses will be stored in the database.

### API Endpoints

- `POST /slack/connect` - Handle Slack events
- `GET /slack/user-replies` - Retrieve stored user replies
- `POST /slack/send-message` - Send messages to users
- `GET /slack/summarize` - Generate and post summary

## Troubleshooting

### Common Issues

1. **Slack Events Not Receiving**
   - Verify the Event Subscription URL is correctly configured
   - Check that the server is publicly accessible
   - Ensure the bot has proper scopes (`chat:write`, `im:history`, `users:read`)

2. **Database Connection Errors**
   - Verify `DATABASE_URL` is correctly formatted
   - Ensure PostgreSQL is running and accessible
   - Check user permissions for the database

3. **Ollama Not Responding**
   - Confirm Ollama is running: `ollama serve`
   - Check if the model is pulled: `ollama list`
   - Verify the model name in `OLLAMA_MODEL`
