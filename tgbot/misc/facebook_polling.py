import asyncio
import aiohttp
import datetime
import logging
from typing import Literal, NamedTuple

import aioredis
from aiogram import Bot
from asgiref.sync import sync_to_async
from aiogram.utils.exceptions import BotBlocked, CantInitiateConversation

from tgbot.config import Config
from tgbot.services.db import get_active_workers
from web.app.models import Worker

GET_LEADS_API_URL = \
    'https://graph.facebook.com/v14.0/{form_id}/leads?access_token={access_token}'
GET_FORMS_API_URL = \
    'https://graph.facebook.com/v14.0/{page_id}/leadgen_forms?access_token={access_token}'

async def request(method: Literal['get', 'post'], url: str, **kwargs) -> dict:
    logger = logging.getLogger(__name__)
    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, **kwargs) as response:
            if response.status != 200:
                logger.error(
                    f'{response.status} {response.reason}\n'
                    f'{await response.text()}\n {url}{kwargs}'
                    )
                await asyncio.sleep(5)
                await session.close()
                return await request(method, url, **kwargs)
            response_data = await response.json()
        await session.close()
    return response_data

async def get_last_worker_telegram_id(config: Config) -> Worker.telegram_id:
    redis = await aioredis.Redis(host=config.redis.host)
    last_worker_telegram_id = await redis.get('last_worker_telegram_id')
    last_worker_telegram_id = last_worker_telegram_id.decode('utf-8')
    await redis.close()
    if last_worker_telegram_id == 'None':
        if workers := (await sync_to_async(get_active_workers)()):
            return workers[0]
        raise NoActiveWorkers
    return int(last_worker_telegram_id)

async def update_last_worker_telegram_id(
    config: Config, 
    last_worker_telegram_id: Worker.telegram_id,
    ):
    redis = await aioredis.Redis(host=config.redis.host)
    await redis.set('last_worker_telegram_id', last_worker_telegram_id)
    await redis.close()
    
async def get_last_update_time(config: Config) -> datetime.datetime:
    redis = await aioredis.Redis(host=config.redis.host)
    last_time_encoded: str = await redis.get('last_update_time')
    if last_time_encoded is None:
        last_time = '2020-08-28T05:47:35+0000'
    else:
        last_time = last_time_encoded.decode('utf-8')
    await redis.close()
    return datetime.datetime.strptime(last_time, '%Y-%m-%dT%H:%M:%S%z')

async def update_last_update_time(config: Config, last_time: str):
    redis = await aioredis.Redis(host=config.redis.host)
    await redis.set('last_update_time', last_time)
    await redis.close()

async def get_leads_from_form(config: Config, form_id: int):
    url = GET_LEADS_API_URL.format(
        form_id=form_id, 
        access_token=config.facebook.access_token,
        )
    data = await request('get', url)
    last_update_time = await get_last_update_time(config)
    valid_leads = []
    for lead in reversed(data['data']):
        lead_created = datetime.datetime.strptime(
            lead['created_time'], 
            '%Y-%m-%dT%H:%M:%S%z',
            )
        if lead_created > last_update_time:
            lead['form_id'] = form_id
            valid_leads.append(lead)
    if valid_leads: await update_last_update_time(config, lead['created_time']) 
    return valid_leads

def get_form_ids(data: dict):
    for form in data['data']:
        if form['status'] == 'ACTIVE':
            yield form['id']
    
async def get_leads(config: Config):
    url = GET_FORMS_API_URL.format(
        page_id=config.facebook.page_id, 
        access_token=config.facebook.access_token,
        )
    data = await request('get', url)
    forms_ids = get_form_ids(data)
    leads = []
    for form in forms_ids:
        form_leads = await get_leads_from_form(config, form)
        
        leads.extend(form_leads)
    if leads == []: raise NoNewLeads
    leads = list(Lead.parse_lead(lead) for lead in leads)
    return leads

async def make_worker_telegram_id_list(config: Config):
    active_workers: list[Worker.telegram_id] = \
        await sync_to_async(get_active_workers)()
    if not active_workers: raise NoActiveWorkers
    last_worker_telegram_id = await get_last_worker_telegram_id(config)
    workers_telegram_ids = \
        active_workers[
            active_workers.index(last_worker_telegram_id)+1:len(active_workers)
            ] \
            + active_workers[
                0:active_workers.index(last_worker_telegram_id)+1
                ]
    await check_workers(workers_telegram_ids, config)
    return workers_telegram_ids

class Lead(NamedTuple):
    id: str
    form_id: str
    data: str
    created_time: datetime.datetime
    
    @classmethod
    def parse_lead(cls, lead: dict) -> 'Lead':
        return cls(
            id=lead['id'],
            form_id=lead['form_id'],
            created_time=datetime.datetime.strptime(
                lead['created_time'], 
                '%Y-%m-%dT%H:%M:%S%z'
            ),
            data='\n'.join(' '.join(field['name'].split('_')).capitalize() + ': ' + ' '.join(field['values']) for field in lead['field_data'])
            )

async def send_leads_loop(
    workers_telegram_ids: list[Worker.telegram_id], 
    leads: list[Lead],
    config: Config,
    ):
    bot = Bot(config.tg_bot.token)
    index = 0
    while leads:
        worker_telegram_id = workers_telegram_ids[index%len(workers_telegram_ids)]
        lead = leads[-1]
        index += 1
        try:
            await bot.send_message(
                chat_id=worker_telegram_id,
                text=(
                    f'Lead ID: {lead.id}\n'
                    f'Form ID: {lead.form_id}\n'
                    f'Created time: {lead.created_time.strftime("%d.%m.%Y %H:%M:%S")}\n'
                    f'{lead.data}'
                )
            )
        except CantInitiateConversation:
            continue
        except BotBlocked:
            continue
        leads.pop(-1)
        await asyncio.sleep(0.1)
    await (await bot.get_session()).close()
    await update_last_worker_telegram_id(config, worker_telegram_id)
    

class NoActiveWorkers(Exception):
    pass

class NoNewLeads(Exception):
    pass

async def check_workers(
    workers_telegrams_ids: list[Worker.telegram_id], 
    config: Config
    ):
    bot = Bot(config.tg_bot.token)
    is_no_workers = True
    for telegram_id in workers_telegrams_ids:
        try:
            await bot.send_chat_action(
                chat_id=telegram_id, 
                action='typing',
                )
        except:
            continue
        is_no_workers = False
    await (await bot.get_session()).close()
    if is_no_workers: raise NoActiveWorkers

async def send_leads(config: Config):
    try:
        workers_telegram_ids = await make_worker_telegram_id_list(config)
    except NoActiveWorkers:
        return
    try: 
        leads = await get_leads(config)
    except NoNewLeads:
        return 
    logger = logging.getLogger(__name__)
    logger.info(f'{len(leads)} leads found')
    await send_leads_loop(workers_telegram_ids, leads, config)
