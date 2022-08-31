from aiogram.dispatcher import Dispatcher
from aiogram.types import Message, CallbackQuery
from asgiref.sync import sync_to_async

from web.app.models import Worker
from tgbot.services.db import get_all_workers
from tgbot.keyboards.inline import page_navigation_for_workers_markup, \
    worker_navigation_callback

async def view_workers_message_handler(call: CallbackQuery):
    await call.answer()
    markup = await create_markup_for_view_workers(page=0)
    await call.message.edit_text(
        text=(
            'Now you see all workers.\n'
            'Choose one to view more info '
            'or you can activate stop or delete worker\n'
            '✅ - worker is active\n'
            '⛔ - worker is stopped'
        ),
        reply_markup=markup,
    )

async def create_markup_for_view_workers(page: int):
    workers: list[Worker] = await sync_to_async(get_all_workers)()
    markup = await page_navigation_for_workers_markup(workers, page)
    return markup

async def view_workers_callback_handler(
    call: CallbackQuery, callback_data: dict
    ):
    await call.answer()
    page = int(callback_data.get('page', 0))
    markup = await create_markup_for_view_workers(page)
    await call.message.edit_text(
        text=(
            'Now you see all workers.\n'
            'Choose one to view more info '
            'or you can activate stop or delete worker\n'
            '✅ - worker is active\n'
            '⛔ - worker is stopped'
        ),
        reply_markup=markup,
    )

def register_view_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        view_workers_message_handler,
        text='view',
    )
    dp.register_callback_query_handler(
        view_workers_callback_handler,
        worker_navigation_callback.filter()
    )