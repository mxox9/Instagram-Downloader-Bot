        from pyrogram import Client, filters
from utils import get_instagram_media

@Client.on_message(filters.command("start"))
def start_handler(client, message):
    message.reply_text(
        "👋 Welcome!\n\n"
        "Send me any Instagram public reel/post link and I will download it for you.\n\n"
        "👉 Usage: /download <Instagram_URL>"
    )

@Client.on_message(filters.command("download"))
def download_handler(client, message):
    if len(message.command) < 2:
        return message.reply_text("⚠️ Please provide an Instagram reel/post link.\n\nExample:\n`/download https://www.instagram.com/reel/xxxx/`")

    url = message.command[1]
    media_url, error = get_instagram_media(url)

    if error:
        message.reply_text(f"❌ Error: {error}")
    else:
        if ".mp4" in media_url:
            message.reply_video(media_url, caption="✅ Here is your Instagram video 🎬")
        else:
            message.reply_photo(media_url, caption="✅ Here is your Instagram photo 🖼️")
