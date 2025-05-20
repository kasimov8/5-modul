import asyncio
import logging
import json
import tabulate

import psycopg2
import sys
import re
from os import getenv


from aiogram import Bot, Dispatcher, html, F
from aiogram.client import bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import Message
from dotenv import load_dotenv


load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher(storage=MemoryStorage())

conn = psycopg2.connect(
    dbname=getenv("DB_NAME"),
    user=getenv("DB_USER"),
    password=getenv("DB_PASSWORD"),
    host=getenv("DB_HOST"),
    port=getenv("DB_PORT")
)

curr = conn.cursor()

GMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@gmail\.com$'


class RegisterState(StatesGroup):
    full_name = State()
    phone = State()
    email = State()


class GameState(StatesGroup):
    game_quiz = State()


def make_keyboards(options, row=2):
    width = len(options)
    width = width + 1 if width % 2 != 0 else width
    keyboards = [KeyboardButton(text=str(o)) for o in options]
    keyboards = [keyboards[i:i + row] for i in range(0, width, row)]

    markup = ReplyKeyboardMarkup(keyboard=keyboards, resize_keyboard=True)
    return markup


async def send_question(message, state):
    data = await state.get_data()
    step = data.get('step')
    corrects = int(data.get('corrects', 0))



    curr.execute("""SELECT quiz, options
                    FROM questions;""")
    rows = curr.fetchall()

    if step >= len(rows):
        await message.answer(f"Savollar tugadi!\n\n1) Yana o'ynash uchun /play ni bosing.\n"
                             f"2)Statisticani ko'rish uchun /statistica buyrug'ini bosing.",
                             reply_markup=ReplyKeyboardRemove())

        user_name = message.from_user.full_name

        curr.execute("SELECT user_name FROM statistica WHERE user_name = %s", (user_name,))
        exists = curr.fetchone()

        if not exists:
            with conn:
                curr.execute("""INSERT INTO statistica (user_name, count_correct)
                                VALUES (%s, %s)""", (user_name, corrects if corrects is not None else 0))
        else:
            with conn:
                curr.execute("""UPDATE statistica
                                SET count_correct = count_correct + %s
                                WHERE user_name = %s""", (corrects, user_name))

        await state.clear()
        return

    quiz, options = rows[step]
    options = json.loads(options) if isinstance(options, str) else options

    await message.answer(quiz, reply_markup=make_keyboards(options))


keyboard = [
    [
        KeyboardButton(text="Share my contact", request_contact=True)
    ]
]

kb_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


@dp.message(CommandStart())
async def command_start_handler(message: Message):
    curr.execute("""SELECT chat_id
                    FROM users""")
    data = curr.fetchall()
    b = message.chat.id
    user_ids = [row[0] for row in data]

    if b not in user_ids:
        await message.answer(f"Salom, botimizdan foydalanish uchun ro'yxatdan o'tishingiz kerak.\n\n"
                             f"Ro'yxatdan o'tish uchun /register tugmasini bosing.")
    else:
        await message.answer(f"😊 Xush kelibsiz {html.bold(message.from_user.full_name)}\n\n"
                             f"O'yinni boshlash uchun /play tugmasini bosing.")


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
        await message.answer(f"🎉 Tabriklayman siz muvaffaqiyatli ro'yxatdan o'tdingiz.\n\n"
                             f"O'yinni boshlash uchun /play tugmasini bosing.")

        datas = await state.get_data()
        fulllname = datas.get("full_name")
        emaill = datas.get("email")
        phonee = datas.get("phone")
        chat_idd = datas.get("chat_id")

        with conn:
            curr.execute("""INSERT INTO users (fullname, phone, email, chat_id)
                            VALUES (%s, %s, %s, %s)""", (fulllname, phonee, emaill, chat_idd))

        await state.clear()


@dp.message(Command('followers'))
async def get_followers(message: Message):
    curr.execute("""SELECT COUNT(*)
                    FROM users""")
    result = curr.fetchone()
    count = result[0]

    await message.answer(f"Botdan foydalanuvchilar soni: {html.bold(count)}")


@dp.message(Command('play'))
async def game(message: Message):
    await message.answer(f"O'yinni boshlaymizmi!", reply_markup=make_keyboards(['Ha', 'Yoq']))


@dp.message(F.text == 'Ha')
async def starting_game(message: Message, state: FSMContext):
    await message.answer("Qani kettik.", reply_markup=ReplyKeyboardRemove())
    await state.set_state(GameState.game_quiz)
    await state.update_data(step=0, corrects=0)
    await send_question(message, state)


@dp.message(F.text == 'Yoq')
async def starting_game2(message: Message):
    await message.answer("O'yinni boshlash uchun /play tugmasini bosing.", reply_markup=ReplyKeyboardRemove())


@dp.message(GameState.game_quiz)
async def game_quiz(message: Message, state: FSMContext):
    data = await state.get_data()
    step = data.get("step", 0)
    corrects = int(data.get("corrects", 0))
    msg_txt = message.text


    curr.execute("SELECT quiz, options, is_correct FROM questions;")
    rows = curr.fetchall()

    if step >= len(rows):
        await send_question(message, state)
        return

    quiz, options, correct_answer = rows[step]
    correct_answer = correct_answer.strip()

    if msg_txt.strip() == correct_answer:
        corrects += 1
        await message.answer("To‘g‘ri ✅")
    else:
        await message.answer(f"No‘to‘g‘ri ❌. To‘g‘ri javob: {correct_answer}")

    step += 1
    await state.update_data(step=step, corrects=corrects)

    await send_question(message, state)


@dp.message(Command("statistica"))
async def show_statistics(message: Message):
    curr.execute("SELECT user_name, count_correct FROM statistica;")
    rows = curr.fetchall()

    if not rows:
        await message.answer("Statistika hali mavjud emas.")
        return

    table = tabulate.tabulate(rows, headers=["Foydalanuvchi", "To'g'ri javoblar"], tablefmt="pretty")

    await message.answer(f"```\n{table}\n```", parse_mode="Markdown")

@dp.message()
async def lyuboy_message(message: Message):
    await message.answer(f"O'yinni boshlash uchun /play tugmasini bosing.")



async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
