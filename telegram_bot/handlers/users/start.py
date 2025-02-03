from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from loader import dp, db

from states.registration import Register
from keyboards.default import contact_request_button
from keyboards.inline import send_question_button


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    telegram_id = message.from_user.id
    user = await db.select_user(telegram_id=telegram_id)
    if not user:
        await message.answer("☎️Please share your phone number or send it as a example.\n\nExample: +998901644101", reply_markup=contact_request_button)
        await Register.phone_number.set()
        return

    await message.answer("👋🏻Hello! If you have a question, click the \"Send question\" button.", reply_markup=send_question_button)
