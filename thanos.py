import os, time, subprocess, asyncio, requests
from pyrogram import Client
from pyrogram.types import Message
from utils import progress_bar

def get_duration(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return float(result.stdout)

async def download_video(url, name, m, bot):
    # File name clean karna
    if not name.endswith(".mp4"): name = f"{name}.mp4"
    clean_name = "".join([c for c in name if c.isalpha() or c.isdigit() or c in ' .-_']).strip()
    
    # --- CLASSPLUS HEADERS ADDED HERE ---
    cmd = [
        "yt-dlp", "-f", "best",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "--add-header", "Referer:https://www.classplusapp.com/",
        "--no-check-certificate", "--external-downloader", "aria2c",
        "--downloader-args", "aria2c:-x 16 -j 32",
        "-o", clean_name, url
    ]
    
    process = subprocess.run(cmd)
    if process.returncode == 0:
        return clean_name if os.path.exists(clean_name) else None
    return None

async def send_vid(bot, m, filename, name):
    try:
        reply = await m.reply_text(f"📤 **Uploading:** `{name}`")
        dur = int(get_duration(filename))
        start_time = time.time()
        
        # Thumbnail generate karna
        thumb = f"{filename}.jpg"
        subprocess.run(f'ffmpeg -i "{filename}" -ss 00:00:05 -vframes 1 -y "{thumb}"', shell=True)

        await bot.send_video(
            chat_id=m.chat.id,
            video=filename,
            caption=f"**🎥 Name:** `{name}`",
            supports_streaming=True,
            duration=dur,
            thumb=thumb if os.path.exists(thumb) else None,
            progress=progress_bar,
            progress_args=(reply, start_time)
        )
        await reply.delete()
        if os.path.exists(filename): os.remove(filename)
        if os.path.exists(thumb): os.remove(thumb)
    except Exception as e:
        await m.reply_text(f"❌ Upload Error: {e}")
