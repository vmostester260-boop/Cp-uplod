import os, re, sys, time, json, aiohttp, requests, asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyromod import listen
from vars import *
import thanos as helper
from db import db

# Initialize Bot
bot = Client(
    "DRM_Wizard",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

@bot.on_message(filters.command("start"))
async def start(client, m: Message):
    if not db.is_user_authorized(m.from_user.id, client.me.username):
        return await m.reply_text("❌ **Access Denied!** Contact Admin.")
    
    await m.reply_text(
        f"**Hello {m.from_user.first_name}!**\n\n"
        "I am your DRM Downloader Bot. Send /drm to start downloading from a .txt file."
    )

@bot.on_message(filters.command("drm"))
async def drm_handler(client, m: Message):
    # Auth Check
    if not db.is_user_authorized(m.from_user.id, client.me.username):
        return await m.reply_text("❌ Unauthorized!")

    editable = await m.reply_text("✨ **Hii! Send me your .txt file (Format - Name:Link)**")
    
    try:
        input_msg: Message = await client.listen(editable.chat.id, timeout=60)
    except asyncio.TimeoutError:
        return await editable.edit("⏰ Timeout! Command restart karein.")

    if input_msg.document and input_msg.document.file_name.endswith('.txt'):
        file_path = await input_msg.download()
        await input_msg.delete()
        
        with open(file_path, "r", encoding='utf-8') as f:
            content = f.read().strip().split("\n")
        os.remove(file_path)
        
        links = []
        for line in content:
            if ":" in line:
                parts = line.split(":", 1)
                links.append([parts[0].strip(), parts[1].strip()])

        if not links:
            return await editable.edit("❌ File mein koi valid link nahi mili (Format: Name:Link)")

        await editable.edit(f"✅ **Found {len(links)} links. Process shuru ho raha hai...**")

        for name, url in links:
            # --- API EXTRACTION LOGIC ---
            prog_msg = await m.reply_text(f"🔎 **𝐄𝐱𝐭𝐫𝐚𝐜𝐭𝐢𝐧𝐠:** `{name}`")
            
            # Aapki Vercel API Link
            api_url = f"https://my-api-ebon-phi.vercel.app/extract_keys?url={url}&user_id={m.from_user.id}"
            
            final_link = url
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(api_url, timeout=15) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            final_link = data.get("video_url", url)
                            print(f"API Success for {name}")
                except Exception as e:
                    print(f"API Error: {e}")
            
            await prog_msg.delete()

            # --- DOWNLOAD & UPLOAD ---
            try:
                # helper.download_video ab thanos.py se headers use karega
                res = await helper.download_video(final_link, name, m, client)
                if res:
                    await helper.send_vid(client, m, res, name)
                else:
                    await m.reply_text(f"❌ **Download Failed:** `{name}`")
            except Exception as e:
                await m.reply_text(f"⚠️ **Error in {name}:** `{str(e)}` \nLink: {final_link}")
                
        await m.reply_text("🎯 **Batch Completed!**")
    else:
        await editable.edit("❌ **Invalid!** Sirf `.txt` file bhejien.")

if __name__ == "__main__":
    bot.run()
