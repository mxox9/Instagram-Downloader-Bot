from telethon import TelegramClient, events
from config import Config
from handler import *
import logging
import asyncio

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)

async def main():
    # Client बनाओ
    client = TelegramClient('bot', Config.API_ID, Config.API_HASH)
    
    # Bot start करो
    await client.start(bot_token=Config.BOT_TOKEN)
    
    # Event handlers add करो
    client.add_event_handler(handle_start, events.NewMessage(pattern='/start'))
    client.add_event_handler(handle_help, events.NewMessage(pattern='/help'))
    client.add_event_handler(handle_about, events.NewMessage(pattern='/about'))
    client.add_event_handler(handle_auth, events.NewMessage(pattern='/auth'))
    client.add_event_handler(handle_unauth, events.NewMessage(pattern='/unauth'))
    client.add_event_handler(handle_profile_pic, events.NewMessage(pattern=r'/(dp|profile_pic)\s*'))
    client.add_event_handler(handle_download, events.NewMessage())
    client.add_event_handler(handle_callback, events.CallbackQuery())
    
    logging.info("🚀 Bot started successfully!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
