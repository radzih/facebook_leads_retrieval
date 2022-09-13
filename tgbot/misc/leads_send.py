import asyncio
import logging

from aiogram import Bot
from asgiref.sync import sync_to_async
from aiogram.utils.exceptions import BotBlocked, CantInitiateConversation
from leads_agregator.exceptions.agregator_exceptions import NoNewLeads

from tgbot.config import Config
from tgbot.keyboards.inline import pipedrive_deal_markup
from tgbot.services import db
from tgbot.exceptions.workers import NoActiveWorkers
from tgbot.services.redis import redis, update_last_worker_telegram_id
from tgbot.services import pipedrive
from web.app.models import Worker
from tgbot.schemas.lead import Lead

   
async def get_last_worker_telegram_id(config: Config) -> Worker.telegram_id:
    last_worker_telegram_id = await redis(
        method='get',
        key=f'last_worker_telegram_id',
        redis_host=config.redis.host,
    )
    if last_worker_telegram_id == 'None':
        if workers := (await sync_to_async(db.get_active_workers)()):
            return workers[0]
        raise NoActiveWorkers
    return int(last_worker_telegram_id)


async def make_worker_telegram_id_list(config: Config):
    active_workers: list[Worker.telegram_id] = \
        await sync_to_async(db.get_active_workers)()
    if not active_workers: raise NoActiveWorkers
    last_worker_telegram_id = await get_last_worker_telegram_id(config)
    workers_telegram_ids = \
        active_workers[
            active_workers.index(last_worker_telegram_id)+1:len(active_workers)
            ] \
            + active_workers[
                0:active_workers.index(last_worker_telegram_id)+1
                ]
    # await check_workers(workers_telegram_ids, config)
    return workers_telegram_ids

async def send_leads_loop(
    workers_telegram_ids: list[Worker.telegram_id], 
    leads: list[Lead],
    config: Config,
    ):
    bot = Bot(config.tg_bot.token)
    index = -1
    while leads:
        index += 1
        lead = leads.pop(-1)
        worker_telegram_id = workers_telegram_ids[index%len(workers_telegram_ids)]
        deal_id = await pipedrive.create_deal(config, lead)
        try:
            await bot.send_message(
                chat_id=worker_telegram_id,
                text=(
                    f'Lead ID: {lead.id}\n'
                    f'{"-"*25}\n'
                    f'Campaign name: {lead.campaign_name}\n'
                    f'Adset name: {lead.adset_name}\n'
                    f'Ad name: {lead.ad_name}\n'
                    f'{"-"*25}\n'
                    f'Name: {lead.name}\n'
                    f'Phone: {lead.phone}\n'
                    f'Created time: {lead.created_time.strftime("%d.%m.%Y %H:%M:%S")}\n'
                    f'Platform: {lead.platform}\n'
                ),
                reply_markup=await pipedrive_deal_markup(
                    deal_id, config.misc.pipedrive_domain
                    ),
            )
        except (CantInitiateConversation, BotBlocked):
            continue
        await sync_to_async(db.update_lead_is_new_status)(lead.id)
        await asyncio.sleep(0.1)
    await (await bot.get_session()).close()
    try:
        await update_last_worker_telegram_id(config, worker_telegram_id)
    except NameError:
        pass
    
# async def check_workers(
#     workers_telegrams_ids: list[Worker.telegram_id], 
#     config: Config
#     ):
#     bot = Bot(config.tg_bot.token)
#     is_no_workers = True
#     for telegram_id in workers_telegrams_ids:
#         try:
#             await bot.send_chat_action(
#                 chat_id=telegram_id, 
#                 action='typing',
#                 )
#         except (CantInitiateConversation, BotBlocked):
#             continue
#         is_no_workers = False
#     await (await bot.get_session()).close()
#     if is_no_workers: raise NoActiveWorkers

async def send_leads(config: Config):
    try:
        workers_telegram_ids = await make_worker_telegram_id_list(config)
    except NoActiveWorkers:
        return
    try:
        leads: list[Lead] = await sync_to_async(db.get_new_leads)()
    except NoNewLeads:
        return
    logger = logging.getLogger(__name__)
    logger.info(f'{len(leads)} leads found')
    await send_leads_loop(workers_telegram_ids, leads, config)
