# bot/config.py
import os
from dotenv import load_dotenv

# Load environment variables from a .env file (for local testing)
# Render automatically loads environment variables into the environment
load_dotenv()

class Config:
    # Get these from https://my.telegram.org
    API_ID = int(os.environ.get("API_ID"))
    API_HASH = os.environ.get("API_HASH")

    # Get this from @BotFather
    BOT_TOKEN = os.environ.get("BOT_TOKEN")

    # Optional: Your Telegram User ID to get error logs
    OWNER_ID = int(os.environ.get("OWNER_ID", 0))
    
    # Port for Flask (Render usually sets PORT env var)
    PORT = int(os.environ.get("PORT", 5000))
