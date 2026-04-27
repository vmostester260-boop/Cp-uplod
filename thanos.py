import os
import subprocess
import asyncio
import time

async def download_video(url, name, message):
    # File name se characters saaf karna
    clean_name = "".join([c for c in name if c.isalnum() or c in (' ', '.', '_')]).strip()
    if not clean_name.endswith(".mp4"):
        clean_name += ".mp4"

    # Edit message to show downloading status
    await message.edit(f"📥 **Downloading:** `{name}`\n\n⚡ *Please wait...*")

    # High-quality headers to bypass 403 Forbidden
    cmd = [
        "yt-dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "--add-header", "Origin:https://web.classplusapp.com",
        "--add-header", "Referer:https://web.classplusapp.com/",
        "--no-check-certificate",
        "--concurrent-fragments", "16",
        "--fragment-retries", "10",
        "--retry-sleep", "5",
        "-o", clean_name,
        url
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            await message.edit(f"✅ **Download Complete!**\n📤 *Uploading to Telegram...*")
            return clean_name
        else:
            error_msg = stderr.decode().strip()
            if "403" in error_msg:
                await message.edit("❌ **Error 403: Forbidden**\nClassplus ne block kiya hai. Headers se kaam nahi chala.")
            else:
                await message.edit(f"❌ **Download Failed!**\nError: `{error_msg[:100]}`")
            return None

    except Exception as e:
        await message.edit(f"⚠️ **Unexpected Error:** `{str(e)}`")
        return None
