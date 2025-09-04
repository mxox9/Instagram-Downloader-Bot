from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import get_instagram_media

@Client.on_message(filters.command("start"))
async def start(client, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Help", callback_data="help"),
         InlineKeyboardButton("ℹ️ About", callback_data="about")]
    ])
    await message.reply_text(
        f"✨ Welcome {message.from_user.first_name}!\n\n"
        "Send me any public Instagram reel/post link and I’ll download it for you.",
        reply_markup=buttons
    )

@Client.on_callback_query()
async def callbacks(client, callback_query):
    if callback_query.data == "help":
        await callback_query.message.edit_text(
            "📚 **Help**\n\n"
            "1. Copy a public Instagram post/reel URL\n"
            "2. Send it here\n"
            "3. Bot will download media and send back"
        )
    elif callback_query.data == "about":
        await callback_query.message.edit_text(
            "ℹ️ **About**\n\n"
            "Simple Instagram Downloader Bot\n"
            "Works only for *public* content."
        )

@Client.on_message(filters.text & ~filters.command(["start", "help", "about"]))
async def download_instagram(client, message):
    url = message.text.strip()

    if "instagram.com" not in url:
        return await message.reply_text("❌ Please send a valid Instagram link.")

    status = await message.reply_text("⏳ Fetching media...")

    media = get_instagram_media(url)
    if not media:
        return await status.edit("❌ Could not fetch media. Maybe link is invalid or private.")

    try:
        if media["type"] == "video":
            await client.send_video(message.chat.id, media["url"], caption="🎥 Here is your video")
        else:
            await client.send_photo(message.chat.id, media["url"], caption="📸 Here is your photo")

        await status.delete()
    except Exception as e:
        await status.edit(f"❌ Failed: {str(e)}")
