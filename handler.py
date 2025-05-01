from telethon import events, Button
from config import Config
from database import db
from utils import extract_post_id, download_post, cleanup
import instaloader
import os

async def handle_start(event):
    bot = await event.client.get_me()
    buttons = [
        [Button.inline("📚 Help", b"help"), Button.inline("ℹ️ About", b"about")],
        [Button.url("🌟 More Bots", "https://t.me/")]
    ]
    await event.reply(
        f"""✨ **Welcome to {bot.first_name}!** ✨

I can download public Instagram content.
For private content, use /auth to login.""",
        buttons=buttons
    )

async def handle_help(event):
    help_text = """🛠 **How to Use** 🛠

1. Send Instagram post link
2. Use `/dp username` for profile pictures
3. Private posts require /auth"""

    if Config.has_insta_creds:
        help_text += "\n\n🔑 Global login available for public content"

    await event.edit(
        help_text,
        buttons=Button.inline("🔙 Back", b"home")
    )

async def handle_about(event):
    await event.edit(
        """🌐 **About This Bot**

• Downloads Instagram content
• Optional login for private posts
• No data retention""",
        buttons=Button.inline("🔙 Back", b"home")
    )

async def handle_auth(event):
    async with event.client.conversation(event.chat_id) as conv:
        await conv.send_message("""🔐 **Instagram Login**

⚠️ For private content only
⚠️ Use a secondary account

Reply `yes` to continue or `no` to cancel""")
        
        response = await conv.get_response()
        if response.text.lower() not in ['yes', 'y']:
            return await conv.send_message("🚫 Cancelled")
            
        await conv.send_message("📧 Send Instagram username:")
        username_msg = await conv.get_response()
        
        await conv.send_message("🔑 Send Instagram password:")
        password_msg = await conv.get_response()
        
        try:
            loader = instaloader.Instaloader()
            loader.login(username_msg.text.strip(), password_msg.text.strip())
            db.set_user_credentials(event.sender_id, username_msg.text, password_msg.text)
            await conv.send_message("✅ Login successful!")
        except Exception:
            await conv.send_message("❌ Login failed. Check credentials")

async def handle_unauth(event):
    if db.delete_user_credentials(event.sender_id):
        await event.reply("🔓 Credentials removed")
    else:
        await event.reply("ℹ️ No credentials stored")

async def handle_profile_pic(event):
    args = event.pattern_match.group(1).split()
    if len(args) < 1:
        return await event.reply("❌ Format: /dp username")
    
    username = args[0].strip('@')
    try:
        instaloader.Instaloader(quiet=True).download_profile(username, profile_pic_only=True)
        
        for file in os.listdir(username.lower()):
            if file.endswith(".jpg"):
                await event.client.send_file(
                    event.chat_id,
                    file=f"{username.lower()}/{file}",
                    caption=f"📸 @{username}"
                )
                break
        
        await cleanup(username.lower())
    except Exception:
        await event.reply("❌ Failed to download")

async def handle_download(event):
    post_id = extract_post_id(event.text)
    if not post_id:
        return
    
    status = await event.reply("⏳ Processing...")
    
    try:
        # Try user credentials first
        username, password = db.get_user_credentials(event.sender_id)
        
        # Fallback to global credentials if available
        if not username and Config.has_insta_creds:
            username, password = Config.INSTA_USERNAME, Config.INSTA_PASSWORD
        
        photos, videos, caption = await download_post(post_id, username, password)
        
        media = photos + videos
        if not media:
            return await status.edit("❌ No media found")
        
        caption = f"{caption}" if caption else "via @"
        
        if len(media) == 1:
            await event.client.send_file(event.chat_id, media[0], caption=caption)
        else:
            await event.client.send_file(
                event.chat_id,
                media,
                caption=caption if len(media) > 1 else None
            )
        
        await status.delete()
    except Exception as e:
        await status.edit(f"❌ Error: {str(e)}")
    finally:
        await cleanup(f"-{post_id}")

async def handle_callback(event):
    data = event.data.decode()
    if data == "home":
        await handle_start(event)
    elif data == "help":
        await handle_help(event)
    elif data == "about":
        await handle_about(event)
