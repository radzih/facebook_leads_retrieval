from ast import operator
from asyncio.log import logger
import datetime
import logging
import time

import pydantic

from tgbot.config import Config, load_config 
from tgbot.schemas.lead import Lead
from tgbot.misc.request import request
from leads_agregator.exceptions.agregator_exceptions import NoNewLeads
from tgbot.services.redis import get_last_update_time,\
    update_last_update_time


GET_FORMS_API_URL = (
        'https://graph.facebook.com/v14.0/{page_id}/leadgen_forms'
        '?access_token={access_token}'
        )

GET_LEADS_API_URL = (
    'https://graph.facebook.com/v14.0/{form_id}/leads'
    '?access_token={access_token}'    
)

FACEBOOK_API_FILTER = (
    '&filtering=[{{"field":"{field}","operator":"{operator}","value":"{value}"}}]'
)

async def get_leads(config: Config) -> list[Lead]:
    get_forms_url = GET_FORMS_API_URL.format(
        page_id=config.facebook.page_id, 
        access_token=config.facebook.access_token,
        )
    data = await request('get', get_forms_url)
    forms_ids = get_form_ids(data)
    leads = []
    for form in forms_ids:
        form_leads = await get_leads_from_form(config, form)
        leads.extend(form_leads)
    await update_last_update_time(config, time.time()) 
    if leads == []: raise NoNewLeads
    leads = parse_leads(leads)
    return leads

def parse_leads(leads: list) -> list[Lead]:
    parsed_leads = []
    for lead in leads:
        try:
            parsed_leads.append(Lead.parse_lead(lead))
        except pydantic.error_wrappers.ValidationError as exception:
            logger = logging.getLogger(__name__)
            logger.debug(f'Invalid lead: {lead}, error: {exception}')
    return parsed_leads
        

def get_form_ids(data: dict) -> list[int]:
    logging.debug(f'Facebook forms: {data}')
    for form in data['data']:
        if form['status'] == 'ACTIVE':
            yield form['id']

async def get_leads_from_form(config: Config, form_id: int) -> list[dict]:
    last_update_time = await get_last_update_time(config)
    get_leads_url = GET_LEADS_API_URL.format(
        form_id=form_id, 
        access_token=config.facebook.access_token,
        ) + FACEBOOK_API_FILTER.format(
            field='time_created',
            operator='GREATER_THAN',
            value=last_update_time,
        )
    data = await request('get', get_leads_url)
    valid_leads = []
    logging.debug(f'Facebook leads: {data}')
    for lead in reversed(data['data']):
        lead['form_id'] = form_id
        valid_leads.append(lead)
    return valid_leads





