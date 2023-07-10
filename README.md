# Тестовое задание

<br>

Расписать примеры unit-тестов на следующую функцию:
```python
async def logs(cont, name):
    conn = aiohttp.UnixConnector(path="/var/run/docker.sock")
    async with aiohttp.ClientSession(connector=conn) as session:
        async with session.get(f"http://xx/containers/{cont}/logs?follow=1&stdout=1") as resp:
            async for line in resp.content:
                print(name, line)

import aiohttp


async def logs(container: str, name: str) -> None:
    connection = aiohttp.UnixConnector(path="/var/run/docker.sock")

    async with aiohttp.ClientSession(connector=connection) as session:
        path = f"http://xx/containers/{container}/logs"
        query = {"follow": 1, "stdout": 1}

        async with session.get(url=path, params=query) as response:
            async for line in response.content:
                print(name, line)

```
