# --------------------------------------------------------------------------------
#  ShizuMusic © 2026
#  Developed by Bad Munda ❤️
# --------------------------------------------------------------------------------

import asyncio

from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.errors import (
    ChatAdminRequired,
    ChatWriteForbidden,
    FloodWait,
    UserIsBlocked,
)
from pyrogram.types import Message

import config
from ShizuMusic import bot


# ─────────────────────────────────────────────
# AUTO SAVE CHATS
# ─────────────────────────────────────────────

@bot.on_message(
    filters.private
    | filters.group
    | filters.supergroup
)
async def save_chat(_, message: Message):

    try:

        from ShizuMusic.database import (
            add_broadcast_chat,
        )

        chat = message.chat

        if chat.type in (
            ChatType.GROUP,
            ChatType.SUPERGROUP,
        ):

            add_broadcast_chat(
                int(chat.id),
                "group",
            )

        elif chat.type == ChatType.PRIVATE:

            add_broadcast_chat(
                int(chat.id),
                "private",
            )

    except Exception:
        pass


# ─────────────────────────────────────────────
# BROADCAST
# ─────────────────────────────────────────────

@bot.on_message(
    filters.command("broadcast")
    & filters.user(config.OWNER_ID)
)
async def broadcast_cmd(_, message: Message):

    if not message.reply_to_message:

        await message.reply(
            "<b>❍ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ</b>\n"
            "<b>❍ ᴛʜᴇɴ ᴜsᴇ /broadcast</b>",
            parse_mode=ParseMode.HTML,
        )

        return

    bm = message.reply_to_message

    try:

        from ShizuMusic.database import (
            get_broadcast_chats,
            get_broadcast_count,
            remove_broadcast_chat,
        )

    except Exception as e:

        await message.reply(
            f"<b>❍ ᴅʙ ᴇʀʀᴏʀ :</b>\n"
            f"<code>{e}</code>",
            parse_mode=ParseMode.HTML,
        )

        return

    counts = get_broadcast_count()

    all_chats = get_broadcast_chats()

    if not all_chats:

        await message.reply(
            "<b>❍ ɴᴏ ᴄʜᴀᴛs ғᴏᴜɴᴅ</b>",
            parse_mode=ParseMode.HTML,
        )

        return

    processing = await message.reply(
        "<b>❍ ʙʀᴏᴀᴅᴄᴀsᴛ sᴛᴀʀᴛᴇᴅ</b>\n\n"
        f"<b>❍ ᴛᴏᴛᴀʟ :</b> <code>{counts['total']}</code>\n"
        f"<b>❍ ɢʀᴏᴜᴩs :</b> <code>{counts['groups']}</code>\n"
        f"<b>❍ ᴜsᴇʀs :</b> <code>{counts['private']}</code>",
        parse_mode=ParseMode.HTML,
    )

    success_groups = 0
    success_users = 0
    pinned = 0
    failed = 0

    for doc in all_chats:

        cid = int(doc["chat_id"])

        chat_type = doc.get(
            "type",
            "group",
        )

        try:

            sent = await bot.forward_messages(
                cid,
                bm.chat.id,
                bm.id,
            )

            if chat_type == "group":

                success_groups += 1

                try:

                    await bot.pin_chat_message(
                        cid,
                        sent.id,
                        disable_notification=True,
                    )

                    pinned += 1

                except ChatAdminRequired:
                    pass

                except Exception:
                    pass

            else:

                success_users += 1

        except FloodWait as e:

            await asyncio.sleep(
                e.value + 2
            )

            try:

                await bot.forward_messages(
                    cid,
                    bm.chat.id,
                    bm.id,
                )

                if chat_type == "group":
                    success_groups += 1
                else:
                    success_users += 1

            except Exception:
                failed += 1

        except (
            UserIsBlocked,
            ChatWriteForbidden,
        ):

            remove_broadcast_chat(cid)

            failed += 1

        except Exception:

            failed += 1

        await asyncio.sleep(0.4)

    await processing.edit_text(
        "<b>❍ ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ✅</b>\n\n"
        f"<b>❍ ɢʀᴏᴜᴩs :</b> <code>{success_groups}</code>\n"
        f"<b>❍ ᴜsᴇʀs :</b> <code>{success_users}</code>\n"
        f"<b>❍ ᴘɪɴɴᴇᴅ :</b> <code>{pinned}</code>\n"
        f"<b>❍ ғᴀɪʟᴇᴅ :</b> <code>{failed}</code>",
        parse_mode=ParseMode.HTML,
    )
