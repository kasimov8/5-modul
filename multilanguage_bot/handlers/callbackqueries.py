from aiogram import Router, F
from aiogram.types import CallbackQuery

from multilanguage_bot.keyboards.default import make_keyboards
from multilanguage_bot.utils.db.postgres_db import pg
from multilanguage_bot.utils.helper.translate import google_translate

call_router = Router()

@call_router.callback_query(F.data.in_({'uz', 'ru', 'en'}))
async def uz_callback_handler(call: CallbackQuery):
    chat_id = call.message.chat.id
    chat_ids = pg.get_chatid()
    languages = google_translate(chat_id)

    if call.data == 'uz':
        if chat_id not in chat_ids:
            pg.save(chat_id, 'uz')
    elif call.data == 'ru':
        if chat_id not in chat_ids:
            pg.save(chat_id, 'ru')
    elif call.data == 'en':
        if chat_id not in chat_ids:
            pg.save(chat_id, 'en')
