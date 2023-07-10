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

Сборка проекта:
```shell
user@host ~ $ git clone https://github.com/SciBourne/test-task--docker-logs-unit-tests.git
user@host ~ $ cd test-task--docker-logs-unit-tests

user@host ~/test-task--docker-logs-unit-tests $ poetry env use python 3.11
user@host ~/test-task--docker-logs-unit-tests $ poetry install
```

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

<br>

## Описание

<br>

### Рекомендуемый набор

Для рекомендуемого набора тестов, объединённых под классом `TestLogs`, не принципиально, какой в функции `logs` используется http-клиент. Изолируясь stub-сервером и mock-объектами, проверяется, действительно ли функция устанавливает соединение средствами **HTTP** поверх **Unix Domain Socket**, в частности, подразумевается получение доступа к **Docker API**, принимает поток данных журнала в виде строк и выводит их на печать в `stdout`.

Функция должна быть относительно эквивалентна запросу:
```shell
user@host ~/project $ curl --unix-socket /var/run/docker.sock http://xx/containers/9c0aae524a78/logs
```

<br>

### aiohttp-специфичный набор

В этом наборе производится подмена методов aiohttp-клиента, используемого в функции. При изменении кода как самой aiohttp, так и тела функции (пусть и при условии сохранения прежней функциональности), скорее всего приведёт к неработоспособности этого набора.
