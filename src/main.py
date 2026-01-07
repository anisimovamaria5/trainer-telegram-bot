import asyncio
import json
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, REDIRECT_URI, YANDEX_CLIENT_ID, YANDEX_CLIENT_SECRET
from keysboards import *
from handlers import other_handlers, user_handlers
from yandex_calendar import YandexCalendarAPI

from aiogram.types import Update


storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


yandex_calendar = YandexCalendarAPI(
    client_id=YANDEX_CLIENT_ID,
    client_secret=YANDEX_CLIENT_SECRET,
    redirect_uri=REDIRECT_URI
)
dp['yandex_calendar'] = yandex_calendar

dp.include_router(user_handlers.router)
dp.include_router(other_handlers.router)

# Обработчик для вебхуков
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