import asyncio
import gc
import logging
from json import loads

import pytest

from aiologstash2 import create_tcp_handler


logging.getLogger().setLevel(logging.DEBUG)


class FakeTcpServer:
    def __init__(self):
        self.data = bytearray()
        self.server = None
        self.futs = set()

    async def start(self):
        self.server = await asyncio.start_server(self.on_connect, host="127.0.0.1")

    @property
    def port(self):
        return self.server.sockets[0].getsockname()[1]

    @property
    def jsons(self):
        s = self.data.decode("utf8")
        return [loads(i) for i in s.split("\n") if i]

    async def close(self):
        if self.server is None:
            return
        self.server.close()
        await self.server.wait_closed()
        self.server = None

    async def on_connect(self, reader, writer):
        while True:
            data = await reader.read(1024)
            if not data:
                break
            self.data.extend(data)
            for fut in self.futs:
                if not fut.done():
                    fut.set_result(None)

    async def wait(self):
        fut = asyncio.get_event_loop().create_future()
        self.futs.add(fut)
        await fut
        self.futs.remove(fut)


@pytest.fixture
async def make_tcp_server():
    servers = []

    async def go():
        server = FakeTcpServer()
        await server.start()
        servers.append(server)
        return server

    yield go

    async def finalize():
        for server in servers:
            await server.close()

    await finalize()


@pytest.fixture
async def make_tcp_handler(make_tcp_server):
    handlers = []

    async def go(*args, level=logging.DEBUG, **kwargs):
        server = await make_tcp_server()
        handler = await create_tcp_handler("127.0.0.1", server.port, **kwargs)
        handlers.append(handler)
        return handler, server

    yield go

    async def finalize():
        for handler in handlers:
            handler.close()
            await handler.wait_closed()

    await finalize()


@pytest.fixture
async def setup_logger(make_tcp_handler):
    async def go(*args, **kwargs):
        handler, server = await make_tcp_handler(*args, **kwargs)
        logger = logging.getLogger("aiologstash_test")
        logger.addHandler(handler)
        return logger, handler, server

    yield go
