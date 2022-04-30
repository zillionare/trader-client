#!/usr/bin/env python
"""Tests for `traderclient` package."""
# pylint: disable=redefined-outer-name

import datetime
import os
import unittest
import uuid

from traderclient.client import TradeClient
from traderclient.utils import enable_logging


class TraderClientTest(unittest.TestCase):
    def setUp(self):
        enable_logging("info")
        # url = "http://192.168.100.114:7080/backtest/api/trade/v0.2"
        url = "http://localhost:3180/backtest/api/trade/v0.2"
        name = "backtest-ut"

        # disable proxy, if any
        os.environ["http_proxy"] = ""
        os.environ["https_proxy"] = ""

        start = datetime.date(2022, 3, 1)
        end = datetime.date(2022, 3, 31)

        admin_token = os.environ.get("TRADER_ADMIN_TOKEN")
        TradeClient.delete_account(url, admin_token, name)
        self.client = TradeClient(
            url, name, uuid.uuid4().hex, is_backtest=True, start=start, end=end
        )

    def test_buy(self):
        """注意这里并非完整的测试用例，只是为了演示如何使用"""
        date = datetime.datetime(2022, 3, 1, 9, 35)
        r = self.client.buy("002537.XSHE", 9.8, 100, order_time=date.isoformat())
        data = r["data"]

        self.assertTrue(
            {
                "tid",
                "eid",
                "security",
                "order_side",
                "price",
                "volume",
                "time",
                "trade_fees",
            }.issubset(data)
        )

    def test_info(self):
        r = self.client.info()
        self.assertTrue(
            {"capital", "assets", "name", "trades", "start", "last_trade"}.issubset(
                r["data"]
            )
        )

    def test_balance(self):
        r = self.client.balance()
        self.assertTrue(
            {"account", "pnl", "available", "market_value", "total", "ppnl"}.issubset(
                r["data"]
            )
        )

    def test_available_money(self):
        import numbers

        r = self.client.available_money()
        self.assertTrue(isinstance(r["data"], numbers.Number))

    def test_positions(self):
        r = self.client.positions()
        print(r)

    def test_available_shares(self):
        date = datetime.datetime(2022, 3, 1, 9, 35)
        r = self.client.buy("002537.XSHE", 9.8, 100, order_time=date.isoformat())

        r = self.client.available_shares("002537.XSHE")
        self.assertDictEqual(r["data"], {"002537.XSHE": 0})

    def test_sell(self):
        date = datetime.datetime(2022, 3, 1, 9, 35)
        self.client.buy("002537.XSHE", 9.8, 100, order_time=date.isoformat())

        r = self.client.sell("002537.XSHE", 9.8, 100, order_time="2022-03-02 09:35:00")
        self.assertEqual(1, len(r["data"]))

        data = r["data"][0]
        self.assertTrue(
            {
                "tid",
                "eid",
                "security",
                "order_side",
                "price",
                "volume",
                "time",
                "trade_fees",
            }.issubset(data)
        )

    def test_metrics(self):
        date = datetime.datetime(2022, 3, 1, 9, 35)
        self.client.buy("002537.XSHE", 9.8, 100, order_time=date.isoformat())
        self.client.sell("002537.XSHE", 9.8, 100, order_time="2022-03-02 09:35:00")

        r = self.client.metrics()
        self.assertSetEqual(
            {
                "start",
                "end",
                "window",
                "total_tx",
                "total_profit",
                "total_profit_rate",
                "win_rate",
                "mean_return",
                "sharpe",
                "sortino",
                "calmar",
                "max_drawdown",
                "annual_return",
                "volatility",
                "baseline",
            },
            set(r.keys()),
        )

    def test_bills(self):
        r = self.client.bills()
        self.assertIn("tx", r)
        self.assertIn("trades", r)
        self.assertIn("positions", r)
        self.assertIn("assets", r)
