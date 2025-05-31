from aiogram.utils.keyboard import ReplyKeyboardBuilder

def make_keyboards(options, col=2):
    builder = ReplyKeyboardBuilder()
    for opt in options:
        builder.button(text=opt)
    builder.adjust(col)
    return builder.as_markup(resize_keyboard=True, input_field_placeholder='Ok',)