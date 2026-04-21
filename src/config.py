import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing in .env")

ADMIN_ID = os.getenv("ADMIN_ID")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "somly_ai")

_keys = os.getenv("GROQ_API_KEYS", "")
GROQ_API_KEYS = [k.strip() for k in _keys.split(",") if k.strip()]
if not GROQ_API_KEYS:
    raise ValueError("GROQ_API_KEYS is missing in .env")

GROQ_MODEL = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
