# --------------------------------------------------------------------------------
#  ShizuMusic © 2026
#  Developed by Bad Munda ❤️
#
#  Unauthorized copying, editing, re-uploading or removing credits
#  from this source code is strictly prohibited.
# --------------------------------------------------------------------------------

import asyncio

from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

import config
from ShizuMusic import bot, call_py
from ShizuMusic.core.call import leave_vc
from ShizuMusic.core.player import play_song
from ShizuMusic.core.queue import clear_queue, peek_current, pop_current, queue_size
from ShizuMusic.utils.db import is_user_blocked_db
from ShizuMusic.utils.formatters import short
from ShizuMusic.utils.helpers import delete_file
from ShizuMusic.utils.permissions import is_user_authorized


# ── Help menu layout ───────────────────────────────────────────────────────────
#
#   Row 1 : [ᴧᴅᴍɪɴ]  [ᴧ-ᴘʟᴀʏ]  [ɢ-ᴄᴧsᴛ]
#   Row 2 : [ʙʟ-ᴄʜᴧᴛ] [ʙʟ-ᴜsᴇʀs] [ᴘɪɴɢ]
#   Row 3 : [ᴘʟᴀʏ]   [sᴘᴇᴇᴅ]   [ɪɴғᴏ]
#   Row 4 :          [⌯ ʜᴏᴍᴇ ⌯]
#
# ──────────────────────────────────────────────────────────────────────────────

_HELP_KB = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("ᴧᴅᴍɪɴ",    callback_data="help_admin"),
        InlineKeyboardButton("ᴧ-ᴘʟᴀʏ",   callback_data="help_autoplay"),
        InlineKeyboardButton("ɢ-ᴄᴧsᴛ",   callback_data="help_gcast"),
    ],
    [
        InlineKeyboardButton("ʙʟ-ᴄʜᴧᴛ",  callback_data="help_blchat"),
        InlineKeyboardButton("ʙʟ-ᴜsᴇʀs", callback_data="help_blusers"),
        InlineKeyboardButton("ᴘɪɴɢ",     callback_data="help_ping"),
    ],
    [
        InlineKeyboardButton("ᴘʟᴀʏ",     callback_data="help_play"),
        InlineKeyboardButton("sᴘᴇᴇᴅ",    callback_data="help_speed"),
        InlineKeyboardButton("ɪɴғᴏ",     callback_data="help_info"),
    ],
    [
        InlineKeyboardButton("⌯ ʜᴏᴍᴇ ⌯", callback_data="go_back"),
    ],
])

_BACK_KB = InlineKeyboardMarkup([[
    InlineKeyboardButton("⌯ ʙᴀᴄᴋ ⌯", callback_data="show_help"),
]])

# ── Help texts ─────────────────────────────────────────────────────────────────

_HELP_TEXTS = {

    # ── Admin commands ────────────────────────────────────────────────────────
    "help_admin": (
        "<b>╭────────────────────▣</b>\n"
        "<b>│⚙️ ᴧᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /pause</b>\n"
        "<b>│   ᴘᴀᴜsᴇ ᴄᴜʀʀᴇɴᴛ ᴘʟᴀʏʙᴀᴄᴋ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /resume</b>\n"
        "<b>│   ʀᴇsᴜᴍᴇ ᴘᴀᴜsᴇᴅ ᴘʟᴀʏʙᴀᴄᴋ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /skip</b>\n"
        "<b>│   sᴋɪᴩ ᴛᴏ ɴᴇxᴛ sᴏɴɢ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /stop  ᴏʀ  /end</b>\n"
        "<b>│   sᴛᴏᴩ ᴘʟᴀʏʙᴀᴄᴋ & ʟᴇᴀᴠᴇ ᴠᴄ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /clear</b>\n"
        "<b>│   ᴄʟᴇᴀʀ ᴀʟʟ sᴏɴɢs ɪɴ ǫᴜᴇᴜᴇ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /seek</b> <code>&lt;seconds&gt;</code>\n"
        "<b>│   sᴇᴇᴋ ғᴏʀᴡᴀʀᴅ ʙʏ ɴ sᴇᴄᴏɴᴅs</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /seekback</b> <code>&lt;seconds&gt;</code>\n"
        "<b>│   sᴇᴇᴋ ʙᴀᴄᴋᴡᴀʀᴅ ʙʏ ɴ sᴇᴄᴏɴᴅs</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /reboot</b>\n"
        "<b>│   ʀᴇsᴇᴛ ᴄʜᴀᴛ sᴛᴀᴛᴇ & ʟᴇᴀᴠᴇ ᴠᴄ</b>\n"
        "<b>╰────────────────────▣</b>"
    ),

    # ── Autoplay ──────────────────────────────────────────────────────────────
    "help_autoplay": (
        "<b>╭────────────────────▣</b>\n"
        "<b>│🔁 ᴧ-ᴘʟᴀʏ ᴄᴏᴍᴍᴀɴᴅs</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /autoplay</b> <code>&lt;query&gt;</code>\n"
        "<b>│   ᴄᴏɴᴛɪɴᴜᴏᴜsʟʏ ᴘʟᴀʏ sᴏɴɢs</b>\n"
        "<b>│   ʙᴀsᴇᴅ ᴏɴ ʏᴏᴜʀ ǫᴜᴇʀʏ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /end  ᴏʀ  /stop</b>\n"
        "<b>│   sᴛᴏᴩ ᴀᴜᴛᴏᴩʟᴀʏ & ᴄʟᴇᴀʀ ǫᴜᴇᴜᴇ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│💡 ᴇxᴀᴍᴩʟᴇ :</b>\n"
        "<b>│</b> <code>/autoplay sidhu moose wala</code>\n"
        "<b>│</b> <code>/autoplay arijit singh</code>\n"
        "<b>╰────────────────────▣</b>"
    ),

    # ── Gcast / Broadcast ─────────────────────────────────────────────────────
    "help_gcast": (
        "<b>╭────────────────────▣</b>\n"
        "<b>│📢 ɢ-ᴄᴧsᴛ ᴄᴏᴍᴍᴀɴᴅs</b>\n"
        "<b>│   (ᴏᴡɴᴇʀ ᴏɴʟʏ)</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /broadcast  ᴏʀ  /gcast</b>\n"
        "<b>│   ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴍsɢ ᴏʀ ᴛʏᴩᴇ ᴛᴇxᴛ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ ғʟᴀɢs :</b>\n"
        "<b>│</b> <code>-pin</code>      <b>→ ᴩɪɴ sɪʟᴇɴᴛʟʏ ɪɴ ɢʀᴏᴜᴩs</b>\n"
        "<b>│</b> <code>-pinloud</code>  <b>→ ᴩɪɴ ᴡɪᴛʜ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ</b>\n"
        "<b>│</b> <code>-nogroup</code>  <b>→ sᴋɪᴩ ɢʀᴏᴜᴩs</b>\n"
        "<b>│</b> <code>-user</code>     <b>→ ᴀʟsᴏ sᴇɴᴅ ᴛᴏ ᴜsᴇʀs</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│💡 ᴇxᴀᴍᴩʟᴇ :</b>\n"
        "<b>│</b> <code>/gcast -pin</code>           <i>(reply)</i>\n"
        "<b>│</b> <code>/gcast -user Hello!</code>   <i>(text)</i>\n"
        "<b>│</b> <code>/gcast -nogroup -user</code> <i>(reply, users only)</i>\n"
        "<b>╰────────────────────▣</b>"
    ),

    # ── Block Chat ────────────────────────────────────────────────────────────
    "help_blchat": (
        "<b>╭────────────────────▣</b>\n"
        "<b>│🚫 ʙʟ-ᴄʜᴧᴛ ᴄᴏᴍᴍᴀɴᴅs</b>\n"
        "<b>│   (ᴏᴡɴᴇʀ ᴏɴʟʏ)</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /gblock</b>\n"
        "<b>│   ʙʟᴏᴄᴋ ᴄᴜʀʀᴇɴᴛ ɢʀᴏᴜᴩ</b>\n"
        "<b>│   ɴᴏ ᴄᴏᴍᴍᴀɴᴅs ᴡɪʟʟ ᴡᴏʀᴋ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /gblock</b> <code>-100xxxxxxx</code>\n"
        "<b>│   ʙʟᴏᴄᴋ ʙʏ ᴄʜᴀᴛ ɪᴅ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /gunblock</b>\n"
        "<b>│   ᴜɴʙʟᴏᴄᴋ ɢʀᴏᴜᴩ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /gunblock</b> <code>-100xxxxxxx</code>\n"
        "<b>│   ᴜɴʙʟᴏᴄᴋ ʙʏ ᴄʜᴀᴛ ɪᴅ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /blocklist</b>\n"
        "<b>│   sʜᴏᴡ ᴀʟʟ ʙʟᴏᴄᴋᴇᴅ ɢʀᴏᴜᴩs & ᴜsᴇʀs</b>\n"
        "<b>╰────────────────────▣</b>"
    ),

    # ── Block Users ───────────────────────────────────────────────────────────
    "help_blusers": (
        "<b>╭────────────────────▣</b>\n"
        "<b>│🚫 ʙʟ-ᴜsᴇʀs ᴄᴏᴍᴍᴀɴᴅs</b>\n"
        "<b>│   (ᴏᴡɴᴇʀ ᴏɴʟʏ)</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /ublock</b>\n"
        "<b>│   ʀᴇᴩʟʏ ᴛᴏ ᴜsᴇʀ's ᴍsɢ ᴛᴏ ʙʟᴏᴄᴋ</b>\n"
        "<b>│   ᴜsᴇʀ ᴄᴀɴɴᴏᴛ ᴜsᴇ ᴀɴʏ ᴄᴏᴍᴍᴀɴᴅ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /ublock</b> <code>123456789</code>\n"
        "<b>│   ʙʟᴏᴄᴋ ʙʏ ᴜsᴇʀ ɪᴅ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /uunblock</b>\n"
        "<b>│   ʀᴇᴩʟʏ ᴛᴏ ᴜsᴇʀ's ᴍsɢ ᴛᴏ ᴜɴʙʟᴏᴄᴋ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /uunblock</b> <code>123456789</code>\n"
        "<b>│   ᴜɴʙʟᴏᴄᴋ ʙʏ ᴜsᴇʀ ɪᴅ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /blocklist</b>\n"
        "<b>│   sʜᴏᴡ ᴀʟʟ ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs & ᴄʜᴀᴛs</b>\n"
        "<b>╰────────────────────▣</b>"
    ),

    # ── Ping ──────────────────────────────────────────────────────────────────
    "help_ping": (
        "<b>╭────────────────────▣</b>\n"
        "<b>│🏓 ᴘɪɴɢ ᴄᴏᴍᴍᴀɴᴅs</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /ping</b>\n"
        "<b>│   ʙᴏᴛ ʟᴀᴛᴇɴᴄʏ, ʀᴀᴍ, ᴄᴩᴜ</b>\n"
        "<b>│   ᴅɪsᴋ & ᴜᴩᴛɪᴍᴇ sᴛᴀᴛs</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /speedtest</b>  ᴏʀ  <b>/spt</b>\n"
        "<b>│   ɴᴇᴛᴡᴏʀᴋ sᴩᴇᴇᴅ ᴛᴇsᴛ</b>\n"
        "<b>│   (ᴏᴡɴᴇʀ ᴏɴʟʏ)</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /stats</b>\n"
        "<b>│   ғᴜʟʟ sʏsᴛᴇᴍ + ᴍᴏɴɢᴏᴅʙ sᴛᴀᴛs</b>\n"
        "<b>│   (ᴏᴡɴᴇʀ ᴏɴʟʏ)</b>\n"
        "<b>╰────────────────────▣</b>"
    ),

    # ── Play ──────────────────────────────────────────────────────────────────
    "help_play": (
        "<b>╭────────────────────▣</b>\n"
        "<b>│🎵 ᴘʟᴀʏ ᴄᴏᴍᴍᴀɴᴅs</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /play</b> <code>&lt;song name or URL&gt;</code>\n"
        "<b>│   ᴩʟᴀʏ ᴀᴜᴅɪᴏ ɪɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /vplay</b> <code>&lt;song name or URL&gt;</code>\n"
        "<b>│   ᴩʟᴀʏ ᴠɪᴅᴇᴏ ɪɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ ʀᴇᴩʟʏ ᴛᴏ ᴀᴜᴅɪᴏ/ᴠɪᴅᴇᴏ + /play</b>\n"
        "<b>│   ᴩʟᴀʏ ᴛʜᴀᴛ ᴍᴇᴅɪᴀ ᴅɪʀᴇᴄᴛʟʏ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ ʏᴏᴜᴛᴜʙᴇ ᴜʀʟs sᴜᴩᴩᴏʀᴛᴇᴅ</b>\n"
        "<b>├────────────────────▣</b>\n"
        f"<b>│❍ ᴍᴀx ᴅᴜʀᴀᴛɪᴏɴ : {config.MAX_DURATION_SECONDS // 60} ᴍɪɴᴜᴛᴇs</b>\n"
        f"<b>│❍ ǫᴜᴇᴜᴇ ʟɪᴍɪᴛ : {config.QUEUE_LIMIT} sᴏɴɢs</b>\n"
        "<b>╰────────────────────▣</b>"
    ),

    # ── Speed / Effects ───────────────────────────────────────────────────────
    "help_speed": (
        "<b>╭────────────────────▣</b>\n"
        "<b>│🎚️ sᴩᴇᴇᴅ & ᴇғғᴇᴄᴛs</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /speed</b> <code>&lt;0.25 – 4.0&gt;</code>\n"
        "<b>│   ᴄʜᴀɴɢᴇ ᴩʟᴀʏʙᴀᴄᴋ sᴩᴇᴇᴅ</b>\n"
        "<b>│   ᴇxᴀᴍᴩʟᴇ : /speed 1.5</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /speedreset</b>\n"
        "<b>│   ʀᴇsᴇᴛ sᴩᴇᴇᴅ ᴛᴏ ɴᴏʀᴍᴀʟ (1.0x)</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /bass</b> <code>&lt;1 – 20&gt;</code>\n"
        "<b>│   ʙᴏᴏsᴛ ʙᴀss ʙʏ ɴ ᴅʙ</b>\n"
        "<b>│   ᴇxᴀᴍᴩʟᴇ : /bass 10</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /bassoff</b>\n"
        "<b>│   ᴛᴜʀɴ ᴏғғ ʙᴀss ʙᴏᴏsᴛ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /effecton</b>\n"
        "<b>│   ᴀᴘᴩʟʏ ᴇғғᴇᴄᴛs ᴛᴏ ᴀʟʟ sᴏɴɢs</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /effectoff</b>\n"
        "<b>│   ᴅɪsᴀʙʟᴇ ᴀᴜᴛᴏ ᴇғғᴇᴄᴛs</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /effects</b>\n"
        "<b>│   sʜᴏᴡ ᴄᴜʀʀᴇɴᴛ ᴇғғᴇᴄᴛ sᴛᴀᴛᴜs</b>\n"
        "<b>╰────────────────────▣</b>"
    ),

    # ── Info ──────────────────────────────────────────────────────────────────
    "help_info": (
        "<b>╭────────────────────▣</b>\n"
        "<b>│ℹ️ ɪɴғᴏ ᴄᴏᴍᴍᴀɴᴅs</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /id</b>\n"
        "<b>│   ɢᴇᴛ ɪᴅs ᴏғ ᴜsᴇʀ / ᴄʜᴀᴛ / ᴍsɢ</b>\n"
        "<b>│   ᴀʟsᴏ ᴡᴏʀᴋs ᴡɪᴛʜ ʀᴇᴩʟʏ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /id</b> <code>@username</code>\n"
        "<b>│   ɢᴇᴛ ᴀɴʏ ᴜsᴇʀ's ɪᴅ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /repo</b>\n"
        "<b>│   sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ ʟɪɴᴋ</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ /stats</b>\n"
        "<b>│   ғᴜʟʟ sᴛᴀᴛs (ᴏᴡɴᴇʀ ᴏɴʟʏ)</b>\n"
        "<b>│   sʏsᴛᴇᴍ + ᴍᴏɴɢᴏᴅʙ ɪɴғᴏ</b>\n"
        "<b>╰────────────────────▣</b>"
    ),
}


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN CALLBACK HANDLER
# ══════════════════════════════════════════════════════════════════════════════

@bot.on_callback_query()
async def on_callback(client, cbq: CallbackQuery) -> None:

    chat_id = cbq.message.chat.id
    user    = cbq.from_user
    data    = cbq.data

    # ── Block check ────────────────────────────────────────────────────────────
    if user and is_user_blocked_db(user.id):
        await cbq.answer()
        return

    # ── Admin check for playback controls ─────────────────────────────────────
    if data in ("pause", "resume", "skip", "stop", "clear"):
        if not await is_user_authorized(cbq):
            await cbq.answer("❍ ᴀᴅᴍɪɴs ᴏɴʟʏ", show_alert=True)
            return

    # ── PAUSE ──────────────────────────────────────────────────────────────────
    if data == "pause":
        try:
            await call_py.pause(chat_id)
            await cbq.answer("Paused")
            await client.send_message(
                chat_id,
                f"<b>❍ sᴛʀᴇᴀᴍ ᴘᴀᴜsᴇᴅ</b>\n<b>❍ ʙʏ :</b> {user.mention}",
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            await cbq.answer("Failed To Pause", show_alert=True)

    # ── RESUME ─────────────────────────────────────────────────────────────────
    elif data == "resume":
        try:
            await call_py.resume(chat_id)
            await cbq.answer("Resumed")
            await client.send_message(
                chat_id,
                f"<b>❍ sᴛʀᴇᴀᴍ ʀᴇsᴜᴍᴇᴅ</b>\n<b>❍ ʙʏ :</b> {user.mention}",
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            await cbq.answer("Failed To Resume", show_alert=True)

    # ── SKIP ───────────────────────────────────────────────────────────────────
    elif data == "skip":
        if not queue_size(chat_id):
            await cbq.answer("Queue Is Empty", show_alert=True)
            return

        skipped = pop_current(chat_id)

        try:
            await call_py.leave_call(chat_id)
        except Exception:
            pass

        await asyncio.sleep(2)

        try:
            delete_file(skipped.get("file_path", ""))
        except Exception:
            pass

        await client.send_message(
            chat_id,
            f"<b>❍ ᴛʀᴀᴄᴋ sᴋɪᴘᴘᴇᴅ</b>\n"
            f"<b>❍ ʙʏ :</b> {user.mention}\n"
            f"<b>❍ sᴏɴɢ :</b> <code>{short(skipped['title'])}</code>",
            parse_mode=ParseMode.HTML,
        )

        nxt = peek_current(chat_id)
        if nxt:
            await cbq.answer("Playing Next")
            dm = await bot.send_message(
                chat_id,
                f"<b>❍ ɴᴇxᴛ ᴛʀᴀᴄᴋ :</b> <code>{nxt['title']}</code>",
                parse_mode=ParseMode.HTML,
            )
            await play_song(chat_id, dm, nxt)
        else:
            await cbq.answer("Queue Empty", show_alert=True)

    # ── STOP ───────────────────────────────────────────────────────────────────
    elif data == "stop":
        await leave_vc(chat_id)
        await cbq.answer("Stopped")
        await client.send_message(
            chat_id,
            f"<b>❍ ᴘʟᴀʏʙᴀᴄᴋ sᴛᴏᴘᴘᴇᴅ</b>\n<b>❍ ʙʏ :</b> {user.mention}",
            parse_mode=ParseMode.HTML,
        )

    # ── CLEAR ──────────────────────────────────────────────────────────────────
    elif data == "clear":
        clear_queue(chat_id)
        await cbq.answer("Queue Cleared")
        await cbq.message.edit_text(
            f"<b>❍ ǫᴜᴇᴜᴇ ᴄʟᴇᴀʀᴇᴅ</b>\n<b>❍ ʙʏ :</b> {user.mention}",
            parse_mode=ParseMode.HTML,
        )

    # ── NOOP ───────────────────────────────────────────────────────────────────
    elif data == "noop":
        await cbq.answer()

    # ── HELP ───────────────────────────────────────────────────────────────────
    elif data == "show_help":
        await cbq.answer()
        try:
            await cbq.message.edit_text(
                "<b>📜 ᴄʜᴏᴏsᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ :</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=_HELP_KB,
            )
        except Exception:
            await cbq.message.edit_caption(
                caption="<b>📜 ᴄʜᴏᴏsᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ :</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=_HELP_KB,
            )

    elif data == "go_back":
        await _go_back(cbq)

    elif data.startswith("help_"):
        await cbq.answer()
        text = _HELP_TEXTS.get(data)
        if text:
            try:
                await cbq.message.edit_text(
                    text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=_BACK_KB,
                )
            except Exception:
                pass


# ── Go back to start message ───────────────────────────────────────────────────

async def _go_back(cbq: CallbackQuery) -> None:
    await cbq.answer()
    uid  = cbq.from_user.id
    name = cbq.from_user.first_name or "User"

    caption = (
        "<b>╭────────────────────▣</b>\n"
        f"<b>│❍ нєу</b> <a href='tg://user?id={uid}'>{name}</a>, 🥀\n"
        f"<b>│❍ ᴛʜɪs ɪs {config.BOT_NAME} !</b>\n"
        "<b>├────────────────────▣</b>\n"
        "<b>│❍ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴜsɪᴄ ʙᴏᴛ.</b>\n"
        "<b>├────────────────────▣</b>\n"
        f"<b>│❍ 𝖯ᴏᴡᴇʀᴇᴅ 𝖡ʏ » "
        f"<a href='https://t.me/PBXCHATS'>sʜɪᴢᴜ-ᴍᴜsɪᴄ™</a></b>\n"
        "<b>╰────────────────────▣</b>"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("⛩️ ᴧᴅᴅ мᴇ ʙᴧʙʏ ⛩️",
                              url=f"{config.BOT_LINK}?startgroup=true")],
        [
            InlineKeyboardButton("🍬 sᴜᴩᴩᴏʀᴛ 🍬", url=config.SUPPORT_GROUP),
            InlineKeyboardButton("🍹 ᴜᴩᴅᴀᴛᴇ 🍹",  url=config.UPDATES_CHANNEL),
        ],
        [InlineKeyboardButton("🏩 ʜᴇʟᴩ ᴧɴᴅ ᴄᴏᴍᴍᴀɴᴅs 🏩",
                              callback_data="show_help")],
        [
            InlineKeyboardButton("🫧 ᴏᴡɴᴇʀ 🫧",
                                 url=f"tg://user?id={config.OWNER_ID}"),
            InlineKeyboardButton("🍡 sᴏᴜʀᴄᴇ 🍡",
                                 url="https://github.com/Badmunda05/ShizuMusic"),
        ],
    ])

    try:
        await cbq.message.edit_caption(
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )
    except Exception:
        try:
            await cbq.message.edit_text(
                caption,
                parse_mode=ParseMode.HTML,
                reply_markup=kb,
            )
        except Exception:
            pass
