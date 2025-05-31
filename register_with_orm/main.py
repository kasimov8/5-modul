import asyncio
import logging
import sys
import re

from os import getenv
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import Message
from dotenv import load_dotenv

from register_with_orm.sqlalchemy_orm import session, Users

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher(storage=MemoryStorage())
GMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@gmail\.com$'


class RegisterState(StatesGroup):
    full_name = State()
    phone = State()
    email = State()




def make_keyboards(options, row=2):
    width = len(options)
    width = width + 1 if width % 2 != 0 else width
    keyboards = [KeyboardButton(text=str(o)) for o in options]
    keyboards = [keyboards[i:i + row] for i in range(0, width, row)]

    markup = ReplyKeyboardMarkup(keyboard=keyboards, resize_keyboard=True)
    return markup


keyboard = [
    [
        KeyboardButton(text="Share my contact", request_contact=True)
    ]
]

kb_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


@dp.message(CommandStart())
async def command_start_handler(message: Message):
    datas = Users.select()
    b = message.chat.id


    if b not in datas:
        await message.answer(f"Salom, botimizdan foydalanish uchun ro'yxatdan o'tishingiz kerak.\n\n"
                             f"Ro'yxatdan o'tish uchun /register tugmasini bosing.")
    else:
        await message.answer(f"😊 Xush kelibsiz {html.bold(message.from_user.full_name)}.\n"
                             f"Siz oldin ro'yxatdan o'tgansiz. Botimizdan bemalol foydalaning.", reply_markup=make_keyboards(["Update my information", "Delete my informations"]))


@dp.message(Command('register'))
async def start_register(message: Message, state: FSMContext):
    await state.set_state(RegisterState.full_name)
    await message.answer("🧑 To'liq ismingizni kiriting.")


@dp.message(RegisterState.full_name)
async def get_full_name(message: Message, state: FSMContext):
    full_name = message.text
    chat_id = message.chat.id
    await state.update_data(full_name=full_name.title(), chat_id=chat_id)
    a = full_name.count(" ")
    if a == 0:
        await message.answer(f"To'liq ismingizni ajratib yozing.")
    elif a > 1:
        await message.answer(f"To'liq ismingizda probellar soni ortib ketti.")
    else:
        await message.answer("📲 Telefon raqamingizni kiriting.", reply_markup=kb_markup)
        await state.set_state(RegisterState.phone)


@dp.message(RegisterState.phone)
async def get_phone(message: Message, state: FSMContext):
    if message.contact:
        phone_number = message.contact.phone_number
    else:
        phone_number = message.text
    await state.update_data(phone=phone_number)

    await message.answer('Elektron pochta manzilingizni kiriting.', reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegisterState.email)


@dp.message(RegisterState.email)
async def get_email(message: Message, state: FSMContext):
    email = message.text
    await state.update_data(email=email.lower())

    if not re.fullmatch(GMAIL_REGEX, email):
        await message.reply("❌ Email manzil noto‘g‘ri! Iltimos, to‘g‘ri formatda kiriting (masalan: user@example.com)")
    else:
        await message.answer(f"🎉 Tabriklayman siz muvaffaqiyatli ro'yxatdan o'tdingiz.\n\n", reply_markup=make_keyboards(["Update my information", "Delete my informations"]))

        datas = await state.get_data()
        fulllname = datas.get("full_name")
        emaill = datas.get("email")
        phonee = datas.get("phone")
        chat_idd = datas.get("chat_id")

        db = Users(full_name=fulllname, email=emaill, phone=phonee, chat_id=chat_idd)
        db.save(session)
        await state.clear()

@dp.message(F.text == "Delete my informations")
async def delete_informations(message: Message):
    chat_id = message.chat.id
    Users.delete(session, chat_id)

    await message.answer(f"Muvvafaqiyatli o'chirildi!\n\n"
                         f"Botdan foydalanish uchun yana registratsiyadan o'tishingiz kerak! /register", reply_markup=ReplyKeyboardRemove())

@dp.message(F.text == "Update my information")
async def update_informations(message: Message):
    await message.answer(f"Ma'lumotingizni o'zgartirish uchun quyidagi formatta sms yuboring.\n\n"
                         f"{html.bold('full_name=...')}\n" 
                         f"{html.bold('email=...')}\n"
                         f"{html.bold('phone=...')}" , reply_markup=ReplyKeyboardRemove())

@dp.message()
async def update(message: Message):
    mg_txt = message.text
    chat_id = message.chat.id
    try:
        if mg_txt.startswith('full_name='):
            Users.update(session, chat_id, mg_txt)
            await message.answer("Ma'lumot o'zgartirildi.", reply_markup=make_keyboards(["Update my information", "Delete my informations"]))
        elif mg_txt.startswith('email='):
            Users.update(session, chat_id, mg_txt)
            await message.answer("Ma'lumot o'zgartirildi.", reply_markup=make_keyboards(["Update my information", "Delete my informations"]))
        elif mg_txt.startswith('phone='):
            Users.update(session, chat_id, mg_txt)
            await message.answer("Ma'lumot o'zgartirildi.", reply_markup=make_keyboards(["Update my information", "Delete my informations"]))
        else:
            await message.answer("O'zgartirish uchun tepada ko'rsatilgandek qilib qiymat kiriting.")
    except Exception as e:
        await message.answer("Ma'lumotlar ba'zasida bunday ustun yo'q.")
    


async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
