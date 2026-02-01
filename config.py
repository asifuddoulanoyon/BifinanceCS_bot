import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set")

OWNER_ID = int(os.getenv("OWNER_ID", "0"))
AGENT_IDS = []  # will load from DB later
