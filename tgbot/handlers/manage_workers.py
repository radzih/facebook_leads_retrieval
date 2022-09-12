from re import L
from turtle import update
from aiogram.dispatcher import Dispatcher
from aiogram.types import Message, CallbackQuery
from asgiref.sync import sync_to_async
from tgbot.config import Config
from tgbot.misc.leads_send import NoActiveWorkers, get_last_worker_telegram_id, update_last_worker_telegram_id

from web.app.models import Worker
from tgbot.services.db import get_next_worker_telegram_id, get_worker, stop_or_activate_worker_sync, \
    delete_worker_sync
from tgbot.keyboards.inline import manage_worker_markup,\
    manage_worker_action_callback, worker_callback

async def view_worker_info(call: CallbackQuery, callback_data: dict):
    await call.answer()
    worker_id = int(callback_data.get('worker_id'))
    worker: Worker = await sync_to_async(get_worker)(id=worker_id)
    await call.message.edit_text(
        text=(
            'Worker info:\n'
            f' Name: {worker.name}\n'
            f' Position: {worker.position}\n'
            f' Telegram id: {worker.telegram_id}\n'
            f' Is stopped: {worker.stop}\n'
        ),
        reply_markup=await manage_worker_markup(worker),
    )

async def delete_worker(
    call: CallbackQuery, 
    callback_data: dict, 
    config: Config,
    ):
    await call.answer()
    worker_id = int(callback_data.get('worker_id'))
    worker: Worker = await sync_to_async(get_worker)(id=worker_id)
    await update_last_worker_telegram_id(config, worker.telegram_id)
    worker: Worker = await sync_to_async(delete_worker_sync)(id=worker_id)
    await call.message.edit_text(
        text=(
            f'Worker {worker.name} was deleted'
        )
    )

async def update_last_worker_telegram_id_prevent(worker: Worker, config: Config):
    try:
        last_worker_telegram_id = await get_last_worker_telegram_id(config)
    except NoActiveWorkers:
        return
    if worker.telegram_id == last_worker_telegram_id:
        new_last_worker_telegram_id = await sync_to_async(
            get_next_worker_telegram_id,
            )(last_worker_telegram_id)
        await update_last_worker_telegram_id(config, new_last_worker_telegram_id)

async def stop_or_activate_worker(
    call: CallbackQuery, 
    callback_data: dict,
    config: Config,
    ):
    await call.answer()
    worker_id = int(callback_data.get('worker_id'))
    worker: Worker = await sync_to_async(get_worker)(id=worker_id)
    await update_last_worker_telegram_id_prevent(worker, config)
    worker: Worker = await sync_to_async(stop_or_activate_worker_sync)(id=worker_id)
    await call.message.edit_text(
        text=(
            f'Worker {worker.name} was '
            f'{("stopped" if worker.stop else "activated")}'
        )
    )

def register_manage_workers_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        view_worker_info,
        worker_callback.filter(),
    )
    dp.register_callback_query_handler(
        delete_worker,
        manage_worker_action_callback.filter(action='delete'),
    )
    dp.register_callback_query_handler(
        stop_or_activate_worker,
        manage_worker_action_callback.filter(action='stop'),
    )
    dp.register_callback_query_handler(
        stop_or_activate_worker,
        manage_worker_action_callback.filter(action='activate'),
    )