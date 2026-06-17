from pyrogram import filters
from pyromod import Client, Message
from logging import getLogger
import asyncio
import os
import yt_dlp
import requests

_logger = getLogger(__name__)


def download_soundcloud(url):
    base_name = f"track_{os.urandom(4).hex()}"

    ydl_opts = {
        'outtmpl': f'{base_name}.%(ext)s',
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        # 'proxy': 'http://127.0.0.1:10808',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        audio_filepath = ydl.prepare_filename(info)

    title = info.get('title', 'Unknown Title')
    performer = info.get('uploader', 'Unknown Artist')
    duration = int(info.get('duration', 0))
    thumb_url = info.get('thumbnail')

    thumb_filepath = None
    if thumb_url:
        try:
            response = requests.get(thumb_url, timeout=10)
            if response.status_code == 200:
                thumb_filepath = f"{base_name}_cover.jpg"
                with open(thumb_filepath, 'wb') as f:
                    f.write(response.content)
        except Exception as e:
            print(f"Cover download failed: {e}")

    # برگرداندن یک پکیج کامل از اطلاعات به ربات تلگرام
    return {
        "audio_path": audio_filepath,
        "thumb_path": thumb_filepath,
        "title": title,
        "performer": performer,
        "duration": duration
    }

@Client.on_message(filters.command('start') & filters.private)
async def handle_start(client, message):
    await message.reply_text('سلام! خوش آمدید. 🎵\nلطفاً لینک آهنگ مورد نظرتان از ساندکلود را بفرستید تا آن را دانلود کنم.')


@Client.on_message(filters.regex(r'soundcloud\.com') & filters.private)
async def handle_soundcloud_link(client, message):
    url = message.text.strip()
    status_msg = await message.reply_text("⏳ در حال دریافت اطلاعات آهنگ و کاور...")

    data = None
    try:
        data = await asyncio.to_thread(download_soundcloud, url)

        audio_path = data.get("audio_path")
        if not audio_path or not os.path.exists(audio_path):
            raise Exception("فایل صوتی یافت نشد.")

        await status_msg.edit_text("📤 در حال آپلود آهنگ در تلگرام... 🎵")

        await message.reply_audio(
            audio=audio_path,
            thumb=data.get("thumb_path"),
            title=data.get("title"),
            performer=data.get("performer"),
            duration=data.get("duration"),
            caption=f"🎧 **{data.get('title')}**\n👤 {data.get('performer')}\n\n✅ دانلود شده توسط ربات ما"
        )

    except Exception as e:
        print(f"Error: {e}")
        await message.reply_text("❌ مشکلی در دانلود پیش آمد. مطمئن شوید لینک عمومی است.")

    finally:
        await status_msg.delete()

        if data:
            if data.get("audio_path") and os.path.exists(data.get("audio_path")):
                os.remove(data.get("audio_path"))
            if data.get("thumb_path") and os.path.exists(data.get("thumb_path")):
                os.remove(data.get("thumb_path"))

@Client.on_message(filters.command('start') & filters.private)
async def handle_start(client, message):
    await message.reply_text('سلام! 🎵\nلینک آهنگ از ساندکلود رو بفرست تا با کاور اصلی برات دانلودش کنم.')