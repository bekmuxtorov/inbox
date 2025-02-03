from re import match as re_match
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from loader import dp, db

from states.registration import Register
from keyboards.default import contact_request_button
from keyboards.inline import send_question_button


@dp.message_handler(content_types=types.ContentType.CONTACT, state=Register.phone_number)
async def process_adding_departmant(message: types.Message, state: FSMContext):
    contact = message.contact.phone_number
    service_message = await message.answer(text=".", reply_markup=ReplyKeyboardRemove())
    await service_message.delete()
    await create_user(message, contact, state)


@dp.message_handler(content_types=types.ContentType.TEXT, state=Register.phone_number)
async def process_adding_departmant(message: types.Message, state: FSMContext):
    contact = message.text.strip()
    pattern = r"^\+998\d{9}$"

    if re_match(pattern, contact):
        service_message = await message.answer(text=".", reply_markup=ReplyKeyboardRemove())
        await service_message.delete()
        await create_user(message, contact, state)
    else:
        await message.answer("‼️Please share your phone number or send it as a example.\n\nExample: +998901644101", reply_markup=contact_request_button)
        await Register.phone_number.set()
        return


async def create_user(message: types.Message, contact: str, state: FSMContext):
    telegram_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    status = await db.add_user(
        telegram_id=telegram_id,
        full_name=full_name,
        phone_number=contact,
        username=username,
    )

    if not status:
        await message.answer("Please share your phone number or send it as a example.\n\nExample: +998901644101", reply_markup=contact_request_button)
        await Register.phone_number.set()
        return

    await message.answer("👋🏻Hello! If you have a question, click the \"Send question\" button.", reply_markup=send_question_button)
    await state.finish()
