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
    token = "29b7cce7-e9bb-4510-9231-6d492750b4db"
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
    token = "29b7cce7-e9bb-4510-9231-6d492750b4db"
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
    token = "29b7cce7-e9bb-4510-9231-6d492750b4db"

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
    token = "29b7cce7-e9bb-4510-9231-6d492750b4db"

    # initialize client instance
    client = TraderClient(url, acct, token)

    print("\n------------- cancel_entrust --------------")
    result = client.cancel_entrust("50f5aaee-6fa8-470c-a630-39b43bc9dda7")
    if result is None:
        return None
    print(result)


def test_trade_cancel_all():
    url = "http://192.168.100.133:8000/api/trade/v0.1"
    acct = "henry"
    token = "29b7cce7-e9bb-4510-9231-6d492750b4db"

    # initialize client instance
    client = TraderClient(url, acct, token)

    print("\n------------- cancel_all_entrust --------------")
    result = client.cancel_all_entrusts()
    print(result)


def test_trade_buy():
    url = "http://192.168.100.133:8000/api/trade/v0.1"
    acct = "henry"
    token = "29b7cce7-e9bb-4510-9231-6d492750b4db"

    # initialize client instance
    client = TraderClient(url, acct, token)

    # test buy
    print("\n------------- buy --------------")
    result = client.buy(security="002537.XSHE", price=8.45, volume=200)
    if result is None:
        return None
    print(result)
    # buy for cancel
    result = client.buy(security="002537.XSHE", price=6.97, volume=600)
    if result is None:
        return None
    print(result)


def test_trade_market_buy():
    url = "http://192.168.100.133:8000/api/trade/v0.1"
    acct = "henry"
    token = "29b7cce7-e9bb-4510-9231-6d492750b4db"

    # initialize client instance
    client = TraderClient(url, acct, token)

    print("\n------------- market_buy --------------")
    rsp = client.market_buy(security="002537.XSHE", price=7.8, volume=500)
    print(rsp)


def test_for_nginx():
    url = "http://203.189.206.225:9100/api/trade/v0.1"
    acct = "guobotest"
    token = "b1733675-f525-49e9-82c4-a91360ec36e6"

    # initialize client instance
    client = TraderClient(url, acct, token)

    try:
        result = client.info()
        if result is None:
            logger.error("failed to get information")
        print(result)
    except Exception as e:
        print(e)


def test_trade_sell():
    url = "http://192.168.100.133:8000/api/trade/v0.1"
    acct = "henry"
    token = "29b7cce7-e9bb-4510-9231-6d492750b4db"

    # initialize client instance
    client = TraderClient(url, acct, token)

    print("\n------------- sell --------------")
    rsp = client.sell(security="002537.XSHE", price=9.9, volume=200)
    print(rsp)

    print("\n------------- market_sell ---------------")
    rsp = client.market_sell(security="002537.XSHE", price=9.7, volume=400)
    print(rsp)


def test_sell_percent():
    url = "http://192.168.100.19:9000/backtest/api/trade/v0.1"
    acct = "henry"
    token = "29b7cce7-e9bb-4510-9231-6d492750b4db"

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
    acct = "henry"
    token = "29b7cce7-e9bb-4510-9231-6d492750b4db"

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
    acct = "henry"
    token = "29b7cce7-e9bb-4510-9231-6d492750b4db"

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


def trade_test_entry():
    test_trade_market_buy()


if __name__ == "__main__":
    test_for_nginx()
