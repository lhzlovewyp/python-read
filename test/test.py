import asyncio
from aiohttp import ClientSession


async def hello():
    async with ClientSession() as session:
        async with session.get("https://api.github.com/events",ssl=False) as response:
            response = await response.read()
            print(response)


loop = asyncio.get_event_loop()
loop.run_until_complete(hello())