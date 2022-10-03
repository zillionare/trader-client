"""for performance and demo testing
"""
import datetime
import uuid

from traderclient.client import TraderClient


def demo():
    """demo basic usage"""
    url = "http://192.168.100.114:7080/backtest/api/trade/v0.4/"
    # url = "http://192.168.100.112:3180/backtest/api/trade/v0.3"

    token = uuid.uuid4().hex
    account = f"my-great-strategy-v1-{token[-4:]}"
    start = datetime.date(2022, 3, 1)
    end = datetime.date(2022, 3, 14)
    client: TraderClient = TraderClient(
        url, account, token, is_backtest=True, start=start, end=end
    )

    code = "002537.XSHE"

    buy = client.buy(code, 16, 200, order_time="2022-03-01 09:31:00")
    print(buy)

    sell = client.sell_percent(
        code, 9, 0.5, order_time=datetime.datetime(2022, 3, 4, 14, 57)
    )
    print(sell)
    sell = client.sell(code, 9, 1000, order_time="2022-03-07 14:57:00")
    print(sell)

    print(client.metrics())
    print(client.bills())
    print(client.get_assets())


def benchmark():
    # https://github.com/zillionare/backtesting/issues/6
    # url = "http://192.168.100.112:3180/backtest/api/trade/v0.3"
    url = "http://192.168.100.130:8000/api/trade/v0.1/"

    token = uuid.uuid4().hex
    account = f"my-great-strategy-v1-{token[-4:]}"
    start = datetime.date(2015, 1, 5)
    end = datetime.date(2022, 3, 14)
    client: TraderClient = TraderClient(url, account, token)

    import time

    t0 = time.time()
    for code in [f"{i:06d}.XSHE" for i in range(1, 150)]:
        try:
            client.market_buy(code, 100, order_time="2015-01-05 09:31:00")
        except Exception:
            pass

    print(client.positions())
    client.market_sell(
        "000001.XSHE", 100, order_time="2022-03-14 09:31:00", timeout=60 * 10
    )
    print("time cost:", time.time() - t0)


def debug_bills():
    url = "http://192.168.100.114:7080/backtest/api/trade/v0.4"
    token = "bGZJGEZ"

    accounts = TraderClient.list_accounts(url, token)

    client = TraderClient(url, "an-v1-8a74", "065b7772bfc040e8bcc11fd947d88a74", False)
    bills = client.bills()
    print(bills)


def debug_issue_23():
    url = "http://192.168.100.114:7080/backtest/api/trade/v0.4"
    token = uuid.uuid4().hex
    acct = "issue_23"

    client = TraderClient(
        url,
        acct,
        token,
        is_backtest=True,
        start=datetime.date(2022, 3, 18),
        end=datetime.date(2022, 8, 23),
    )

    code = "000732.XSHE"
    trades = """2022-03-29,买入,000732.XSHE,295300.0,3.07,90.66
2022-04-01,卖出,000732.XSHE,295300.0,3.36,99.22
2022-04-06,买入,000732.XSHE,298500.0,3.52,105.07
2022-04-08,卖出,000732.XSHE,298500.0,3.08,91.94
2022-08-16,买入,000732.XSHE,760100.0,1.26,95.77"""
    import arrow

    for line in trades.splitlines():
        if line:
            dt, side, code, volume, price, fee = line.split(",")
            if side == "买入":
                order_time = arrow.get(dt).shift(hours=9, minutes=31)
                client.buy(
                    code, float(price), float(volume), order_time=order_time.naive
                )
            else:
                order_time = arrow.get(dt).shift(hours=9, minutes=31)
                client.sell(
                    code, float(price), float(volume), order_time=order_time.naive
                )

    assets = client.get_assets()
    print(assets)


def debug_issue_26():
    import arrow

    url = "http://192.168.100.112:3180/backtest/api/trade/v0.4/"
    token = uuid.uuid4().hex
    account = f"my-great-strategy-v1-{token[-4:]}"
    start = datetime.date(2020, 4, 1)
    end = datetime.date(2022, 6, 28)

    client: TraderClient = TraderClient(
        url, account, token, is_backtest=True, start=start, end=end
    )

    r = client.market_buy(
        security="600892.XSHG",
        volume=63500.0,
        order_time=arrow.get("2020-04-27 09:32").naive,
    )
    r = client.market_sell(
        security="600892.XSHG",
        volume=63500.0,
        order_time=arrow.get("2020-05-11 09:31").naive,
    )


if __name__ == "__main__":
    # benchmark()
    # debug_bills()
    demo()
    # debug_issue_26()
