from aiogram import html, Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove

from multilanguage_bot.keyboards.default import make_keyboards
from multilanguage_bot.keyboards.inline import three_languages
from multilanguage_bot.utils.db.postgres_db import pg
from multilanguage_bot.utils.helper.translate import google_translate

start_router = Router()

@start_router.message(CommandStart())
async def command_start_handler(message: Message):
    chat_id = message.chat.id
    languages = google_translate(chat_id)
    chat_ids = pg.get_chatid()

    if chat_id not in chat_ids:
        await message.answer(f"{languages["start"]}",
                             reply_markup=three_languages())

    await message.answer(f"{languages["keyboards"]}",
                         reply_markup=make_keyboards([languages["language"], languages["valyuta"]]))





@start_router.message(F.text.in_({"Valyuta kursi", "Курсы валют", "Currensy rates"}))
async def show_rates(message: Message):
    chat_id = message.chat.id
    languages = google_translate(chat_id)

    await message.answer(f"{languages["valyuta"]}:\n\n"
                         f"$ 1 = 12,937 UZS\n"
                         f"¥ 1 = 1,795 UZS\n"
                         f"$ 1 = ¥ 7.21")

@start_router.message(F.text.in_({"Tilni o'zgartirish", "Изменить язык", "Change language"}))
async def change_lang_handler(message: Message):
    chat_id = message.chat.id
    languages = google_translate(chat_id)

    await message.answer(f"{languages["choose"]}",
                         reply_markup=make_keyboards(["🇺🇿 uz", "🇷🇺 ru", "🇺🇸 en"], 3))

@start_router.message(F.text.in_({"🇺🇿 uz", "🇷🇺 ru", "🇺🇸 en"}))
async def change_lang(message: Message):
    chat_id = message.chat.id
    languages = google_translate(chat_id)
    lang = ""

    if message.text == '🇺🇿 uz':
        lang = 'uz'
        await message.answer("🇺🇿 uz", reply_markup=ReplyKeyboardRemove())
    elif message.text == '🇷🇺 ru':
        lang = 'ru'
        await message.answer("🇷🇺 ru", reply_markup=ReplyKeyboardRemove())
    elif message.text == '🇺🇸 en':
        lang = 'en'
        await message.answer("🇺🇸 en", reply_markup=ReplyKeyboardRemove())

    pg.update(call_data=lang, chat_id=chat_id)

    if not pg.update(call_data=lang, chat_id=chat_id):
        await message.answer("Til o'zgartirildi", reply_markup=ReplyKeyboardRemove())

    await message.answer(f"{languages["keyboards"]}",
                             reply_markup=make_keyboards([languages["language"], languages["valyuta"]]))
