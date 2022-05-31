import datetime
import unittest

import httpx

from tests import MockServer, get_free_port
from traderclient.client import TraderClient
from traderclient.errors import TradeError
from traderclient.transport import process_response_result
from traderclient.utils import enable_logging


class TransportTest(unittest.TestCase):
    def setUp(self):
        enable_logging("info")
        self.port = get_free_port()
        self.mock_server = MockServer("localhost", self.port)
        self.mock_server.run()

        self.url = f"http://localhost:{self.port}/"
        self.client = TraderClient(self.url, "test", "test")

    def tearDown(self) -> None:
        self.mock_server.stop()
        return super().tearDown()

    def test_process_response_result(self):
        r = httpx.get(
            self.url + "echo",
            params={"status": 421, "reason": "no enough shares to sell"},
        )

        with self.assertRaises(httpx.HTTPStatusError):
            process_response_result(r)

        r = httpx.post(self.url + "echo", json={"security": "000001.XSHE"})

        data = process_response_result(r)
        self.assertDictEqual(data, {"security": "000001.XSHE"})

        r = httpx.get(
            self.url + "echo",
            params={
                "status": 499,
                "reason": "no enough shares to sell",
                "data": {"security": "000001.XSHE"},
            },
        )

        with self.assertRaises(TradeError) as cm:
            process_response_result(r)

        self.assertEqual(cm.exception.code, 499)
        self.assertEqual(cm.exception.message, "no enough shares to sell")
