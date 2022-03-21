# -*- coding: utf-8 -*-
# @Author   : henry
# @Time     : 2022-03-09 15:08
import datetime
import logging

from traderclient import TradeClient


def init_logging(level=logging.INFO):
    logger = logging.getLogger()

    handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt="---%(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(level)


def test_functions():
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


def test_trade_functions():
    url = "http://192.168.100.19:9000/backtest/api/trade/v0.1"
    acct = "仿真_张三_策略1"
    token = "ec31c154fc0cbf4ba39eb48689ebcbfaacf8067f"

    # initialize client instance
    client = TradeClient(url, acct, token)

    # test buy
    print("\n------------- buy --------------")
    client.set_trade_entrust("002537.XSHE", 200, 9.9)
    rsp = client.buy()
    print(rsp)
    print(client.order.toDict())

    print("\n------------- backtest buy --------------")
    # for backtest, add trade time
    order = client.set_trade_entrust("002537.XSHE", 200, 9.9)
    # set trade time
    trade_date = datetime.datetime(2022, 3, 1, 9, 35)
    # pass trade time as an optional parameter
    rsp = client.buy(order_time=trade_date.isoformat())
    print(rsp)
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


if __name__ == "__main__":
    init_logging(logging.DEBUG)

    # test_functions()
    test_trade_functions()
