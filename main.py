import re
import requests
import tempfile
import os
import time
import logging
from dotenv import load_dotenv 
from instaloader import Instaloader, Post, Profile
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

TOKEN = os.environ.get('TG_BOT_TOKEN')

LOG_FILE = "log.txt"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me an Instagram post/reel URL or profile URL to download content!")
    logging.info(f"User {update.effective_user.id} started the bot.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    logging.info(f"Received message: {text} from user {update.effective_user.id}")

    post_reel_pattern = r'^https?://(www\.)?instagram\.com/(p|reel)/([a-zA-Z0-9_-]+)/?.*'
    profile_pattern = r'^https?://(www\.)?instagram\.com/([^/?]+)(?:\?.*)?$'

    post_reel_match = re.match(post_reel_pattern, text)
    profile_match = re.match(profile_pattern, text)

    if post_reel_match:
        shortcode = post_reel_match.group(3)
        await download_instagram_post(shortcode, update)
    elif profile_match:
        username = profile_match.group(2)
        if username in ["p", "reel", "stories", "explore"]:
            return
        await download_profile_pic(username, update)
    else:
        await update.message.reply_text("Please send a valid Instagram URL.")
        logging.warning(f"Invalid URL received: {text}")

async def download_instagram_post(shortcode, update):
    L = Instaloader()
    downloading_message = await update.message.reply_text("🔄 Downloading Instagram post...")
    logging.info(f"Downloading post: {shortcode}")

    try:
        start_time = time.time()
        post = Post.from_shortcode(L.context, shortcode)

        url = post.video_url if post.is_video else post.url
        media_type = 'video' if post.is_video else 'photo'
        caption = post.caption if post.caption else "No caption available."

        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()

        suffix = '.mp4' if media_type == 'video' else '.jpg'
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_file.flush()
            temp_file.close()

        download_time = time.time() - start_time
        upload_time_estimate = download_time * 1.5

        await downloading_message.edit_text(f"✅ Download complete in {download_time:.2f} sec. Uploading...")
        logging.info(f"Download complete: {shortcode} in {download_time:.2f} sec.")

        with open(temp_file.name, 'rb') as media:
            if media_type == 'video':
                msg = await update.message.reply_video(video=media, caption=f"`{caption}`", parse_mode="Markdown")
            else:
                msg = await update.message.reply_photo(photo=media, caption=f"`{caption}`", parse_mode="Markdown")

        os.unlink(temp_file.name)
        logging.info(f"Upload complete: {shortcode}")
      
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=downloading_message.message_id)
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)

    except requests.RequestException as e:
        await update.message.reply_text("❌ Failed to download media. Please try again later.")
        logging.error(f"Request error for {shortcode}: {e}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
        logging.error(f"Error downloading {shortcode}: {e}")

async def download_profile_pic(username, update):
    L = Instaloader()
    downloading_message = await update.message.reply_text("🔄 Downloading profile picture...")
    logging.info(f"Downloading profile picture for: {username}")

    try:
        start_time = time.time()
        profile = Profile.from_username(L.context, username)
        url = profile.profile_pic_url
        bio = profile.biography if profile.biography else "No bio available."

        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_file.flush()
            temp_file.close()

        download_time = time.time() - start_time
        upload_time_estimate = download_time * 1.5

        await downloading_message.edit_text(f"📥 Download complete in {download_time:.2f} sec. 📤 Uploading...")
        logging.info(f"Download complete for {username} in {download_time:.2f} sec.")

        with open(temp_file.name, 'rb') as media:
            msg = await update.message.reply_photo(photo=media, caption=f"👤 *Bio:*\n`{bio}`", parse_mode="Markdown")

        os.unlink(temp_file.name)
        logging.info(f"Upload complete for {username}")

        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=downloading_message.message_id)
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)

    except requests.RequestException as e:
        await update.message.reply_text("❌ Failed to download profile picture. Please try again later.")
        logging.error(f"Request error for {username}: {e}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
        logging.error(f"Error downloading profile {username}: {e}")

async def send_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if os.path.exists(LOG_FILE):
            await update.message.reply_document(document=InputFile(LOG_FILE))
            logging.info(f"Sent logs to user {update.effective_user.id}")
        else:
            await update.message.reply_text("No logs found.")
    except Exception as e:
        await update.message.reply_text("❌ Error retrieving logs.")
        logging.error(f"Error sending logs: {e}")

def main():
    logging.info("Bot is starting...")
    print("✅ Bot is running!")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("logs", send_logs))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
