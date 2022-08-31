from aiogram.types import Message
from asgiref.sync import sync_to_async
from aiogram.dispatcher import Dispatcher

from web.app.models import Worker
from tgbot.services.db import get_worker
from tgbot.keyboards.inline import worker_profile_markup, admin_profile_markup

async def worker_profile_handler(message: Message):
    worker: Worker = await sync_to_async(get_worker)(telegram_id=message.from_user.id)
    await message.answer(
        text=(
            f'Name: {worker.name}\n'
            f'Position: {worker.position}\n'
            f'Telegram id: {worker.telegram_id}\n'
            f'Is stopped: {worker.stop}'
        ),
        reply_markup=await worker_profile_markup(worker),
    )

async def admin_profile_handler(message: Message):
    await message.answer(
        text='Admin profile',
        reply_markup=admin_profile_markup,
    )

def register_profile_handlers(dp: Dispatcher):
    dp.register_message_handler(
        admin_profile_handler,
        commands=['profile'],
        is_admin=True,
    )
    dp.register_message_handler(
        worker_profile_handler,
        commands=['profile'],
        is_worker=True,
    )
