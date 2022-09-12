import datetime

import aioredis
from asgiref.sync import sync_to_async
from typing import Any, Literal

from tgbot.config import Config
from web.app.models import Worker

async def get_last_update_time(config: Config) -> float:
    last_time: float = await redis(
        method='get',
        key='last_update_time',
        redis_host=config.redis.host,
    )
    return last_time
   
    
async def update_last_update_time(config: Config, last_time: str):
    await redis(
        method='set',
        key='last_update_time',
        value=last_time,
        redis_host=config.redis.host,
    )

async def update_last_worker_telegram_id(
    config: Config, 
    last_worker_telegram_id: Worker.telegram_id,
    ):
    await redis(
        method='set',
        key='last_worker_telegram_id',
        value=last_worker_telegram_id,
        redis_host=config.redis.host,
    )
    
async def redis(
    method: Literal['get', 'set'],
    key: str,
    redis_host: str,
    value: str = None,
    ) -> Any:
    redis = await aioredis.Redis(host=redis_host)
    if method == 'get':
        getted_value: bytes = await redis.get(key)
        await redis.close()
        return getted_value.decode('utf-8')
    elif method == 'set':
        await redis.set(key, value)
    await redis.close()