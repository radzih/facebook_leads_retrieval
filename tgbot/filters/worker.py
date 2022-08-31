import typing

from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message, CallbackQuery
from asgiref.sync import sync_to_async

from tgbot.services.db import get_all_workers


class WorkerFilter(BoundFilter):
    key = 'is_worker'

    def __init__(self, is_worker: typing.Optional[bool] = None):
        self.is_worker = is_worker

    async def check(self, obj):
        if self.is_worker is None:
            return False
        workers = await sync_to_async(get_all_workers)() 
        return obj.from_user.id in list(worker.telegram_id for worker in workers)
        

