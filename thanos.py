import os
import subprocess
import asyncio
import time

# Ye function ab kitne bhi arguments (3 ya 4) handle kar lega
async def download_video(*args, **kwargs):
    # Arguments ko extract karna (Safety Check)
    url = args[0] if len(args) > 0 else None
    name = args[1] if len(args) > 1 else "video"
    message = args[2] if len(args) > 2 else None
    
    if not url or not message:
        print("URL or Message object missing!")
        return None

    # File name cleaning
    clean_name = "".join([c for c in name if c.isalnum() or c in (' ', '.', '_')]).strip()
    if not clean_name.endswith(".mp4"):
        clean_name += ".mp4"

    try:
        await message.edit(f"📥 **Downloading:** `{name}`\n\n⚡ *Bypass logic active...*")
    except:
        pass

    # High-quality headers to bypass 403 Forbidden
    cmd = [
        "yt-dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "--add-header", "Origin:https://web.classplusapp.com",
        "--add-header", "Referer:https://web.classplusapp.com/",
        "--no-check-certificate",
        "--concurrent-fragments", "16",
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
            try:
                await message.edit(f"✅ **Download Complete!**\n📤 *Uploading...*")
            except:
                pass
            return clean_name
        else:
            error_msg = stderr.decode().strip()
            print(f"yt-dlp error: {error_msg}")
            try:
                await message.edit(f"❌ **Download Failed!**\nError: `{error_msg[:100]}`")
            except:
                pass
            return None

    except Exception as e:
        print(f"Python error: {str(e)}")
        try:
            await message.edit(f"⚠️ **Error:** `{str(e)}`")
        except:
            pass
        return None
