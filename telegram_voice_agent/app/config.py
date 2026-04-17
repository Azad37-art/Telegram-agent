import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gemini-2.5-flash")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/embedding-001")
DOCS_DIR = os.getenv("DOCS_DIR", "data/docs")
VECTORSTORE_DIR = os.getenv("VECTORSTORE_DIR", "data/vectorstore")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN in .env")

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in .env")