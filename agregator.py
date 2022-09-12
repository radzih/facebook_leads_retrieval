import asyncio
import logging
from apscheduler.schedulers.blocking import BlockingScheduler

from tgbot.misc.setup_django import setup_django; setup_django()
from tgbot.config import load_config
from leads_agregator.facebook import get_leads
from leads_agregator.db import write_leads_to_db
from leads_agregator.exceptions.agregator_exceptions import NoNewLeads


def main():
    config = load_config()
    try:
        leads = asyncio.run(get_leads(config))
    except NoNewLeads:
        return
    logger = logging.getLogger('leads_agregator')
    logger.info(f'Got {len(leads)} leads')
    write_leads_to_db(leads)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    ) 
    logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)
    logger.info("Starting agregator")
    scheduler = BlockingScheduler()
    scheduler.add_job(main, 'interval', seconds=5)
    scheduler.start()
