import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

if not BOT_TOKEN or not ADMIN_CHAT_ID:
    raise RuntimeError("Проверь BOT_TOKEN и/или ADMIN_CHAT_ID in environment or .env")

ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)