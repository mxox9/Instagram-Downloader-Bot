import re
import requests
import tempfile
import os
import logging
import time
from config import Telegram
from instaloader import Instaloader, Post, Profile
from telethon import TelegramClient, events

API_ID = Telegram.API_ID 
API_HASH = Telegram.API_HASH
BOT_TOKEN = Telegram.BOT_TOKEN

LOG_FILE = "log.txt"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("Send me an Instagram post or reel Link(URL) to download it.")
    logging.info(f"User {event.sender_id} started the bot.")

@bot.on(events.NewMessage(pattern='/logs'))
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
    profile_pattern = r'^https?://(www\.)?instagram\.com/([^/?]+)(?:\?.*)?$'

    post_reel_match = re.match(post_reel_pattern, text)
    profile_match = re.match(profile_pattern, text)

    if post_reel_match:
        shortcode = post_reel_match.group(3)
        await download_instagram_post(event, shortcode)
    elif profile_match:
        username = profile_match.group(2)
        if username in ["p", "reel", "stories", "explore"]:
            return
        await download_profile_pic(event, username)
    else:
        await event.reply("Please send a valid Instagram URL.")
        logging.warning(f"Invalid URL received: {text}")

async def download_instagram_post(event, shortcode):
    L = Instaloader()
    start_time = time.time()
    downloading_message = await event.reply("🔄 Downloading Instagram post... (Estimating time)")
    logging.info(f"Downloading post: {shortcode}")

    try:
        post = Post.from_shortcode(L.context, shortcode)
        url = post.video_url if post.is_video else post.url
        media_type = 'video' if post.is_video else 'photo'
        caption = post.caption if post.caption else ""

        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()

        expected_time = response.headers.get('Content-Length')
        if expected_time:
            expected_time = round(int(expected_time) / (500 * 1024), 2)

        await bot.edit_message(event.chat_id, downloading_message.id, f"🔄 Downloading Instagram post... (~{expected_time}s)")

        suffix = '.mp4' if media_type == 'video' else '.jpg'
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_file.flush()
            temp_file.close()

        download_time = time.time() - start_time
        logging.info(f"Download complete: {shortcode} in {download_time:.2f} sec.")

        await bot.send_file(event.chat_id, temp_file.name, caption=caption if caption else None)
        os.unlink(temp_file.name)

        logging.info(f"Upload complete: {shortcode}")
        await bot.delete_messages(event.chat_id, [downloading_message.id])

    except requests.RequestException as e:
        await event.reply("❌ Failed to download media. Please try again later.")
        logging.error(f"Request error for {shortcode}: {e}")
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")
        logging.error(f"Error downloading {shortcode}: {e}")

async def download_profile_pic(event, username):
    L = Instaloader()
    start_time = time.time()
    downloading_message = await event.reply("🔄 Downloading profile picture...")
    logging.info(f"Downloading profile picture for: {username}")

    try:
        profile = Profile.from_username(L.context, username)
        url = profile.profile_pic_url
        bio = profile.biography if profile.biography else ""

        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_file.flush()
            temp_file.close()

        download_time = time.time() - start_time
        logging.info(f"Download complete for {username} in {download_time:.2f} sec.")

        await bot.send_file(event.chat_id, temp_file.name, caption=bio if bio else None)
        os.unlink(temp_file.name)

        logging.info(f"Upload complete for {username}")
        await bot.delete_messages(event.chat_id, [downloading_message.id])

    except requests.RequestException as e:
        await event.reply("❌ Failed to download profile picture. Please try again later.")
        logging.error(f"Request error for {username}: {e}")
    except Exception as e:
        await event.reply(f"❌ Error: {str(e)}")
        logging.error(f"Error downloading profile {username}: {e}")

if __name__ == "__main__":
    logging.info("Bot is starting...")
    print("✅ Bot is running!")
    bot.run_until_disconnected()
