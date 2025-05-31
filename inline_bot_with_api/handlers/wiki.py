import random
import uuid

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
import wikipedia

wiki_router = Router()


@wiki_router.inline_query()
async def inline_query_handler(inline_query: InlineQuery):
    word = inline_query.query.strip()
    results = []
    if not word:
        results.append(InlineQueryResultArticle(
            id=str(1),
            title="🤔 Hech narsa yo'q!",
            description=f"\"{word}\" haqida ma'lumot topilmadi!",
            thumbnail_url='https://pngimg.com/d/wikipedia_PNG38.png',
            input_message_content=InputTextMessageContent(
                message_text=f"☹️ \"{word}\" haqida ma'lumot topilmadi!"
            )

        ))
        return await inline_query.answer(results, cache_time=1)

    objs = wikipedia.search(word, results=3)

    results = []
    for title in objs:
        obj = wikipedia.page(title)
        results.append(InlineQueryResultArticle(
            id=str(random.randint(100000, 10000000)),
            title=f"{obj.title}",
            description=f"\"{obj.content[:20]}\"",
            input_message_content=InputTextMessageContent(
                message_text=f'<a href="{obj.url}">{obj.title}</a>',
                parse_mode=ParseMode.HTML
            )

        ))
    await inline_query.answer(results, cache_time=1)