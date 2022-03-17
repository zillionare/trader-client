#!/usr/bin/env python
"""Tests for `traderclient` package."""
# pylint: disable=redefined-outer-name

import datetime
import unittest

from traderclient.client import TradeClient
from traderclient.utils import enable_logging


class TraderClientTest(unittest.TestCase):
    def setUp(self):
        enable_logging("info")
        url = "http://localhost:7080/backtest/api/trade/v0.1"
        self.client = TradeClient(url, "abcd")

    def test_buy(self):
        date = datetime.datetime(2022, 3, 1, 9, 35)
        r = self.client.buy("002537.XSHE", 9.8, 100, order_time=date.isoformat())
        print(r)

    def test_info(self):
        r = self.client.info()
        print(r)

    def test_balance(self):
        r = self.client.balance()
        print(r)

    def test_available_money(self):
        r = self.client.available_money()
        print(r)

    def test_position(self):
        r = self.client.positions()
        print(r)

    def test_available_shares(self):
        date = datetime.datetime(2022, 3, 1, 9, 35)
        r = self.client.buy("002537.XSHE", 9.8, 100, order_time=date.isoformat())

        r = self.client.available_shares()
        print(r)
