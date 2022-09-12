import json
import aiohttp
import logging

from typing import Literal


async def request(
    method: Literal['get', 'post'], 
    url: str, 
    expected_status: int = 200,
    **kwargs
    ) -> dict or str:
    logger = logging.getLogger(__name__)
    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, **kwargs) as response:
            if response.status != expected_status:
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