from aiogram.dispatcher import Dispatcher
from aiogram.types import Message

async def start_work(message: Message):
    await message.answer(
        text='Ok, now you can receive leads',
    )

def register_start_handlers(dp: Dispatcher):
    dp.register_message_handler(
        start_work,
        commands=['start'],
        is_worker=True,
    )