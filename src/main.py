import asyncio
import json
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from src.config import BOT_TOKEN
from src.keysboards import *
from src.handlers import other_handlers, user_handlers
from src.google_calendar import GoogleCalendarAPI
from aiogram.types import Update


storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


google_calendar = GoogleCalendarAPI()
dp['google_calendar'] = google_calendar 

dp.include_router(user_handlers.router)
dp.include_router(other_handlers.router)


async def handler(event: dict, context):
    try:

        body = event.get("body", "{}")
        update_data = json.loads(body)
        update = types.Update(**update_data)
        await dp.feed_update(bot=bot, update=update)
        
        return {
            "statusCode": 200,
            "body": json.dumps({"ok": True})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())