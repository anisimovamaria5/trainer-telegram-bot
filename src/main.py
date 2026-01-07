import asyncio
import json
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, REDIRECT_URI, YANDEX_CLIENT_ID, YANDEX_CLIENT_SECRET
from keysboards import *
from handlers import other_handlers
from handlers import user_handlers
from yandex_calendar import YandexCalendarAPI
from aiogram.types import Update

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def handler(event: dict, context):
    body: str = event["body"]
    update_data = json.loads(body) if body else {}

    await dp.feed_update(
        bot, 
        Update.model_validate(update_data)
        )

    return {"statusCode": 200,
            "body": ""}


async def main() -> None:
    yandex_calendar = YandexCalendarAPI(
        client_id=YANDEX_CLIENT_ID,
        client_secret=YANDEX_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI
    )
    dp['yandex_calendar'] = yandex_calendar

    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())