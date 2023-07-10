# Тестовое задание

<br>

Расписать примеры unit-тестов на следующую функцию:
```python
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

<br>

## Запуск тестов

**NOTE:** Все тесты запускаются из корневого каталога проекта.

<br>

Полный набор:
```shell
user@host ~/project-dir $ pytest
```
Только рекомендуемый набор:
```shell
user@host ~/project-dir $ pytest -m logs
```

Только aiohttp-специфичные тесты:
```shell
user@host ~/project-dir $ pytest -m logs_aiohttp_specific
```
