[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)


[![codecov](https://codecov.io/gh/SciBourne/test-task--docker-logs-unit-tests/branch/main/graph/badge.svg?token=OGV48MY9TY)](https://codecov.io/gh/SciBourne/test-task--docker-logs-unit-tests)
[![gitlab-ci: build](http://scibourne.gitlab.io/test-task-docker-logs-unit-tests/build.svg)](https://gitlab.com/SciBourne/test-task-docker-logs-unit-tests)
[![gitlab-ci: type-check](http://scibourne.gitlab.io/test-task-docker-logs-unit-tests/type-check.svg)](https://gitlab.com/SciBourne/test-task-docker-logs-unit-tests)
[![gitlab-ci: unit-tests](http://scibourne.gitlab.io/test-task-docker-logs-unit-tests/unit-tests.svg)](https://gitlab.com/SciBourne/test-task-docker-logs-unit-tests)
[![gitlab-ci: aiohttp-specific-tests](http://scibourne.gitlab.io/test-task-docker-logs-unit-tests/aiohttp-specific-tests.svg)](https://gitlab.com/SciBourne/test-task-docker-logs-unit-tests)


<br>

# Тестовое задание `#Webtronics`

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
git clone https://github.com/SciBourne/test-task--docker-logs-unit-tests.git
cd test-task--docker-logs-unit-tests

poetry env use python3.11
poetry install
```

<br>

Полный набор:
```shell
poetry run pytest
```
Только рекомендуемый набор:
```shell
poetry run pytest -m logs
```

Только aiohttp-специфичные тесты:
```shell
poetry run pytest -m logs_aiohttp_specific
```

<br>

## Описание

<br>

### Рекомендуемый набор

Для рекомендуемого набора тестов, объединённых под классом `TestLogs`, не принципиально, какой в функции `logs` используется http-клиент. Изолируясь stub-сервером и mock-объектами, проверяется, действительно ли функция устанавливает соединение средствами **HTTP** поверх **Unix Domain Socket**, в частности, подразумевается получение доступа к **Docker API**, принимает поток данных журнала в виде строк и выводит их на печать в `stdout`.

Функция должна быть относительно эквивалентна запросу:
```shell
curl --unix-socket /var/run/docker.sock http://xx/containers/9c0aae524a78/logs
```

<br>

### aiohttp-специфичный набор

В этом наборе производится подмена методов aiohttp-клиента, используемого в функции. При изменении кода как самой aiohttp, так и тела функции (пусть и при условии сохранения прежней функциональности), скорее всего приведёт к неработоспособности этого набора.
