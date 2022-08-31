from asyncio.log import logger
import logging
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.types import CallbackQuery, Message
from asgiref.sync import sync_to_async

from tgbot.keyboards.inline import cancel_markup, start_work_markup
from tgbot.services.db import get_or_create_worker, is_worker_exists_sync

async def add_worker_handler(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state('get_worker_name')
    await call.message.edit_text(
        text='Enter worker name',
        reply_markup=cancel_markup,
    )

async def get_worker_name(message: Message, state: FSMContext):
    if len(message.text) > 255:
        return await message.answer(
            text='Name is too long',
            reply_markup=cancel_markup,
        )
    await state.set_state('get_worker_position')
    await state.update_data(name=message.text)
    await message.answer(
        text='Enter worker position',
        reply_markup=cancel_markup,
    )

async def get_worker_position(message: Message, state: FSMContext):
    if len(message.text) > 255:
        return await message.answer(
            text='Position is too long',
            reply_markup=cancel_markup,
        )
    state_data = await state.get_data()
    await state.set_state('get_worker_telegram_id')
    await state.update_data(
        position=message.text,
        name=state_data['name'],
        )
    await message.answer(
        text='Forward any text message from worker',
        reply_markup=cancel_markup,
    )

async def is_worker_exists(telegram_id: int) -> bool:
    is_exists =  await sync_to_async(
        is_worker_exists_sync
        )(telegram_id=telegram_id)
    return is_exists

async def get_worker_telegram_id(message: Message, state: FSMContext):
    if not message.forward_from:
        return await message.answer(
            text=(
                'Forward any text message from worker!!!\n'
                '(Worker account should not be hidden)'
            ),
            reply_markup=cancel_markup
        )
    elif await is_worker_exists(message.forward_from.id):
        return await message.answer(
            text='Worker with this telegram id already exists',
            reply_markup=cancel_markup,
        )
    state_data = await state.get_data()
    await state.finish()
    telegram_id = message.forward_from.id
    name, position = state_data['name'], state_data['position']
    await sync_to_async(get_or_create_worker)(
        telegram_id=telegram_id, 
        name=name, 
        position=position,
        )
    await message.answer(
        text=f'Worker {name} added\nYou can forward message bellow to worker',
    )
    await message.answer(
        text=(
            f'{name} please start bot'
        ),
        reply_markup=await start_work_markup(message.bot)
    ) 

def register_add_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        add_worker_handler,
        text='add',
        is_admin=True,
    )
    dp.register_message_handler(
        get_worker_name,
        state='get_worker_name',
    )
    dp.register_message_handler(
        get_worker_position,
        state='get_worker_position',
    )
    dp.register_message_handler(
        get_worker_telegram_id,
        state='get_worker_telegram_id',
    )