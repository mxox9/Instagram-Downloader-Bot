from telethon import TelegramClient, events
from config import Config
from handlers import *
import logging

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)

async def main():
    client = TelegramClient('bot', Config.API_ID, Config.API_HASH).start(bot_token=Config.BOT_TOKEN)
    
    client.add_event_handler(handle_start, events.NewMessage(pattern='/start'))
    client.add_event_handler(handle_help, events.NewMessage(pattern='/help'))
    client.add_event_handler(handle_about, events.NewMessage(pattern='/about'))
    client.add_event_handler(handle_auth, events.NewMessage(pattern='/auth'))
    client.add_event_handler(handle_unauth, events.NewMessage(pattern='/unauth'))
    client.add_event_handler(handle_profile_pic, events.NewMessage(pattern=r'/(dp|profile_pic)\s*'))
    client.add_event_handler(handle_download, events.NewMessage())
    client.add_event_handler(handle_callback, events.CallbackQuery())
    
    logging.info("Bot started!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
