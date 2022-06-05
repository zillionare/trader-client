# -*- coding: utf-8 -*-
# @Author   : henry
# @Time     : 2022-03-09 15:08
import datetime
import logging
import pickle

from traderclient import TraderClient

logger = logging.getLogger(__name__)


def init_logging(level=logging.INFO):
    logger = logging.getLogger()

    handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt="---%(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(level)


def test_info():
    url = "http://192.168.100.133:8000/api/trade/v0.1"
    acct = "henry"
    token = "b0dd8e56-2b5c-49fa-826d-08a9d0014fe0"
    client = TraderClient(url, acct, token)

    print("\n------------- info --------------")
    try:
        result = client.info()
        if result is None:
            logger.error("failed to get information")
            return None
        print(result)
    except Exception as e:
        print(e)
        return False

    print("\n------------- balance --------------")
    result = client.balance()
    print(result)

    tmp = client.principal
    print("principal: ", tmp)
    tmp = client.available_money
    print("available money: ", tmp)


def test_info_with_error():
    url = "http://192.168.100.133:8000/api/trade/v0.1"
    acct = "henry111111"
    token = "41e84e9a-c281-4ed3-86f3-01ef412f3970"
    client = TraderClient(url, acct, token)

    print("\n------------- info --------------")
    try:
        result = client.info()
        if result is None:
            logger.error("failed to get information")
            return None
        print(result)
    except Exception as e:
        print(e)
        return False


def test_position():
    url = "http://192.168.100.133:8000/api/trade/v0.1"
    acct = "henry"
    token = "b0dd8e56-2b5c-49fa-826d-08a9d0014fe0"
    client = TraderClient(url, acct, token)

    print("\n------------- positions --------------")
    try:
        result = client.positions()
        print(result)

        print("\n------------- available_shares --------------")
        result = client.available_shares("601118.XSHG")
        print(result)
    except Exception as e:
        print(e)
        return False


def test_entrusts():
    url = "http://192.168.100.133:8000/api/trade/v0.1"
    acct = "henry"
    token = "b0dd8e56-2b5c-49fa-826d-08a9d0014fe0"

    # initialize client instance
    client = TraderClient(url, acct, token)

    print("\n------------- today_entrusts --------------")
    result = client.today_entrusts()
    if result is None:
        return None

    print(result)


def test_trade_cancel():
    url = "http://192.168.100.133:8000/api/trade/v0.1"
    acct = "henry"
    token = "b0dd8e56-2b5c-49fa-826d-08a9d0014fe0"

    # initialize client instance
    client = TraderClient(url, acct, token)

    print("\n------------- cancel_entrust --------------")
    result = client.cancel_entrust("20f48ea9-cd92-4dad-86f0-4e8e925e8496")
    if result is None:
        return None

    print(result)

    print("\n------------- cancel_all_entrust --------------")
    result = client.cancel_all_entrusts()
    print(result)


def test_trade_buy():
    url = "http://192.168.100.133:8000/api/trade/v0.1"
    acct = "henry"
    token = "b0dd8e56-2b5c-49fa-826d-08a9d0014fe0"

    # initialize client instance
    client = TraderClient(url, acct, token)

    # test buy
    print("\n------------- buy --------------")
    result = client.buy(security="002537.XSHE", price=7.9, volume=200)
    if result is None:
        return None

    print(result)

    print("\n------------- market_buy --------------")
    rsp = client.market_buy(security="002537.XSHE", price=7.8, volume=500)
    print(rsp)


def test_trade_sell():
    url = "http://192.168.100.133:8000/api/trade/v0.1"
    acct = "henry"
    token = "b0dd8e56-2b5c-49fa-826d-08a9d0014fe0"

    # initialize client instance
    client = TraderClient(url, acct, token)

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
    client = TraderClient(url, acct, token)

    # test buy
    print("\n------------- sell_percent --------------")
    result = client.sell_percent("002537.XSHE", 0.2, 0.6)
    if result is None:
        return None

    print(result)


def test_sell_all():
    url = "http://192.168.100.19:9000/backtest/api/trade/v0.1"
    acct = "仿真_张三_策略1"
    token = "ec31c154fc0cbf4ba39eb48689ebcbfaacf8067f"

    # initialize client instance
    client = TraderClient(url, acct, token)

    # test buy
    print("\n------------- sell_all --------------")
    result = client.sell_all(0.2, 0.6)
    if result is None:
        return None

    print(result)


def test_get_data_in_range():
    url = "http://192.168.100.19:9000/backtest/api/trade/v0.1"
    acct = "仿真_张三_策略1"
    token = "ec31c154fc0cbf4ba39eb48689ebcbfaacf8067f"

    # initialize client instance
    client = TraderClient(url, acct, token)

    print("\n------------- get_trade_in_range --------------")

    start = datetime.datetime(2022, 3, 1, 9, 35)
    end = datetime.datetime(2022, 3, 10, 9, 35)
    result = client.get_trades_in_range(start=start, end=end)
    if result is None:
        return None

    print(result)

    print("\n------------- get_enturst_in_range --------------")

    start = datetime.datetime(2022, 3, 1, 9, 35)
    end = datetime.datetime(2022, 3, 10, 9, 35)
    result = client.get_entrusts_in_range(start=start, end=end)
    if result is None:
        return None

    print(result)


# the following fits backtesting server only


def backtest_trade():
    import uuid

    url = "http://192.168.100.114:7080/backtest/api/trade/v0.3/"

    token = uuid.uuid4().hex
    account = f"my-great-strategy-v1-{token[-4:]}"
    start = datetime.date(2022, 5, 18)
    end = datetime.date(2022, 5, 25)
    client: TraderClient = TraderClient(
        url, account, token, is_backtest=True, start=start, end=end
    )

    code = "000001.XSHE"

    buy = client.buy(code, 16, 200, order_time="2022-05-20 09:31:00")
    print(buy)

    sell = client.sell_percent(
        code, 10.1, 0.5, order_time=datetime.datetime(2022, 5, 23, 14, 57)
    )
    print(sell)
    sell = client.sell(code, 10.1, 1000, order_time="2022-05-23 14:57:00")
    print(sell)

    print(client.metrics())
    print(client.bills())
    print(client.get_assets())


if __name__ == "__main__":
    backtest_trade()
