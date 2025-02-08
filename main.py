import re
import requests
import os
import logging
import time
import asyncio
from io import BytesIO
from database import db
from config import Telegram
from instaloader import Instaloader, Post, Profile, Story
from telethon import TelegramClient, events

API_ID = Telegram.API_ID 
API_HASH = Telegram.API_HASH
BOT_TOKEN = Telegram.BOT_TOKEN
SESSION_ID = getattr(Telegram, 'SESSION_ID', None)

LOG_FILE = "log.txt"
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def get_instaloader():
    L = Instaloader()
    if SESSION_ID:
        try:
            L.load_session_from_file(SESSION_ID)
        except Exception as e:
            logging.error(f"Failed to load session: {e}")
            print(f"Failed to load session: {e}")
    return L

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("Send me an Instagram post/reel, story, or profile URL to download it.")
    logging.info(f"User {event.sender_id} started the bot.")
    if not await db.is_inserted("users", int(event.sender_id)):
        await db.insert("users", int(event.sender_id))

@bot.on(events.NewMessage(pattern='/logs', from_users=Telegram.AUTH_USER_ID))
async def send_logs(event):
    if os.path.exists(LOG_FILE):
        await bot.send_file(event.chat_id, LOG_FILE)
        logging.info(f"Sent logs to user {event.sender_id}")
    else:
        await event.reply("No logs found.")

@bot.on(events.NewMessage())
async def handle_message(event):
    text = event.message.text.strip()
    logging.info(f"Received message: {text} from user {event.sender_id}")

    if text.startswith("/"):
        return  

    post_reel_pattern = r'^https?://(www\.)?instagram\.com/(p|reel)/([a-zA-Z0-9_-]+)/?.*'
    profile_pattern = r'^https?://(www\.)?instagram\.com/([a-zA-Z0-9_.-]+)(?:\?.*)?$'
    story_pattern = r'^https?://(www\.)?instagram\.com/stories/([^/]+)/(\d+)/?.*'

    post_reel_match = re.match(post_reel_pattern, text)
    profile_match = re.match(profile_pattern, text)
    story_match = re.match(story_pattern, text)

    if post_reel_match:
        shortcode = post_reel_match.group(3)
        await download_instagram_post(event, shortcode)
    elif profile_match:
        username = profile_match.group(1)
        if username.lower() in ["p", "reel", "stories", "explore"]:
            return
        await download_profile_pic(event, username)
    elif story_match:
        if not SESSION_ID:
            await event.reply("❌ Story downloads require an active Instagram session.")
            return
        username = story_match.group(2)
        await download_story(event, username)
    else:
        await event.reply("Please send a valid Instagram URL.")
        logging.warning(f"Invalid URL received: {text}")

async def download_instagram_post(event, shortcode):
    L = get_instaloader()
    start_time = time.time()
    downloading_message = await event.reply("🔄 Downloading Instagram post...")
    
    try:
        post = Post.from_shortcode(L.context, shortcode)
        url = post.video_url if post.is_video else post.url
        media_type = 'video' if post.is_video else 'photo'
        caption = post.caption[:1024] if post.caption else None

        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()

        chunk_size = 256 * 1024
        buffer = BytesIO()
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        last_update = 0

        for chunk in response.iter_content(chunk_size):
            if chunk:
                downloaded += len(chunk)
                buffer.write(chunk)
                progress = (downloaded / total_size * 100) if total_size > 0 else 0
                if progress - last_update >= 10:
                    await downloading_message.edit(f"⬇️ Downloading... {progress:.1f}%")
                    last_update = progress

        buffer.seek(0)
        await downloading_message.edit("⬆️ Uploading...")

        file_name = f"{shortcode}.mp4" if media_type == 'video' else f"{shortcode}.jpg"
        await bot.send_file(event.chat_id, buffer, file_name=file_name, caption=caption, force_document=False)

    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")
        logging.error(f"Error downloading {shortcode}: {e}")
        print(f"Error: {e}")
    finally:
        await bot.delete_messages(event.chat_id, [downloading_message.id])
        buffer.close()

async def download_profile_pic(event, username):
    L = get_instaloader()
    downloading_message = await event.reply("🔄 Downloading profile picture...")
    
    try:
        profile = Profile.from_username(L.context, username)
        url = profile.profile_pic_url
        bio = profile.biography[:1024] if profile.biography else None

        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()

        buffer = BytesIO()
        for chunk in response.iter_content(256 * 1024):
            buffer.write(chunk)
        buffer.seek(0)

        await bot.send_file(event.chat_id, buffer, file_name=f"{username}_profile.jpg", caption=bio)
        
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")
        logging.error(f"Error downloading profile {username}: {e}")
        print(f"Error: {e}")
    finally:
        await bot.delete_messages(event.chat_id, [downloading_message.id])
        buffer.close()

async def download_story(event, username):
    L = get_instaloader()
    downloading_message = await event.reply("🔄 Downloading story...")
    
    try:
        profile = Profile.from_username(L.context, username)
        stories = Story.from_profile(L.context, profile).get_items()

        if not stories:
            return await event.reply("❌ No active stories found.")

        for story in stories:
            url = story.video_url if story.is_video else story.url
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()

            buffer = BytesIO()
            for chunk in response.iter_content(256 * 1024):
                buffer.write(chunk)
            buffer.seek(0)

            file_name = f"{username}_story.mp4" if story.is_video else f"{username}_story.jpg"
            await bot.send_file(event.chat_id, buffer, file_name=file_name, force_document=False)

            buffer.close()

    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")
        logging.error(f"Error downloading story for {username}: {e}")
        print(f"Error: {e}")
    finally:
        await bot.delete_messages(event.chat_id, [downloading_message.id])

if __name__ == "__main__":
    logging.info("Bot is starting...")
    print("✅ Bot is running!")
    bot.run_until_disconnected()
