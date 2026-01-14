"""Configuration module for the bot."""
import os
from dotenv import load_dotenv

load_dotenv()

# Bot settings
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Validate required settings
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")
