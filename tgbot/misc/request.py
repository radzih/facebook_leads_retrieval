import json
import aiohttp
import logging

from typing import Literal

from leads_agregator.exceptions.agregator_exceptions import MissingPermissions


async def request(
    method: Literal['get', 'post'], 
    url: str, 
    expected_status: tuple = (200),
    **kwargs
    ) -> dict or str:
    if isinstance(expected_status, int):
        expected_status = (expected_status,)
    logger = logging.getLogger(__name__)
    logger.debug(f'Requesting {method} {url}')
    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, **kwargs) as response:
            if response.status not in expected_status:
                logger.error(
                    f'{response.status} {response.reason}\n'
                    f'{await response.text()}\n {url}{kwargs}'
                    )
                await session.close()
            response_data = await response.text()
            try:
                response_data = json.loads(response_data)
            except json.decoder.JSONDecodeError:
                pass
    return response_data