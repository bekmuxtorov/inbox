from aiogram.dispatcher.filters.state import State, StatesGroup


class Register(StatesGroup):
    phone_number = State()
