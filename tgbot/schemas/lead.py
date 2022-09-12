import datetime
import logging
import re

from pydantic import BaseModel, validator



class Lead(BaseModel):
    id: str
    form_id: str = None
    created_time: datetime.datetime
    phone: str
    name: str
    
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
        if isinstance(input_time, str):
            return datetime.datetime.strptime(input_time, '%Y-%m-%d %H:%M:%S%z')
        return input_time

    @classmethod
    def parse_lead(cls, lead: dict) -> 'Lead':
        for field in lead['field_data']:
            if 'phone_number' == field['name']:
                phone = field['values'][0]
            elif 'name' in field['name']:
                name = field['values'][0]
        logging.debug(f'Phone: {phone}, name: {name}')
        return cls(
            id=lead['id'],
            form_id=lead['form_id'],
            created_time=lead['created_time'],
            name=name,
            phone=phone
            )