"""Unit test package for traderclient."""
import multiprocessing
import os
import pickle
import socket
import time
import uuid
from enum import IntEnum
from http.client import CONFLICT, FORBIDDEN, UNAUTHORIZED
from signal import SIGTERM

import arrow
import httpx
import numpy as np
from sanic import HTTPResponse, Sanic
from sanic import response as r

app = Sanic("__BASE__")
is_backtest = False


def assert_deep_almost_equal(test_case, expected, actual, *args, **kwargs):
    """
    copied from https://github.com/larsbutler/oq-engine/blob/master/tests/utils/helpers.py

    Assert that two complex structures have almost equal contents.
    Compares lists, dicts and tuples recursively. Checks numeric values
    using test_case's :py:meth:`unittest.TestCase.assertAlmostEqual` and
    checks all other values with :py:meth:`unittest.TestCase.assertEqual`.
    Accepts additional positional and keyword arguments and pass those
    intact to assertAlmostEqual() (that's how you specify comparison
    precision).
    :param test_case: TestCase object on which we can call all of the basic
        'assert' methods.
    :type test_case: :py:class:`unittest.TestCase` object
    """
    is_root = "__trace" not in kwargs
    trace = kwargs.pop("__trace", "ROOT")
    try:
        if isinstance(expected, (int, float, complex)):
            test_case.assertAlmostEqual(expected, actual, *args, **kwargs)
        elif isinstance(expected, (list, tuple, np.ndarray)):
            test_case.assertEqual(len(expected), len(actual))
            for index in range(len(expected)):
                v1, v2 = expected[index], actual[index]
                assert_deep_almost_equal(
                    test_case, v1, v2, __trace=repr(index), *args, **kwargs
                )
        elif isinstance(expected, dict):
            test_case.assertEqual(set(expected), set(actual))
            for key in expected:
                assert_deep_almost_equal(
                    test_case,
                    expected[key],
                    actual[key],
                    __trace=repr(key),
                    *args,
                    **kwargs,
                )
        else:
            test_case.assertEqual(expected, actual)
    except AssertionError as exc:
        exc.__dict__.setdefault("traces", []).append(trace)
        if is_root:
            trace = " -> ".join(reversed(exc.traces))
            exc = AssertionError("%s\nTRACE: %s" % (exc, trace))
        raise exc


class Status(IntEnum):
    """HTTP status code"""

    OK = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409

    SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    SERVICE_UNAVAILABLE = 503


@app.listener("after_server_start")
async def after_server_start(app, loop):
    print("server is started at ", app.config.get("SERVER_PORT"))


@app.route("/info", methods=["GET", "POST"])
async def info(request):
    data = {
        "name": "aaron",
        "principal": 1000000,
        "assets": 1_000_000,
        "start": arrow.now().format("YYYY-MM-DD HH:mm:ss"),
        "last_trade": arrow.now().format("YYYY-MM-DD HH:mm:ss"),
        "available": 9_000_00,
        "pnl": -1_000_00,
        "ppnl": -0.23,
        "market_value": 1_000_000,
        "positions": np.array(
            [
                ("000001.XSHE", "中国平安", 1000, 500, 9.2),
                ("600000.XSHG", "浦发银行", 2000, 1000, 12.3),
            ],
            dtype=[
                ("security", "O"),
                ("alias", "O"),
                ("shares", "<i4"),
                ("sellable", "<i4"),
                ("price", "<f4"),
            ],
        ),
    }

    return r.raw(pickle.dumps(data))


@app.post("/buy")
async def buy(request):
    global is_backtest

    params = request.json
    if "security" not in params or "volume" not in params:
        return r.text("Invalid params, security and volume are required", status=400)

    if is_backtest and "order_time" not in params:
        return r.text("Invalid params, order_time is required", status=400)

    order_time = params["order_time"] if is_backtest else arrow.now().isoformat()
    return r.raw(
        pickle.dumps(
            {
                "tid": uuid.uuid4().hex,
                "eid": uuid.uuid4().hex,
                "security": params["security"],
                "order_side": "买入",
                "price": params.get("price", 10.01),
                "volume": params["volume"],
                "time": order_time,
                "trade_fees": 0.51,
            }
        )
    )


@app.get("/positions")
async def positions(request):
    # 代码，名称，总股数，可卖数，成本均价
    dt = request.args.get("date")
    position = np.array(
        [
            ("000001.XSHE", "中国平安", 1000, 500, 9.2),
            ("600000.XSHG", "浦发银行", 2000, 1000, 12.3),
        ],
        dtype=[
            ("security", "O"),
            ("alias", "O"),
            ("shares", "<i4"),
            ("sellable", "<i4"),
            ("price", "<f4"),
        ],
    )

    return r.raw(pickle.dumps(position))


@app.get("/echo")
async def echo(request):
    status = request.args.get("status")
    reason = request.args.get("reason")
    data = request.args.get("data")

    if status == "200":
        body = data
    else:
        body = reason

    return r.text(body, status=int(status))


@app.post("/echo")
async def echo_post(request):
    return r.json(request.json)


def get_free_port():
    sock = socket.socket()
    try:
        sock.bind(("", 0))
        return sock.getsockname()[1]
    finally:
        sock.close()


class MockServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self._server = None
        self._loop = None
        self._process = None

    def run(self):
        mp = multiprocessing.get_context("fork")
        self._process = mp.Process(target=self._run_server)
        self._process.daemon = True
        self._process.start()
        is_ready = False
        while not is_ready:
            try:
                httpx.get(f"http://localhost:{self.port}")
            except httpx.ConnectError:
                time.sleep(0.1)
                continue
            else:
                is_ready = True

    def _run_server(self):
        print("Running server")
        app.run(host=self.host, port=self.port)

    def stop(self):
        os.kill(self._process.pid, SIGTERM)
        print("Stopping server")
        self._process.join()
        self._process.terminate()


if __name__ == "__main__":
    print(f"Main pid: {os.getpid()}")
    service = MockServer("localhost", get_free_port())
    service.run()

    time.sleep(3)
    print("Closing server in 3 seconds")
    time.sleep(3)

    service.stop()
