
import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, BotCommand
from dotenv import load_dotenv

load_dotenv()
TOKEN = getenv("BOT_TOKEN")
ADMINS = getenv('ADMINS').split(',')
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Salom, {html.bold(message.from_user.full_name)}!")


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command='start', description='Botni ishga tushurish'),
        BotCommand(command='help', description='Yordam olish botdan'),
        BotCommand(command='play', description='Guess Number o`yinini o`ynash'),
        # BotCommand(command='register', description='Ro`yxatdan o`tish'),
        # BotCommand(command='set', description='Nimadur o`zgartirish')
    ]
    await bot.set_my_commands(commands)


async def start_up(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(admin, 'Bot ishga tushdi!')
        except Exception as e:
            print(f'{e} :{admin} id li user topilmadi!')


async def shut_down(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(admin, 'Bot o`chdi!')
        except Exception as e:
            print(f'{e} :{admin} id li user topilmadi!')


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await set_commands(bot)
    dp.startup.register(start_up)
    dp.shutdown.register(shut_down)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
