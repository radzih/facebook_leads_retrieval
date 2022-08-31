from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.types import CallbackQuery

async def close(call: CallbackQuery, state: FSMContext):
    await call.answer('Closed')
    await state.finish()
    await call.message.delete()

def register_global_actions_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        close,
        text='close',
        state='*',
    )