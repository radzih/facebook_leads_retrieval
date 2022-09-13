import logging
import time
from typing import Iterable

import pydantic

from tgbot.config import Config
from tgbot.schemas.lead import Lead
from tgbot.misc.request import request
from leads_agregator.exceptions.agregator_exceptions import MissingPermissions, NoNewLeads
from tgbot.services.redis import get_last_update_time,\
    update_last_update_time


GET_ADS_API_URL = (
        'https://graph.facebook.com/v14.0/act_{ad_account_id}/ads'
        '?access_token={access_token}&fields=id,status'
        )

GET_LEADS_API_URL = (
    'https://graph.facebook.com/v14.0/{ad_id}/leads'
    '?access_token={access_token}'    
)

FACEBOOK_API_FILTER = (
    '&filtering=[{filter}]'
)

FACEBOOK_GET_LEAD_INFO_URL = (
    'https://graph.facebook.com/v14.0/{lead_id}'
    '?access_token={access_token}'
    '&fields=field_data,ad_name,campaign_name,adset_name,created_time,platform'
)

async def get_leads(config: Config) -> list[Lead]:
    get_ads_url = GET_ADS_API_URL.format(
        ad_account_id=config.facebook.ad_account_id, 
        access_token=config.facebook.access_token,
        )
    data = await request('get', get_ads_url)
    ads_ids = get_ads_ids(data)
    leads_ids = []
    for ad_id in ads_ids:
        ad_leads_ids = await get_leads_ids_from_ad(config, ad_id)
        leads_ids.extend(ad_leads_ids)
    if leads_ids == []: raise NoNewLeads
    await update_last_update_time(config, int(time.time())) 
    leads_datas = await get_leads_data(leads_ids, config)
    leads = parse_leads(leads_datas)
    return leads

async def get_leads_data(leads_ids: list[int], config: Config) -> list[dict]:
    leads = []
    for lead_id in leads_ids:
        get_lead_info_url = FACEBOOK_GET_LEAD_INFO_URL.format(
            lead_id=lead_id,
            access_token=config.facebook.access_token,
            )
        lead_data = await request('get', get_lead_info_url)
        logging.debug(f'Facebook lead info: {lead_data}')
        leads.append(lead_data)
    return leads

def parse_leads(leads: Iterable[dict]) -> list[Lead]:
    parsed_leads = []
    for lead in leads:
        try:
            parsed_leads.append(Lead.parse_lead(lead))
        except pydantic.error_wrappers.ValidationError as exception:
            logger = logging.getLogger(__name__)
            logger.debug(f'Invalid lead: {lead}, error: {exception}')
    return parsed_leads
        

def get_ads_ids(data: dict) -> Iterable[int]:
    logging.debug(f'Facebook forms: {data}')
    for form in data['data']:
        if form['status'] == 'ACTIVE':
            yield form['id']

async def get_leads_ids_from_ad(config: Config, ad_id: int) -> list[int]:
    last_update_time = await get_last_update_time(config)
    get_leads_url = GET_LEADS_API_URL.format(
        ad_id=ad_id,
        access_token=config.facebook.access_token,
        ) + FACEBOOK_API_FILTER.format(
            filter=str(
                {
                    'field': 'time_created',
                    'operator': 'GREATER_THAN',
                    'value': last_update_time,
                }
            )
        )
    data = await request('get', get_leads_url, expected_status=(200, 400))
    if data.get('error'):
        return []
    logging.debug(f'Facebook leads: {data}')
    leads = list(lead['id'] for lead in data['data'])
    return leads






