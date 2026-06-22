from pyrogram import filters
from pyromod import Client, Message
from logging import getLogger
import asyncio
import os
import re
import yt_dlp
import requests

_logger = getLogger(__name__)


def download_instagram(url):
    base_name = f"ig_{os.urandom(4).hex()}"

    ydl_opts = {
        'outtmpl': f'{base_name}.%(ext)s',
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filepath = ydl.prepare_filename(info)

    title = info.get('title', '')
    description = info.get('description', '')
    thumb_url = info.get('thumbnail')
    duration = int(info.get('duration', 0))
    ext = info.get('ext', '')

    thumb_filepath = None
    if thumb_url:
        try:
            response = requests.get(thumb_url, timeout=10)
            if response.status_code == 200:
                thumb_filepath = f"{base_name}_thumb.jpg"
                with open(thumb_filepath, 'wb') as f:
                    f.write(response.content)
        except Exception as e:
            print(f"Thumbnail download failed: {e}")

    return {
        "filepath": filepath,
        "thumb_path": thumb_filepath,
        "title": title,
        "description": description,
        "duration": duration,
        "ext": ext
    }


@Client.on_message(filters.regex(r'(?:www\.)?(?:instagram\.com|instagr\.am)') & (filters.private | filters.group))
async def handle_instagram_link(client, message):
    url_match = re.search(r'https?://[^\s]+(?:instagram\.com|instagr\.am)[^\s]*', message.text)
    if not url_match:
        await message.reply_text("❌ لینک اینستاگرام یافت نشد.")
        return
    url = url_match.group(0)
    status_msg = await message.reply_text("⏳ در حال دریافت و دانلود از اینستاگرام...")

    data = None
    try:
        data = await asyncio.to_thread(download_instagram, url)

        filepath = data.get("filepath")
        if not filepath or not os.path.exists(filepath):
            raise Exception("فایل یافت نشد.")

        ext = data.get("ext", "")
        caption = f"📸 {data.get('title') or data.get('description') or 'Instagram Post'}"

        await status_msg.edit_text("📤 در حال آپلود...")

        if ext in ("mp4", "webm", "mkv"):
            await message.reply_video(
                video=filepath,
                thumb=data.get("thumb_path"),
                caption=caption,
                duration=data.get("duration"),
            )
        else:
            await message.reply_photo(
                photo=filepath,
                thumb=data.get("thumb_path"),
                caption=caption,
            )

    except Exception as e:
        print(f"Error: {e}")
        await message.reply_text("❌ مشکلی در دانلود پیش آمد. مطمئن شوید لینک صحیح است.")

    finally:
        await status_msg.delete()

        if data:
            if data.get("filepath") and os.path.exists(data.get("filepath")):
                os.remove(data.get("filepath"))
            if data.get("thumb_path") and os.path.exists(data.get("thumb_path")):
                os.remove(data.get("thumb_path"))
