import os
import subprocess
import asyncio

# Global flag to control the process
STOP_PROCESS = False

async def download_video(*args, **kwargs):
    global STOP_PROCESS
    STOP_PROCESS = False  # Reset flag for each new video call
    
    url = args[0] if len(args) > 0 else None
    name = args[1] if len(args) > 1 else "video"
    message = args[2] if len(args) > 2 else None
    
    if not url or not message:
        return None

    # Aapka updated token
    token = "EyJhbGciOiJIUzM4NCIsInR5cCI6IkpXVCJ9.eyJpZCI6OTI2NDc0NTgsIm9yZ0lkIjozOTUzMzgsInR5cGUiOjEsIm1vYmlsZSI6IjkxOTI4NDY3ODU2OCIsIm5hbWUiOiJQcmFmdWwgSmFtbmlrIiwiZW1haWwiOm51bGwsImlzSW50ZXJuYXRpb25hbCI6MCwiZGVmYXVsdExhbmd1YWdlIjoiZW4iLCJjb3VudHJ5Q29kZSI6IklOIiwiY291bnRyeUlTTyI6IjkxIiwidGltZXpvbmUiOiJHTVQrNTozMCIsImlzRGl5Ijp0cnVlLCJvcmdDb2RlIjoieHB0dXoiLCJpc0RpeVN1YmFkbWluIjowLCJmaW5nZXJwcmludElkIjoiMGIwOGM3ODJjNjVhNDM5ZmIxODYxNjU4ZWFjZWI1NTMiLCJpYXQiOjE3NzcyNjMxMjksImV4cCI6MTc3Nzg2NzkyOX0.9gu1AYc_o5fsaUTLnEIIGnKRfHGhAVz58gAXEBy8hcTpmP71TQB-0fvrgDMCqDXz"

    clean_name = "".join([c for c in name if c.isalnum() or c in (' ', '.', '_')]).strip()
    if not clean_name.endswith(".mp4"):
        clean_name += ".mp4"

    cmd = [
        "yt-dlp",
        "-f", "best",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "--add-header", f"x-access-token:{token}",
        "--add-header", "Origin:https://web.classplusapp.com",
        "--add-header", "Referer:https://web.classplusapp.com/",
        "--no-check-certificate",
        "--hls-prefer-native",
        "--concurrent-fragments", "16",
        "-o", clean_name,
        url
    ]

    try:
        # Start the process
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Check for stop signal while downloading
        while process.returncode is None:
            if STOP_PROCESS:
                try:
                    process.terminate()  # Kills yt-dlp
                    await message.edit("🛑 **Process Stopped!** Current download cancelled.")
                except:
                    pass
                return "STOPPED"
            
            await asyncio.sleep(2) # CPU par load kam karne ke liye
            if process.stdout.at_eof() and process.stderr.at_eof():
                break

        await process.wait()

        if process.returncode == 0:
            return clean_name
        return None

    except Exception as e:
        print(f"Error: {str(e)}")
        return None
