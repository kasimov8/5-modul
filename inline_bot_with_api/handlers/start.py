from aiogram import Router, html
from aiogram.filters import CommandStart
from aiogram.types import Message

startRouter = Router()


@startRouter.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer(f"Salom, {html.bold(message.from_user.full_name)}")
