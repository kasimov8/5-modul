import asyncio
import logging
import sys
from datetime import datetime, timedelta
from os import getenv

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
import random

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Salom, {html.bold(message.from_user.full_name)}!")
    # await message.answer(f"Salom, {html.bold(message.from_user.full_name)} bir o'yin o'ynaymiz. Men 1dan 20gacha son o'yladim son o'yladim topishga harakat qilingchi.")

# @dp.message()
# async def game(message: Message):
#     a = message.text
#     b = random.randint(1, 20)
#     if a.isdigit():
#         a = int(a)
#         if 1 <= a <= 20:
#             if a == b:
#                 await message.answer(f"Topdingiz qoyil🙂")
#             else:
#                 await message.answer(f"Yo'q topolmadingiz men o'ylagan son {b} edi")
#         else:
#             await message.answer(f"Men o'ylagan son 1 va 20 oralig'ida!")
#     else:
#         await message.send_copy(chat_id=message.chat.id)


@dp.message(F.sticker)
async def detect_photo(message: Message):
    await message.answer("Siz sticker yubordingiz!")

# @dp.message(F.text.regxp(r'(\u00a9|\u00ae|[\u2000-\u3300]|\ud83c[\ud000-\udfff]|\ud83d[\ud000-\udfff]|\ud83e[\ud000-\udfff])'))
# async def detect_emoji(message: Message):
#     await message.answer("Siz emoji yubordingiz!")

# @dp.message(F.text.regexp(r'(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})'))
# async def detect_birthdate(message: Message):
#     try:
#         birth_date = datetime.datetime.strptime(message.text, "%d.%m.%Y")
#         today = datetime.datetime.today()
#         age = today.year - birth_date.year
#         await message.answer(f"Siz {age} yoshdasiz.")
#     except ValueError:
#         await message.answer("⚠️ Iltimos, sanani to'g'ri formatda kiriting: kun.oy.yil (masalan, 12.03.2001)")

# @dp.message()
# async def detect_birthday(message: Message):
#     a  = message.text
#     if a.isdigit():
#         a = int(a)
#         if 1 < a < 100:
#             c = datetime.now() - timedelta(days=a * 365)
#             await message.answer(f"Siz {c.year}-yilda tug'ilgansiz")
#         else:
#             await message.answer(f"Men faqat 100 yoshgacha topa olaman!")
#     else:
#         await message.send_copy(chat_id=message.chat.id)


@dp.message()
async def echo_handler(message: Message) -> None:
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Yana urinib ko'ring!")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
