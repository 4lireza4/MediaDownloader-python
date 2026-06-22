from pyrogram import filters
from pyromod import Client, Message
from logging import getLogger
import asyncio
import json
import os
import config

_logger = getLogger(__name__)

USERS_FILE = "users.json"


def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return []


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)


def add_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        save_users(users)


@Client.on_message(filters.command('start') & filters.private)
async def handle_start(client, message):
    add_user(message.from_user.id)
    await message.reply_text(
        'سلام! خوش آمدید.\n'
        'لطفاً لینک مد نظرتان را بفرستید تا دانلود کنم.\n\n'
        '🎵 SoundCloud | 📸 Instagram'
    )


@Client.on_message(filters.command('broadcast') & filters.private)
async def handle_broadcast(client, message):
    if message.from_user.id not in config.admin_ids:
        await message.reply_text("❌ شما ادمین نیستید.")
        return

    text = message.text.replace("/broadcast", "", 1).strip()
    if not text:
        await message.reply_text("❌ متن پیام را وارد کنید.\nمثال: /broadcast سلام دوستان")
        return

    users = load_users()
    if not users:
        await message.reply_text("❌ هیچ کاربری یافت نشد.")
        return

    status_msg = await message.reply_text(f"⏳ در حال ارسال به {len(users)} کاربر...")

    success = 0
    failed = 0
    for user_id in users[:]:
        try:
            await client.send_message(user_id, text)
            success += 1
            await asyncio.sleep(0.5)
        except Exception as e:
            failed += 1
            users.remove(user_id)
            _logger.warning(f"Failed to send to {user_id}: {e}")

    save_users(users)
    await status_msg.edit_text(
        f"✅ ارسال شد!\n"
        f"📨 موفق: {success}\n"
        f"❌ ناموفق: {failed}"
    )
