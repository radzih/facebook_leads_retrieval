import asyncio
from datetime import datetime
import logging

import aioredis
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.misc.setup_django import setup_django; setup_django()
from tgbot.config import Config, load_config
from tgbot.filters.admin import AdminFilter
from tgbot.filters.worker import WorkerFilter
from tgbot.misc.leads_send import send_leads
from tgbot.handlers.add import register_add_handlers
from tgbot.handlers.view import register_view_handlers
from tgbot.handlers.start import register_start_handlers
from tgbot.handlers.profile import register_profile_handlers
from tgbot.middlewares.environment import EnvironmentMiddleware
from tgbot.handlers.notifications import register_notifications_handlers
from tgbot.handlers.global_actions import register_global_actions_handlers
from tgbot.handlers.manage_workers import register_manage_workers_handlers

logger = logging.getLogger(__name__)


def register_all_middlewares(dp, config):
    dp.setup_middleware(EnvironmentMiddleware(config=config))


def register_all_filters(dp: Dispatcher):
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(WorkerFilter)


def register_all_handlers(dp):
    register_add_handlers(dp)
    register_view_handlers(dp)
    register_manage_workers_handlers(dp)
    register_notifications_handlers(dp)
    register_global_actions_handlers(dp)
    register_profile_handlers(dp)
    register_start_handlers(dp)




async def set_default_values_for_redis(config: Config):
    import time
    from tgbot.services.redis import redis
    await redis(
        method='set',
        key='last_update_time',
        redis_host=config.redis.host,
        value=1662109244
    )

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)
    logger.info("Starting bot")
    config = load_config(".env")

    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)
    scheduler = AsyncIOScheduler()

    bot['config'] = config
    scheduler.add_job(send_leads, 'interval', minutes=5, kwargs={'config': config}, next_run_time=datetime.now())
    await set_default_values_for_redis(config)
    register_all_middlewares(dp, config)
    register_all_filters(dp)
    register_all_handlers(dp)

    # start
    try:
        scheduler.start()
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
