from contextlib import asynccontextmanager
import socket

import pytest
from yarl import URL

from aiohttp.web import (
    Application,
    Request,
    Response,
    AppRunner,
    UnixSite
)

from aiohttp import (
    UnixConnector,
    ClientSession,
    ClientResponse
)

from logs_docker_containers.main import logs


@pytest.mark.logs
class TestLogs:

    DUMMY_CONTAINER_ID = "9c0aae524a78"
    DUMMY_NAME = "hyper_app"

    DUMMY_CONTENT = (
        "[ info ]: message 0x01\n"
        "[ info ]: message 0x02\n"
        "[ info ]: message 0x03\n"
    )

    DOCKER_SOCKET_PATH = "/var/run/docker.sock"
    FAKE_SOCKET_PATH = "/tmp/docker.sock"

    URL_METHOD = "GET"
    URL_HOST = "xx"
    URL_PATH = f"/containers/{DUMMY_CONTAINER_ID}/logs"
    URL_QUERY = {"follow": "1", "stdout": "1"}

    CONTROL_CONTENT = (
        f"{DUMMY_NAME} b'[ info ]: message 0x01\\n'\n"
        f"{DUMMY_NAME} b'[ info ]: message 0x02\\n'\n"
        f"{DUMMY_NAME} b'[ info ]: message 0x03\\n'\n"
    )

    arg_buffer: dict = {}

    @pytest.fixture
    def patch_socket_connect(self, monkeypatch):
        def patch(set_path: str):
            def mock_socket_connect(sock: socket.socket, path: str) -> None:
                self.arg_buffer.update(socket_path=path)
                monkeypatch.undo()
                sock.connect(set_path)

            monkeypatch.setattr(socket.socket, "connect", mock_socket_connect)
            monkeypatch.setattr(socket.socket, "bind", mock_socket_connect)

        return patch

    async def mock_handler(self, request: Request) -> Response:
        self.arg_buffer.update(
            url_method=request.method,
            url_host=request.host,
            url_path=request.path,
            url_query=request.query
        )

        return Response(text=self.DUMMY_CONTENT)

    @asynccontextmanager
    async def stub_server(self, handler) -> UnixSite:
        app = Application()

        app.router.add_get(
            path="/{any_path:.*}",
            handler=handler
        )

        try:
            runner = AppRunner(app)
            await runner.setup()

            site = UnixSite(runner, path=self.FAKE_SOCKET_PATH)
            await site.start()

            yield

        finally:
            await site.stop()

    @pytest.mark.asyncio
    async def test_logs_get_stream_data(self, patch_socket_connect, capsys):
        async with self.stub_server(handler=self.mock_handler):
            patch_socket_connect(set_path=self.FAKE_SOCKET_PATH)

            await logs(
                container=self.DUMMY_CONTAINER_ID,
                name=self.DUMMY_NAME
            )

        assert capsys.readouterr().out == self.CONTROL_CONTENT

    @pytest.mark.asyncio
    async def test_logs_docker_api_socket_path(self):
        assert self.arg_buffer.get("socket_path") == self.DOCKER_SOCKET_PATH

    @pytest.mark.asyncio
    async def test_logs_docker_api_url(self):
        assert self.arg_buffer.get("url_method") == self.URL_METHOD
        assert self.arg_buffer.get("url_host") == self.URL_HOST
        assert self.arg_buffer.get("url_path") == self.URL_PATH
        assert self.arg_buffer.get("url_query") == self.URL_QUERY


class FakeAsyncIterator:
    def __init__(self, data: list[str]):
        self._iterator = iter(data)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._iterator)
        except StopIteration:
            raise StopAsyncIteration


class FakeRequestContextManager:
    def __init__(self, content: list[str]):
        self.content = FakeAsyncIterator(content)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


@pytest.mark.logs_aiohttp_specific
class TestLogsAiohttpSpecific:
    DUMMY_CONTAINER = "container_id"
    DUMMY_NAME = "name"

    DUMMY_CONTENT = [
        "[ info ]: message 0x01",
        "[ info ]: message 0x02",
        "[ info ]: message 0x03"
    ]

    CONTROL_STDOUT = (
        f"{DUMMY_NAME} [ info ]: message 0x01\n"
        f"{DUMMY_NAME} [ info ]: message 0x02\n"
        f"{DUMMY_NAME} [ info ]: message 0x03\n"
    )

    CONTROL_CONNECTOR_TYPE = UnixConnector
    CONTROL_UNIX_SOCKET_PATH = "/var/run/docker.sock"

    CONTROL_URL = URL(
        f"http://xx/containers/{DUMMY_CONTAINER}/logs?follow=1&stdout=1"
    )

    arg_buffer = {
        "args": None,
        "kwargs": None
    }

    def get_stub(self, *args, **kwargs):
        return FakeRequestContextManager(content=self.DUMMY_CONTENT)

    def args_capture(self, *args, **kwargs):
        self.arg_buffer.update(args=args, kwargs=kwargs)

    @pytest.mark.asyncio
    async def test_logs_content(self, monkeypatch, capsys):
        monkeypatch.setattr(
            ClientSession,
            "get",
            self.get_stub
        )

        await logs(
            container=self.DUMMY_CONTAINER,
            name=self.DUMMY_NAME
        )

        logs_content = capsys.readouterr()
        assert logs_content.out == self.CONTROL_STDOUT

    @pytest.mark.asyncio
    async def test_logs_connector(self, monkeypatch):
        self.arg_buffer.update(args=None, kwargs=None)

        monkeypatch.setattr(
            ClientSession,
            "__init__",
            self.args_capture
        )

        try:
            await logs(container=None, name=None)

        except Exception:
            for arg in self.arg_buffer["args"]:
                if isinstance(arg, self.CONTROL_CONNECTOR_TYPE):
                    assert arg.path == self.CONTROL_UNIX_SOCKET_PATH
                    return True
            else:
                connector = self.arg_buffer["kwargs"].get("connector")

                assert isinstance(connector, self.CONTROL_CONNECTOR_TYPE)
                assert connector.path == self.CONTROL_UNIX_SOCKET_PATH

    @pytest.mark.asyncio
    async def test_logs_url(self, monkeypatch):
        self.arg_buffer.update(args=None, kwargs=None)

        monkeypatch.setattr(
            ClientResponse,
            "__init__",
            self.args_capture
        )

        try:
            await logs(
                container=self.DUMMY_CONTAINER,
                name=None
            )

        except Exception:
            url = self.arg_buffer["args"][1]

            test_set = {
                url.scheme == self.CONTROL_URL.scheme,
                url.host == self.CONTROL_URL.host,
                url.path == self.CONTROL_URL.path,
                url.query == dict(self.CONTROL_URL.query)
            }

            assert all(test_set)
