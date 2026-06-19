"""
config.py — All environment variables in one place.
Copy sample.env → .env and fill in your values.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Required ──────────────────────────────────────────────────────────────────
API_ID          = int(os.environ["API_ID"])
API_HASH        = os.environ["API_HASH"]
BOT_TOKEN       = os.environ["BOT_TOKEN"]
STRING_SESSION  = os.environ["STRING_SESSION"]
MONGO_DB_URL    = os.environ["MONGO_DB_URL"]
OWNER_ID        = int(os.environ["OWNER_ID"])

# ── Optional ──────────────────────────────────────────────────────────────────
BOT_NAME         = os.getenv("BOT_NAME", "Shizu Music")
BOT_LINK         = os.getenv("BOT_LINK", "https://t.me/ShizuMusicBot")
UPDATES_CHANNEL  = os.getenv("UPDATES_CHANNEL", "https://t.me/PBX_UPDATE")
SUPPORT_GROUP    = os.getenv("SUPPORT_GROUP", "https://t.me/PBXCHATS")
LOGGER_ID        = int(os.getenv("LOGGER_ID", "0"))
PING_IMG_URL     = os.getenv("PING_IMG_URL", "https://files.catbox.moe/ddzvc0.jpg",)
SESSION_NAME     = os.getenv("SESSION_NAME", "ShizuMusic")
PORT             = int(os.getenv("PORT", 10000))

#── Start ───────────────────────────────────────────────────────────────────────
START_ANIMATIONS = [
    "https://files.catbox.moe/00gg2f.mp4",
    "https://files.catbox.moe/00gg2f.mp4",
    "https://files.catbox.moe/00gg2f.mp4",
    "https://files.catbox.moe/00gg2f.mp4",
    "https://files.catbox.moe/00gg2f.mp4",
    "https://files.catbox.moe/00gg2f.mp4",
    "https://files.catbox.moe/00gg2f.mp4",
]

# ── Limits ────────────────────────────────────────────────────────────────────
MAX_DURATION_SECONDS = 1800   # 30 minutes
QUEUE_LIMIT          = 20
COOLDOWN             = 10     # seconds between /play per chat
