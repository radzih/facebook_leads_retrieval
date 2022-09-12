import datetime
import logging
from platform import platform
from typing import Any, Literal

from pydantic import BaseModel, validator


class Lead(BaseModel):
    id: str
    created_time: datetime.datetime
    phone: str
    name: str
    ad_name: str
    campaign_name: str
    adset_name: str
    platform: str
    
    @validator('phone')
    def phone_validator(cls, input_phone: str):
        if input_phone.startswith('<test lead'):
            input_phone = '380955048231'
        if len(input_phone) < 10: raise ValueError('Phone number is too short')
        elif len(input_phone) > 14: raise ValueError('Phone number is too long')
        phone_without_country_code = input_phone[-9:]
        logging.debug(f'Phone without country code: {phone_without_country_code}')
        return f'+380{phone_without_country_code}'
    
    @validator('created_time')
    def created_time_validator(cls, input_time):
        FACEBOOK_TIME_DIFFERENCE = 3
        if isinstance(input_time, str):
            created_time = datetime.datetime.strptime(input_time, '%Y-%m-%dT%H:%M:%S%z')
            return created_time + datetime.timedelta(
                hours=FACEBOOK_TIME_DIFFERENCE
                )
        return input_time + datetime.timedelta(
            hours=FACEBOOK_TIME_DIFFERENCE
        )
    
    @validator('platform')
    def platform_validator(cls, input_platform: str):
        if input_platform == 'fb':
            return 'Facebook'
        elif input_platform == 'ig':
            return 'Instagram'
        else:
            return input_platform

    @classmethod
    def parse_lead(cls, lead: dict) -> 'Lead':
        for field in lead['field_data']:
            if 'phone_number' == field['name']:
                phone = field['values'][0]
            elif 'name' in field['name']:
                name = field['values'][0]
        return cls(
            id=lead['id'],
            created_time=lead['created_time'],
            name=name,
            phone=phone,
            ad_name=lead['ad_name'],
            campaign_name=lead['campaign_name'],
            adset_name=lead['adset_name'],
            platform=lead['platform'],
            )