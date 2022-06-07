#!/usr/bin/env python
"""Tests for `traderclient` package."""
# pylint: disable=redefined-outer-name

import datetime
import unittest

import numpy as np

from tests import assert_deep_almost_equal
from traderclient.client import TraderClient
from traderclient.errors import TradeError
from traderclient.utils import enable_logging


class TraderClientWithBacktestServerTest(unittest.TestCase):
    def setUp(self):
        enable_logging("info")

        self.url = "http://localhost:3180/backtest/api/trade/v0.4"
        start = datetime.date(2022, 3, 1)
        end = datetime.date(2022, 3, 14)
        try:
            TraderClient.delete_account(self.url, "test", "test")
        except:
            pass

        # this also tested _start_backtest
        self.client = TraderClient(
            self.url, "test", "test", is_backtest=True, start=start, end=end
        )

    def tearDown(self) -> None:
        return super().tearDown()

    def test_buy(self):
        date = datetime.datetime(2022, 3, 1, 10, 4)
        r = self.client.buy("002537.XSHE", 10, 500, order_time=date)

        self.assertEqual(r["security"], "002537.XSHE")
        self.assertAlmostEqual(r["price"], 9.420000076293945, 2)
        self.assertEqual(r["filled"], 500)
        self.assertEqual(r["time"], date)

        # no excpetion is ok
        r = self.client.buy("002537.XSHE", 10, 500, order_time=date.isoformat())

    def test_info(self):
        # this also test available_money, balance
        info = self.client.info()
        self.assertEqual(info["available"], 1_000_000)
        self.assertEqual(info["assets"], 1_000_000)
        self.assertAlmostEqual(info["pnl"], 0, 2)

        self.client.buy(
            "002537.XSHE", 10, 500, order_time=datetime.datetime(2022, 3, 1, 10, 4)
        )

        info = self.client.info()
        self.assertAlmostEqual(info["available"], 995289.5289618492, 2)
        self.assertAlmostEqual(info["market_value"], 4750.0, 2)
        self.assertAlmostEqual(info["assets"], 1000039.528, 2)
        self.assertAlmostEqual(info["pnl"], 39.5289, 2)
        self.assertAlmostEqual(info["ppnl"], 39.5289 / 1_000_000, 2)
        self.assertEqual(datetime.date(2022, 3, 1), info["start"])
        self.assertEqual(datetime.date(2022, 3, 1), info["last_trade"])
        self.assertEqual(1_000_000, info["principal"])
        positions = info["positions"]

        self.assertListEqual(positions["security"].tolist(), ["002537.XSHE"])
        self.assertListEqual(positions["shares"].tolist(), [500])
        self.assertListEqual(positions["sellable"].tolist(), [0])
        np.testing.assert_array_almost_equal(positions["price"], [9.42], decimal=2)

        self.assertAlmostEqual(self.client.available_money, 995289.528, 2)
        balance = self.client.balance()
        self.assertAlmostEqual(balance["available"], 995289.528, 2)
        self.assertAlmostEqual(balance["market_value"], 4750, 2)
        self.assertAlmostEqual(balance["assets"], 1000039.528, 2)
        self.assertAlmostEqual(balance["pnl"], 39.5289, 2)
        self.assertAlmostEqual(balance["ppnl"], 39.5289 / 1_000_000, 2)

    def test_positions(self):
        # this also test available_shares
        positions = self.client.positions()
        self.assertEqual(0, positions.size)

        self.client.buy(
            "002537.XSHE", 10, 500, order_time=datetime.datetime(2022, 3, 1, 10, 4)
        )

        positions = self.client.positions()
        self.assertListEqual(positions["security"].tolist(), ["002537.XSHE"])
        self.assertListEqual(positions["shares"].tolist(), [500])
        self.assertListEqual(positions["sellable"].tolist(), [0])
        np.testing.assert_array_almost_equal(positions["price"], [9.42], decimal=2)

        positions = self.client.positions(datetime.date(2022, 3, 7))
        self.assertListEqual(positions["security"].tolist(), ["002537.XSHE"])
        self.assertListEqual(positions["shares"].tolist(), [500])
        self.assertListEqual(positions["sellable"].tolist(), [500])
        np.testing.assert_array_almost_equal(positions["price"], [9.42], decimal=2)

        # last_tradeday is still 2022, 3, 1, so the available_shares is 0
        r = self.client.available_shares("002537.XSHE")
        self.assertEqual(r, 0)

    def test_market_buy(self):
        r = self.client.market_buy(
            "002537.XSHE", 500, order_time=datetime.datetime(2022, 3, 1, 10, 4)
        )

        self.assertEqual(r["security"], "002537.XSHE")
        self.assertAlmostEqual(r["price"], 9.420000076293945, 2)
        self.assertEqual(r["filled"], 500)
        self.assertEqual(r["time"], datetime.datetime(2022, 3, 1, 10, 4))

    def test_market_sell(self):
        self.client.buy(
            "002537.XSHE", 10, 500, order_time=datetime.datetime(2022, 3, 1, 10, 4)
        )
        r = self.client.sell(
            "002537.XSHE", 10, 500, order_time=datetime.datetime(2022, 3, 2, 10, 4)
        )

        tx = r[0]
        self.assertEqual(tx["security"], "002537.XSHE")
        self.assertEqual(tx["filled"], 500)
        self.assertAlmostEqual(tx["price"], 10.45, 2)
        self.assertEqual(datetime.datetime(2022, 3, 2, 10, 4), tx["time"])

    def test_sell_percent(self):
        self.client.buy(
            "002537.XSHE", 10, 500, order_time=datetime.datetime(2022, 3, 1, 10, 4)
        )
        r = self.client.sell(
            "002537.XSHE", 10, 200, order_time=datetime.datetime(2022, 3, 2, 10, 4)
        )

        r = self.client.sell_percent(
            "002537.XSHE", 10, 1, order_time=datetime.datetime(2022, 3, 2, 10, 4)
        )

        tx = r[0]
        self.assertEqual(tx["security"], "002537.XSHE")
        self.assertEqual(tx["filled"], 300)
        self.assertAlmostEqual(tx["price"], 10.45, 2)
        self.assertEqual("2022-03-02T10:04:00", tx["time"])

    def test_metrics(self):
        # this also test bills, get_assets
        hljh = "002537.XSHE"

        for price, volume, tm in [
            (9.13, 500, "2022-03-01 09:31:00"),
            (10.03, 500, "2022-03-02 09:31:00"),
            (11.05, 500, "2022-03-03 09:31:00"),
            (10.47, 500, "2022-03-04 09:31:00"),
            (9.41, 500, "2022-03-07 09:31:00"),
            (9.57, 500, "2022-03-08 09:31:00"),
            (9.08, 500, "2022-03-09 09:31:00"),
            (9.1, 500, "2022-03-10 09:31:00"),
            (9.68, 500, "2022-03-11 09:31:00"),
            (9.65, 500, "2022-03-14 09:31:00"),
        ]:
            try:
                self.client.buy(hljh, price, volume, order_time=tm)
            except TradeError:
                pass

        self.client.sell(
            hljh, 9.1, 5000, order_time=datetime.datetime(2022, 3, 14, 15, 0)
        )

        actual = self.client.metrics(baseline=hljh)
        exp = {
            "start": datetime.date(2022, 3, 1),
            "end": datetime.date(2022, 3, 14),
            "window": 10,
            "total_tx": 9,
            "total_profit": -404.0999999998603,
            "total_profit_rate": -0.0004040999999998603,
            "win_rate": 0.5555555555555556,
            "mean_return": -3.896698729980441e-05,
            "sharpe": -1.396890251070207,
            "sortino": -2.0486727998320817,
            "calmar": -2.422741706100782,
            "max_drawdown": -0.0041827334569883405,
            "annual_return": -0.010133682791748755,
            "volatility": 0.02850594795764624,
            "baseline": {
                "code": "002537.XSHE",
                "win_rate": 0.5555555555555556,
                "sharpe": 0.6190437353475076,
                "max_drawdown": -0.17059373779725692,
                "sortino": 1.0015572769806516,
                "annual_return": 0.19278435493450163,
                "total_profit_rate": 0.006315946578979492,
                "volatility": 1.1038380776228978,
            },
        }

        assert_deep_almost_equal(self, exp, actual, places=2)

        bills = self.client.bills()
        # print(bills)

        start = datetime.date(2022, 3, 4)
        end = datetime.date(2022, 3, 10)
        assets = self.client.get_assets(start, end)
        print(assets)

        assets = self.client.get_assets()
        self.assertEqual(assets[0]["date"], datetime.date(2022, 3, 1))
        self.assertEqual(assets[-1]["date"], datetime.date(2022, 3, 14))

    def test_stop_backtest(self):
        self.client.stop_backtest()
