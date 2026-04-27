import os
import asyncio
import thanos
from pyrogram import Client, filters
from pyrogram.types import Message

# --- CONFIGURATION ---
# Inhe aap variables mein set kar sakte hain ya environment se fetch kar sakte hain
API_ID = int(os.environ.get("API_ID", "12345")) # Apna API ID dalo
API_HASH = os.environ.get("API_HASH", "your_hash") # Apna API Hash dalo
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_token") # Apna Bot Token dalo

bot = Client("UgDev_Uploader", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- STOP COMMAND ---
@bot.on_message(filters.command("stop") & filters.private)
async def stop_handler(client, message):
    thanos.STOP_PROCESS = True
    await message.reply_text("⛔ **Stop Signal Sent!**\nAbhi wala process ruk jayega aur baki queue cancel ho jayegi.")

# --- START COMMAND ---
@bot.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    await message.reply_text("👋 **Welcome to UGDEV Uploader!**\n\nBhai, link bhejo format mein: `Name | Link` ya sirf link.")

# --- MAIN DOWNLOAD LOGIC ---
@bot.on_message(filters.text & filters.private)
async def handle_request(client, message: Message):
    # Ignore commands
    if message.text.startswith("/"):
        return

    # Reset Stop Flag har naye request ke liye
    thanos.STOP_PROCESS = False

    # Parsing Name and URL
    if "|" in message.text:
        parts = message.text.split("|")
        name = parts[0].strip()
        url = parts[1].strip()
    else:
        name = "Video_File"
        url = message.text.strip()

    if not url.startswith("http"):
        return await message.reply_text("⚠️ **Bhai, sahi link toh dalo!**")

    editable = await message.reply_text("🔎 **Processing your request...**")

    # Call Thanos.py (Arguments handling already fixed)
    # 4 arguments bhej rahe hain (url, name, editable, bot)
    file_path = await thanos.download_video(url, name, editable, client)

    # Agar user ne stop kar diya
    if file_path == "STOPPED":
        return 

    # Uploading Logic
    if file_path and os.path.exists(file_path):
        await editable.edit("📤 **Download Done! Now Uploading...**")
        try:
            await client.send_video(
                chat_id=message.chat.id,
                video=file_path,
                caption=f"✅ **File Name:** `{name}`\n🚀 **Uploaded by UGDEV**",
                supports_streaming=True,
                # Isse progress dikhegi (Optional)
                progress=None 
            )
            await editable.delete()
            os.remove(file_path) # Storage clean karne ke liye
        except Exception as e:
            await editable.edit(f"❌ **Upload Error:** `{str(e)}`")
            if os.path.exists(file_path):
                os.remove(file_path)
    else:
        # Agar thanos.py ne None return kiya matlab error hai
        await editable.edit("❌ **Download Failed!**\n\nPossible Reasons:\n1. Token Expired\n2. 403 Forbidden\n3. DRM Protection")

print("✅ Bot is Online and Ready!")
bot.run()
