import asyncio
import logging
import sys
from os import getenv
import psycopg2

from typing import Optional
from dataclasses import field
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()

conn = psycopg2.connect(
    dbname=getenv("DB_NAME"),
    user=getenv("DB_USER"),
    password=getenv("DB_PASSWORD"),
    host=getenv("DB_HOST"),
    port=getenv("DB_PORT")
)

curr = conn.cursor()

class PageCallbackData(CallbackData, prefix='page'):
    action: str
    page: int
    category: Optional[str] = field(default=None)


def page_keyboards(page: int = -1):
    builder = InlineKeyboardBuilder()
    curr.execute("SELECT category_name FROM examines ORDER BY id;")
    datas = curr.fetchall()
    datas = [row[0] for row in datas]
    datas = set(datas)
    datas = list(sorted(datas))



    if page == -1:
        builder.row(
            InlineKeyboardButton(
                text="Boshlash",
                callback_data=PageCallbackData(action='next', page=page).pack())
        )
    elif page == 0:
        for c in datas:
            builder.row(
                InlineKeyboardButton(
                    text=f"{c}",
                    callback_data=PageCallbackData(action='next', page=page, category=c).pack()),
            )
        builder.row(
            InlineKeyboardButton(
                text=f"Ortga",
                callback_data=PageCallbackData(action='prev', page=page).pack()),
        )

    # builder.row(
    #     InlineKeyboardButton(
    #         text="Avvalgi",
    #         callback_data=PageCallbackData(action='prev', page=page).pack()),
    #     InlineKeyboardButton(
    #         text="Keyingi",
    #         callback_data=PageCallbackData(action='next', page=page).pack())
    # )


    return builder.as_markup()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    chat_id = message.chat.id
    name = message.from_user.full_name
    curr.execute("SELECT chat_id FROM users;")
    rows = curr.fetchall()
    chat_ids = [row[0] for row in rows]

    if chat_id not in chat_ids:
        with conn:
            curr.execute(f"""INSERT INTO users(name, chat_id) VALUES (%s, %s)""", (name, chat_id))

    await message.answer(f"Salom, {html.bold(message.from_user.full_name)}!\n\n"
                         f"O'yinni boshlash uchun pastdagi {html.bold('Boshlash')} tugmasini bosing.",
                         reply_markup=page_keyboards())


@dp.message(Command('help', prefix='/%$'))
async def cmd_help(message: Message) -> None:
    await message.answer('Yordam')


# @dp.callback_query(PageCallbackData.filter(F.action == 'prev'))
# @dp.callback_query(PageCallbackData.filter(F.action == 'next'))
@dp.callback_query(PageCallbackData.filter())
async def callbacks_data(call: CallbackQuery, callback_data: PageCallbackData):
    page = int(callback_data.page)

    if callback_data.action == 'next':
        page += 1
    elif callback_data.action == 'prev':
        page += -1

    # await call.message.edit_text(text=f"{smiles[page]}\n{page} - sahifa",
    #                              reply_markup=page_keyboards(page))

    await call.message.edit_text(text=f"Kategoriya tanlang:", reply_markup=page_keyboards(page))

    if callback_data.category == "Matematika":
        curr.execute("SELECT quiz FROM examines WHERE category_name='Matematika'")
        rows = curr.fetchall()
        datas = [row[0] for row in rows]

        for data in datas:
            await call.message.edit_text(text=f"{data}", reply_markup=page_keyboards(page))





async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
