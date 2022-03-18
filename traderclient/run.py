# -*- coding: utf-8 -*-
# @Author   : henry
# @Time     : 2022-03-09 15:08
import logging

from traderclient import TradeClient


def enable_logging(level: str = "info"):
    logger = logging.getLogger()

    handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt="------%(message)s")
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

    print("\n------------- info --------------")
    rsp = client.info()
    print(rsp)

    print("\n------------- balance --------------")
    rsp = client.balance()
    print(rsp)

    print("\n------------- available_money --------------")
    rsp = client.available_money()
    print(rsp["available"])

    print("\n------------- positions --------------")
    rsp = client.positions()
    for position in rsp:
        print(position)

    print("\n------------- available_shares --------------")
    rsp = client.available_shares("600000")
    print(rsp["sellable"])

    print("\n------------- today_entrusts --------------")
    rsp = client.today_entrusts()
    for entrust in rsp:
        print(entrust)

    print("\n------------- today_trades --------------")
    rsp = client.today_trades()
    for trade in rsp:
        print(trade)

    print("\n------------- cancel_entrust --------------")
    rsp = client.cancel_entrust("xxx-xxx-xxx-xxxxxxx")
    print(rsp)

    print("\n------------- cancel_all_entrust --------------")
    rsp = client.cancel_all_entrusts()
    print(rsp)

    # test buy
    print("\n------------- buy --------------")
    order = client.set_trade_entrust("002537.XSHE", 200, 9.9)
    rsp = client.buy()
    print(order.toDict())

    """

    print("\n------------- market_buy --------------")
    order = client.set_trade_entrust("002537.XSHE", 200, 9.9)
    order.set_limit_price(10.11)
    rsp = client.market_buy()
    print(rsp)

    print("\n------------- sell --------------")
    order = client.set_trade_entrust("002537.XSHE", 200, 9.9)
    rsp = client.sell()
    print(rsp)

    print("\n------------- market_sell ---------------")
    order = client.set_trade_entrust("002537.XSHE", 200, 9.9)
    order.set_limit_price(10.11)
    rsp = client.market_sell()
    print(rsp)

    """
