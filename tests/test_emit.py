import asyncio
import threading
from unittest import mock

import pytest


pytestmark = pytest.mark.asyncio


async def test_emit_full_queue(setup_logger, mocker):
    log, hdlr, srv = await setup_logger(qsize=1, close_timeout=0.01)

    fut = asyncio.Future()

    async def coro(record):
        await fut

    hdlr._send = coro
    m_log = mocker.patch("aiologstash2.base_handler.logger")

    log.info("Msg 1")
    assert not m_log.called
    log.info("Msg 2")
    m_log.warning.assert_called_with(
        'Queue is full, drop oldest message: "%(record)s"', {"record": mock.ANY}
    )


async def test_emit_unexpected_err_in_worker(setup_logger, mocker):
    log, hdlr, srv = await setup_logger()

    err = ValueError()
    fut = asyncio.Future()

    async def coro(record):
        fut.set_result(None)
        raise err

    hdlr._send = coro
    m_log = mocker.patch("aiologstash2.base_handler.logger")

    log.info("Msg")
    await fut
    m_log.warning.assert_called_with(
        "Unexpected exception while sending log", exc_info=err
    )


async def test_reconnection(setup_logger, mocker):
    log, hdlr, srv = await setup_logger()

    m = mock.Mock()

    async def coro(record):
        m()

    hdlr._send = coro
    m_log = mocker.patch("aiologstash2.base_handler.logger")

    m.side_effect = [OSError(), None]
    log.info("Msg 1")
    await asyncio.sleep(0.1)
    m_log.info.assert_has_calls(
        [mock.call("Transport disconnected"), mock.call("Transport reconnected")]
    )
    assert m.call_count == 2


async def test_reconnection_failure(setup_logger, mocker):
    log, hdlr, srv = await setup_logger(reconnect_delay=0.1, reconnect_jitter=0)

    open_connection = asyncio.open_connection
    m = mocker.patch("aiologstash2.tcp_handler.asyncio.open_connection")

    flag = False

    async def switcher(*args, **kwargs):
        nonlocal flag
        if not flag:
            flag = True
            raise OSError()
        else:
            return await open_connection(*args, **kwargs)

    loop = asyncio.get_event_loop()
    m.side_effect = switcher
    t0 = loop.time()
    await hdlr._reconnect()
    assert hdlr._reader is not None
    t1 = loop.time()
    assert t1 - t0 > 0.08
    assert m.call_count == 2


async def test_emit_from_other_thread(setup_logger, mocker):
    log, hdlr, srv = await setup_logger()

    fut = asyncio.Future()

    async def coro(record):
        fut.set_result(record)

    hdlr._send = coro

    th = threading.Thread(target=log.info, args=("Msg",))
    th.start()
    th.join()
    rec = await fut
    assert b"Msg" in rec
