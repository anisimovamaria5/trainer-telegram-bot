import asyncio
from aiogram import Bot, Dispatcher
from .config import BOT_TOKEN, REDIRECT_URI, YANDEX_CLIENT_ID, YANDEX_CLIENT_SECRET
from .keysboards import *
from handlers import other_handlers
from handlers import user_handlers
from .yandex_calendar import YandexCalendarAPI


async def handler(event: dict, context):
    print(f"{event=}")
    print(f"{context=}")

    return {"statusCode": 200,
            "body": ""}

async def main() -> None:
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
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())