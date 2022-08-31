from aiogram.dispatcher import Dispatcher
from aiogram.types import CallbackQuery

async def first_page(call: CallbackQuery):
    await call.answer('Its first page')

async def last_page(call: CallbackQuery):
    await call.answer('Its last page')


def register_notifications_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        first_page,
        text='first_page',
    )
    dp.register_callback_query_handler(
        last_page,
        text='last_page',
    )