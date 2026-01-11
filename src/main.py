import asyncio
import json
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
<<<<<<< HEAD
from src.config import BOT_TOKEN
from src.keysboards import *
from src.handlers import other_handlers, user_handlers
from src.google_calendar import GoogleCalendarAPI
from aiogram.types import Update
=======
from config import BOT_TOKEN, REDIRECT_URI, YANDEX_CLIENT_ID, YANDEX_CLIENT_SECRET
from keysboards import *
from handlers import other_handlers, user_handlers
from yandex_calendar import YandexCalendarAPI
>>>>>>> f11be5c759b73d82ce9286cdd91864a4d88fad7f


storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
<<<<<<< HEAD
dp = Dispatcher()


google_calendar = GoogleCalendarAPI()
dp['google_calendar'] = google_calendar 
=======
dp = Dispatcher(storage=storage)

yandex_calendar = YandexCalendarAPI(
    client_id=YANDEX_CLIENT_ID,
    client_secret=YANDEX_CLIENT_SECRET,
    redirect_uri=REDIRECT_URI
)
dp['yandex_calendar'] = yandex_calendar
>>>>>>> f11be5c759b73d82ce9286cdd91864a4d88fad7f

dp.include_router(user_handlers.router)
dp.include_router(other_handlers.router)

<<<<<<< HEAD

=======
# Обработчик для вебхуков
>>>>>>> f11be5c759b73d82ce9286cdd91864a4d88fad7f
async def handler(event: dict, context):
    try:

        body = event.get("body", "{}")
        update_data = json.loads(body)
<<<<<<< HEAD
        update = types.Update(**update_data)
=======

        update = types.Update(**update_data)

>>>>>>> f11be5c759b73d82ce9286cdd91864a4d88fad7f
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