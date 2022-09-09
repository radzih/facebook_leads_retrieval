from tgbot.misc.setup_django import setup_django; setup_django()
from tgbot.misc.facebook_polling import create_deal, create_person, get_last_worker_telegram_id, update_last_worker_telegram_id, get_last_update_time, Lead
from tgbot.config import load_config, Config
import asyncio

async def test():
    await create_deal(
        config=load_config(), 
        lead=Lead(
            id=1,
            form_id=1,
            created_time='2021-07-01T00:00:00+03:00',
            data='Name: Test\nPhone: +38000000000\n',   
        )
        )

asyncio.run(test())