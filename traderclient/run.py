# -*- coding: utf-8 -*-
# @Author   : henry
# @Time     : 2022-03-09 15:08
import datetime
import logging
import os
import time

from traderclient import (
    BidType,
    OrderRequest,
    OrderResponse,
    OrderSide,
    OrderStatus,
    TradeClient,
    TradeOrder,
)


def enable_logging(level: str = "info"):
    logger = logging.getLogger()

    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    level = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }.get(level.lower(), logging.INFO)

    logger.setLevel(level)


if __name__ == "__main__":
    enable_logging("info")

    url = "http://192.168.100.19:9000/backtest/api/trade/v0.1"
    acct = "仿真_张三_策略1"
    token = "ec31c154fc0cbf4ba39eb48689ebcbfaacf8067f"

    # initialize client instance
    client = TradeClient(url, acct, token)

    rsp = client.info()
    print(rsp)

    rsp = client.balance()
    print(rsp)

    rsp = client.available_money()
    print(rsp["available"])

    rsp = client.positions()
    for position in rsp:
        print(position)

    rsp = client.available_shares("600000")
    print(rsp["sellable"])

    """
    # test buy
    order = TradeOrder("002537", 200, 9.9)
    rsp = client.buy(order)
    print(rsp)

    # test buy
    order = TradeOrder("002537", 200, 9.9)
    order.set_limit_price(10.11)
    rsp = client.market_buy(order)
    print(rsp)
    """
