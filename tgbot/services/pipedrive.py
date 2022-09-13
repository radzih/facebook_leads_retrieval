import logging
from tgbot.config import Config
from tgbot.schemas.lead import Lead
from tgbot.misc.request import request

async def create_deal(config: Config, lead: Lead) -> int:
    PIPEDRIVE_CREATE_DEAL_URL = \
        'https://{domain}.pipedrive.com/api/v1/deals?api_token={api_key}'
    person_id = await create_person(config, lead)
    data = await request(
        method='post',
        url=PIPEDRIVE_CREATE_DEAL_URL.format(
            domain=config.misc.pipedrive_domain,
            api_key=config.misc.pipedrive_api_key,
        ),
        data={
            'title': f'----{lead.name}----',
            'person_id': person_id,
            config.misc.pipedrive_platform_key: lead.platform,
            config.misc.pipedrive_ad_key: lead.ad_name,
            config.misc.pipedrive_adset_key: lead.adset_name,
            config.misc.pipedrive_campaign_key: lead.campaign_name,
            
        },
        expected_status=201,
    )
    logging.debug(f'Pipedrive deal created: {data}')
    return data['data']['id']
    
async def create_person(config: Config, lead: Lead):
    PIPEDRIVE_CREATE_PERSON_URL = \
        'https://{domain}.pipedrive.com/api/v1/persons?api_token={api_key}'
    person = await request(
        method='post',
        url=PIPEDRIVE_CREATE_PERSON_URL.format(
            domain=config.misc.pipedrive_domain,
            api_key=config.misc.pipedrive_api_key,
        ),
        data={
            'name': lead.name,
            'phone': [lead.phone],
        },
        expected_status=201,
    )
    return person['data']['id']
 