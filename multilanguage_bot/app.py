import asyncio
import logging
import sys
from os import getenv, path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

BASE_DIR = path.dirname(path.abspath(__file__))

dp = Dispatcher()

async def main() -> None:
    from multilanguage_bot.handlers import start_router, call_router
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_routers(start_router, call_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
