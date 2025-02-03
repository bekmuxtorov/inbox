from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def make_inline_buttons(words: dict, row_width: int = 1) -> InlineKeyboardMarkup:
    buttons_group = InlineKeyboardMarkup(row_width=row_width)
    for text, callback_data in words.items():
        if text is not None and callback_data is not None:
            buttons_group.insert(InlineKeyboardButton(
                text=text, callback_data=callback_data))
    return buttons_group


send_question_button = make_inline_buttons(
    words={"📤Send question": "send_question"})
