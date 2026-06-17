# --------------------------------------------------------------------------------
#  ShizuMusic © 2026
#  Developed by Bad Munda ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

import logging
from typing import Optional

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

import config

logger = logging.getLogger(__name__)

# ── Client ─────────────────────────────────────────────────────────────────────
_client: Optional[MongoClient] = None
_db = None


def start_mongo() -> bool:
    global _client, _db

    if not config.MONGO_DB_URL:
        logger.warning("MONGO_DB_URL not set — database features disabled.")
        return False

    try:
        _client = MongoClient(config.MONGO_DB_URL, serverSelectionTimeoutMS=5000)
        _client.admin.command("ping")
        _db = _client["ShizuMusic"]
        logger.info("✅ MongoDB connected successfully.")
        return True

    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        _client = None
        _db = None
        return False

    except Exception as e:
        logger.error(f"❌ MongoDB unexpected error: {e}")
        _client = None
        _db = None
        return False


def get_db():
    return _db


def is_connected() -> bool:
    return _db is not None


def get_mongo_client() -> Optional[MongoClient]:
    """Return the raw MongoClient (used for dbstats in /stats command)."""
    return _client


# ── Collections ────────────────────────────────────────────────────────────────

def _col(name: str):
    if _db is None:
        return None
    return _db[name]


# ── Served Chats ───────────────────────────────────────────────────────────────

def add_served_chat(chat_id: int) -> None:
    col = _col("served_chats")
    if col is None:
        return
    try:
        col.update_one({"_id": chat_id}, {"$set": {"_id": chat_id}}, upsert=True)
    except Exception as e:
        logger.error(f"[DB] add_served_chat: {e}")


def get_served_chats() -> list:
    col = _col("served_chats")
    if col is None:
        return []
    try:
        return [doc["_id"] for doc in col.find({}, {"_id": 1})]
    except Exception as e:
        logger.error(f"[DB] get_served_chats: {e}")
        return []


def get_served_chats_count() -> int:
    col = _col("served_chats")
    if col is None:
        return 0
    try:
        return col.count_documents({})
    except Exception as e:
        logger.error(f"[DB] get_served_chats_count: {e}")
        return 0


def remove_served_chat(chat_id: int) -> None:
    col = _col("served_chats")
    if col is None:
        return
    try:
        col.delete_one({"_id": chat_id})
    except Exception as e:
        logger.error(f"[DB] remove_served_chat: {e}")


# ── Served Users ───────────────────────────────────────────────────────────────

def add_served_user(user_id: int) -> None:
    col = _col("served_users")
    if col is None:
        return
    try:
        col.update_one({"_id": user_id}, {"$set": {"_id": user_id}}, upsert=True)
    except Exception as e:
        logger.error(f"[DB] add_served_user: {e}")


def get_served_users() -> list:
    col = _col("served_users")
    if col is None:
        return []
    try:
        return [doc["_id"] for doc in col.find({}, {"_id": 1})]
    except Exception as e:
        logger.error(f"[DB] get_served_users: {e}")
        return []


def get_served_users_count() -> int:
    col = _col("served_users")
    if col is None:
        return 0
    try:
        return col.count_documents({})
    except Exception as e:
        logger.error(f"[DB] get_served_users_count: {e}")
        return 0


# ── Blocked Chats (ban) ────────────────────────────────────────────────────────

def ban_chat(chat_id: int) -> None:
    col = _col("banned_chats")
    if col is None:
        return
    try:
        col.update_one({"_id": chat_id}, {"$set": {"_id": chat_id}}, upsert=True)
    except Exception as e:
        logger.error(f"[DB] ban_chat: {e}")


def unban_chat(chat_id: int) -> None:
    col = _col("banned_chats")
    if col is None:
        return
    try:
        col.delete_one({"_id": chat_id})
    except Exception as e:
        logger.error(f"[DB] unban_chat: {e}")


def is_chat_banned(chat_id: int) -> bool:
    col = _col("banned_chats")
    if col is None:
        return False
    try:
        return col.find_one({"_id": chat_id}) is not None
    except Exception:
        return False


def get_banned_chats() -> list:
    col = _col("banned_chats")
    if col is None:
        return []
    try:
        return [doc["_id"] for doc in col.find({}, {"_id": 1})]
    except Exception:
        return []


def get_banned_chats_count() -> int:
    col = _col("banned_chats")
    if col is None:
        return 0
    try:
        return col.count_documents({})
    except Exception:
        return 0


# ── Assistant Joined Chats ─────────────────────────────────────────────────────

def mark_assistant_joined(chat_id: int) -> None:
    col = _col("assistant_chats")
    if col is None:
        return
    try:
        col.update_one({"_id": chat_id}, {"$set": {"_id": chat_id}}, upsert=True)
    except Exception as e:
        logger.error(f"[DB] mark_assistant_joined: {e}")


def is_assistant_joined(chat_id: int) -> bool:
    col = _col("assistant_chats")
    if col is None:
        return False
    try:
        return col.find_one({"_id": chat_id}) is not None
    except Exception:
        return False


# ── Play Stats ─────────────────────────────────────────────────────────────────

def increment_play_count(chat_id: int) -> None:
    col = _col("play_stats")
    if col is None:
        return
    try:
        col.update_one(
            {"_id": chat_id},
            {"$inc": {"count": 1}},
            upsert=True,
        )
    except Exception as e:
        logger.error(f"[DB] increment_play_count: {e}")


def get_total_plays() -> int:
    col = _col("play_stats")
    if col is None:
        return 0
    try:
        result = col.aggregate([{"$group": {"_id": None, "total": {"$sum": "$count"}}}])
        for r in result:
            return r.get("total", 0)
        return 0
    except Exception:
        return 0


# ── Broadcast Chats ────────────────────────────────────────────────────────────

def add_broadcast_chat(chat_id: int, chat_type: str) -> None:
    col = _col("broadcast")
    if col is None:
        return
    try:
        col.update_one(
            {"_id": int(chat_id)},
            {
                "$set": {
                    "_id":     int(chat_id),
                    "chat_id": int(chat_id),
                    "type":    chat_type,
                }
            },
            upsert=True,
        )
    except Exception as e:
        logger.error(f"[DB] add_broadcast_chat: {e}")


def get_broadcast_chats() -> list:
    col = _col("broadcast")
    if col is None:
        return []
    try:
        return list(col.find({}, {"_id": 1, "chat_id": 1, "type": 1}))
    except Exception as e:
        logger.error(f"[DB] get_broadcast_chats: {e}")
        return []


def get_broadcast_count() -> dict:
    col = _col("broadcast")
    if col is None:
        return {"total": 0, "private": 0, "groups": 0}
    try:
        total   = col.count_documents({})
        private = col.count_documents({"type": "private"})
        groups  = col.count_documents({"type": "group"})
        return {"total": total, "private": private, "groups": groups}
    except Exception as e:
        logger.error(f"[DB] get_broadcast_count: {e}")
        return {"total": 0, "private": 0, "groups": 0}


def remove_broadcast_chat(chat_id: int) -> None:
    col = _col("broadcast")
    if col is None:
        return
    try:
        col.delete_one({"_id": int(chat_id)})
    except Exception as e:
        logger.error(f"[DB] remove_broadcast_chat: {e}")


# ── Blocked Groups (gblock) ────────────────────────────────────────────────────

def is_group_blocked(chat_id: int) -> bool:
    col = _col("blocked_groups")
    if col is None:
        return False
    try:
        return col.find_one({"_id": chat_id}) is not None
    except Exception:
        return False


def block_group(chat_id: int) -> None:
    col = _col("blocked_groups")
    if col is None:
        return
    try:
        col.update_one({"_id": chat_id}, {"$set": {"_id": chat_id}}, upsert=True)
    except Exception as e:
        logger.error(f"[DB] block_group: {e}")


def unblock_group(chat_id: int) -> None:
    col = _col("blocked_groups")
    if col is None:
        return
    try:
        col.delete_one({"_id": chat_id})
    except Exception as e:
        logger.error(f"[DB] unblock_group: {e}")


def get_blocked_groups() -> list:
    col = _col("blocked_groups")
    if col is None:
        return []
    try:
        return [doc["_id"] for doc in col.find({}, {"_id": 1})]
    except Exception:
        return []


# ── Blocked Users (ublock) ─────────────────────────────────────────────────────

def is_user_blocked_db(user_id: int) -> bool:
    col = _col("blocked_users")
    if col is None:
        return False
    try:
        return col.find_one({"_id": user_id}) is not None
    except Exception:
        return False


def block_user(user_id: int) -> None:
    col = _col("blocked_users")
    if col is None:
        return
    try:
        col.update_one({"_id": user_id}, {"$set": {"_id": user_id}}, upsert=True)
    except Exception as e:
        logger.error(f"[DB] block_user: {e}")


def unblock_user(user_id: int) -> None:
    col = _col("blocked_users")
    if col is None:
        return
    try:
        col.delete_one({"_id": user_id})
    except Exception as e:
        logger.error(f"[DB] unblock_user: {e}")


def get_blocked_users() -> list:
    col = _col("blocked_users")
    if col is None:
        return []
    try:
        return [doc["_id"] for doc in col.find({}, {"_id": 1})]
    except Exception:
        return []


# ── Chat Effects (speed / bass / effects_on) ───────────────────────────────────

def save_chat_effects(chat_id: int, speed: float, bass: int, enabled: bool) -> None:
    """Save current effect settings for a chat to MongoDB."""
    col = _col("chat_effects")
    if col is None:
        return
    try:
        col.update_one(
            {"_id": chat_id},
            {"$set": {
                "_id":     chat_id,
                "speed":   speed,
                "bass":    bass,
                "enabled": enabled,
            }},
            upsert=True,
        )
    except Exception as e:
        logger.error(f"[DB] save_chat_effects: {e}")


def load_chat_effects(chat_id: int) -> dict:
    """Load effect settings for a chat. Returns defaults if not found."""
    col = _col("chat_effects")
    if col is None:
        return {"speed": 1.0, "bass": 0, "enabled": False}
    try:
        doc = col.find_one({"_id": chat_id})
        if doc:
            return {
                "speed":   doc.get("speed",   1.0),
                "bass":    doc.get("bass",     0),
                "enabled": doc.get("enabled",  False),
            }
    except Exception as e:
        logger.error(f"[DB] load_chat_effects: {e}")
    return {"speed": 1.0, "bass": 0, "enabled": False}


def delete_chat_effects(chat_id: int) -> None:
    """Remove effect settings for a chat."""
    col = _col("chat_effects")
    if col is None:
        return
    try:
        col.delete_one({"_id": chat_id})
    except Exception as e:
        logger.error(f"[DB] delete_chat_effects: {e}")
               
# ── Moderation Filter Settings (NSFW / Bad-word / Link / Document) ───────────
# All four filters live as fields on the same per-chat document so a single
# read/write covers the whole moderation panel. Each defaults to True (ON)
# when unset, so a brand-new group is protected from day one.
#
#   { "_id": chat_id, "nsfw": bool, "badword": bool, "link": bool, "document": bool }
#
# "enabled" is kept in sync with "nsfw" for backward compatibility with any
# older code/data that still reads the original field name directly.

DEFAULT_MOD_SETTINGS = {
    "nsfw":     True,
    "badword":  True,
    "link":     True,
    "document": True,
}


def get_mod_settings(chat_id: int) -> dict:
    """Return all moderation toggles for a chat (defaults True if unset)."""
    col = _col("nsfw_settings")
    if col is None:
        return DEFAULT_MOD_SETTINGS.copy()
    try:
        doc = col.find_one({"_id": chat_id})
        if doc is None:
            return DEFAULT_MOD_SETTINGS.copy()
        settings = DEFAULT_MOD_SETTINGS.copy()
        for key in settings:
            if key in doc:
                settings[key] = doc[key]
            elif key == "nsfw" and "enabled" in doc:
                settings[key] = doc["enabled"]   # legacy field fallback
        return settings
    except Exception as e:
        logger.error(f"[DB] get_mod_settings: {e}")
        return DEFAULT_MOD_SETTINGS.copy()


def set_mod_setting(chat_id: int, key: str, value: bool) -> None:
    if key not in DEFAULT_MOD_SETTINGS:
        return
    col = _col("nsfw_settings")
    if col is None:
        return
    try:
        update = {key: value}
        if key == "nsfw":
            update["enabled"] = value   # keep legacy field in sync
        col.update_one({"_id": chat_id}, {"$set": update}, upsert=True)
    except Exception as e:
        logger.error(f"[DB] set_mod_setting: {e}")


def is_nsfw_enabled(chat_id: int) -> bool:
    return get_mod_settings(chat_id)["nsfw"]


def set_nsfw_enabled(chat_id: int, enabled: bool) -> None:
    set_mod_setting(chat_id, "nsfw", enabled)


def is_badword_enabled(chat_id: int) -> bool:
    return get_mod_settings(chat_id)["badword"]


def set_badword_enabled(chat_id: int, enabled: bool) -> None:
    set_mod_setting(chat_id, "badword", enabled)


def is_link_filter_enabled(chat_id: int) -> bool:
    return get_mod_settings(chat_id)["link"]


def set_link_filter_enabled(chat_id: int, enabled: bool) -> None:
    set_mod_setting(chat_id, "link", enabled)


def is_document_filter_enabled(chat_id: int) -> bool:
    return get_mod_settings(chat_id)["document"]


def set_document_filter_enabled(chat_id: int, enabled: bool) -> None:
    set_mod_setting(chat_id, "document", enabled)


# ── Moderation Approved Users (per-chat whitelist) ───────────────────────────
# An approved user's media/text bypasses ALL moderation filters above
# (NSFW, bad words, links, blocked files) — not just NSFW.

def approve_nsfw_user(chat_id: int, user_id: int) -> None:
    col = _col("nsfw_approved")
    if col is None:
        return
    try:
        col.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {"chat_id": chat_id, "user_id": user_id}},
            upsert=True,
        )
    except Exception as e:
        logger.error(f"[DB] approve_nsfw_user: {e}")


def disapprove_nsfw_user(chat_id: int, user_id: int) -> None:
    col = _col("nsfw_approved")
    if col is None:
        return
    try:
        col.delete_one({"chat_id": chat_id, "user_id": user_id})
    except Exception as e:
        logger.error(f"[DB] disapprove_nsfw_user: {e}")


def is_nsfw_approved(chat_id: int, user_id: int) -> bool:
    col = _col("nsfw_approved")
    if col is None:
        return False
    try:
        return col.find_one({"chat_id": chat_id, "user_id": user_id}) is not None
    except Exception:
        return False


def get_nsfw_approved_users(chat_id: int) -> list:
    col = _col("nsfw_approved")
    if col is None:
        return []
    try:
        return [doc["user_id"] for doc in col.find({"chat_id": chat_id}, {"user_id": 1})]
    except Exception as e:
        logger.error(f"[DB] get_nsfw_approved_users: {e}")
        return []
