# -*- coding: utf-8 -*-
# @Author   : henry
# @Time     : 2022-03-09 15:08
import datetime
import logging

from traderclient import OrderSide, OrderStatus, OrderType, TradeClient

logger = logging.getLogger(__name__)


def init_logging(level=logging.INFO):
    logger = logging.getLogger()

    handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt="---%(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(level)


def test_info():
    url = "http://192.168.100.19:9000/backtest/api/trade/v0.1"
    acct = "仿真_张三_策略1"
    token = "ec31c154fc0cbf4ba39eb48689ebcbfaacf8067f"

    # initialize client instance
    client = TradeClient(url, acct, token)

    print("\n------------- info --------------")
    result = client.info()
    if result is None:
        logger.error("failed to get information")
        return None

    if result["status"] != 0:
        logger.error("found errors in action: %d, %s", result["status"], result["msg"])
        return None

    if "data" not in result:
        logger.error("no data found in response, please check your parameters")
        return None

    print(result)

    print("\n------------- balance --------------")
    result = client.balance()
    print(result)

    print("\n------------- available_money --------------")
    result = client.available_money()
    print(result)

    print("\n------------- positions --------------")
    result = client.positions()
    print(result)

    print("\n------------- available_shares --------------")
    result = client.available_shares("600000")
    print(result)


def test_entrusts():
    url = "http://192.168.100.19:9000/backtest/api/trade/v0.1"
    acct = "仿真_张三_策略1"
    token = "ec31c154fc0cbf4ba39eb48689ebcbfaacf8067f"

    # initialize client instance
    client = TradeClient(url, acct, token)

    print("\n------------- today_entrusts --------------")
    result = client.today_entrusts()
    if result is None:
        return None

    if result["status"] != 0:
        logger.error("found errors in action: %d, %s", result["status"], result["msg"])
        return None

    if "data" not in result:
        logger.error("no data found in response, please check your parameters")
        return None

    print(result)

    print("\n------------- today_trades --------------")
    result = client.today_trades()
    print(result)


def test_functions():
    url = "http://192.168.100.19:9000/backtest/api/trade/v0.1"
    acct = "仿真_张三_策略1"
    token = "ec31c154fc0cbf4ba39eb48689ebcbfaacf8067f"

    # initialize client instance
    client = TradeClient(url, acct, token)

    print("\n------------- cancel_entrust --------------")
    result = client.cancel_entrust("xxx-xxx-xxx-xxxxxxx")
    if result is None:
        return None

    if result["status"] != 0:
        logger.error("found errors in action: %d, %s", result["status"], result["msg"])
        return None

    if "data" not in result:
        logger.error("no data found in response, please check your parameters")
        return None

    print(result)

    print("\n------------- cancel_all_entrust --------------")
    result = client.cancel_all_entrusts()
    print(result)


def test_trade_functions():
    url = "http://192.168.100.19:9000/backtest/api/trade/v0.1"
    acct = "仿真_张三_策略1"
    token = "ec31c154fc0cbf4ba39eb48689ebcbfaacf8067f"

    # initialize client instance
    client = TradeClient(url, acct, token)

    # test buy
    print("\n------------- buy --------------")
    result = client.buy(security="002537.XSHE", price=9.9, volume=200)
    if result is None:
        return None

    if result["status"] != 0:
        logger.error("found errors in action: %d, %s", result["status"], result["msg"])
        return None

    if "data" not in result:
        logger.error("no data found in response, please check your parameters")
        return None

    print(result)

    print("\n------------- backtest buy --------------")
    # for backtest, add trade time
    trade_date = datetime.datetime(2022, 3, 1, 9, 35)
    # pass trade time as an optional parameter
    rsp = client.buy(
        security="002537.XSHE", price=9.9, volume=200, order_time=trade_date.isoformat()
    )
    print(rsp)

    print("\n------------- market_buy --------------")
    rsp = client.market_buy(security="002537.XSHE", price=9.9, volume=200)
    print(rsp)

    print("\n------------- sell --------------")
    rsp = client.sell(security="002537.XSHE", price=9.9, volume=200)
    print(rsp)

    print("\n------------- market_sell ---------------")
    rsp = client.market_sell(security="002537.XSHE", price=9.9, volume=200)
    print(rsp)


def test_sell_percent():
    url = "http://192.168.100.19:9000/backtest/api/trade/v0.1"
    acct = "仿真_张三_策略1"
    token = "ec31c154fc0cbf4ba39eb48689ebcbfaacf8067f"

    # initialize client instance
    client = TradeClient(url, acct, token)

    # test buy
    print("\n------------- sell_percent --------------")
    result = client.sell_percent("002537.XSHE", 0.2, 0.6)
    if result is None:
        return None

    if result["status"] != 0:
        logger.error("found errors in action: %d, %s", result["status"], result["msg"])
        return None

    if "data" not in result:
        logger.error("no data found in response, please check your parameters")
        return None

    print(result)


def test_sell_all():
    url = "http://192.168.100.19:9000/backtest/api/trade/v0.1"
    acct = "仿真_张三_策略1"
    token = "ec31c154fc0cbf4ba39eb48689ebcbfaacf8067f"

    # initialize client instance
    client = TradeClient(url, acct, token)

    # test buy
    print("\n------------- sell_all --------------")
    result = client.sell_all(0.2, 0.6)
    if result is None:
        return None

    if result["status"] != 0:
        logger.error("found errors in action: %d, %s", result["status"], result["msg"])
        return None

    if "data" not in result:
        logger.error("no data found in response, please check your parameters")
        return None

    print(result)


def test_get_data_in_range():
    url = "http://192.168.100.19:9000/backtest/api/trade/v0.1"
    acct = "仿真_张三_策略1"
    token = "ec31c154fc0cbf4ba39eb48689ebcbfaacf8067f"

    # initialize client instance
    client = TradeClient(url, acct, token)

    print("\n------------- get_trade_in_range --------------")

    start = datetime.datetime(2022, 3, 1, 9, 35)
    end = datetime.datetime(2022, 3, 10, 9, 35)
    result = client.get_trades_in_range(start=start, end=end)
    if result is None:
        return None

    if result["status"] != 0:
        logger.error("found errors in action: %d, %s", result["status"], result["msg"])
        return None

    if "data" not in result:
        logger.error("no data found in response, please check your parameters")
        return None

    print(result)

    print("\n------------- get_enturst_in_range --------------")

    start = datetime.datetime(2022, 3, 1, 9, 35)
    end = datetime.datetime(2022, 3, 10, 9, 35)
    result = client.get_entrusts_in_range(start=start, end=end)
    if result is None:
        return None

    if result["status"] != 0:
        logger.error("found errors in action: %d, %s", result["status"], result["msg"])
        return None

    if "data" not in result:
        logger.error("no data found in response, please check your parameters")
        return None

    print(result)


if __name__ == "__main__":
    init_logging(logging.DEBUG)

    # test_info()
    # test_functions()
    # test_trade_functions()
    # test_sell_percent()
    # test_sell_all()
    # test_get_data_in_range()

    waiting = input("press any key to continue...")
    print(waiting)
