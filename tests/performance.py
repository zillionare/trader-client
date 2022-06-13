"""for performance and demo testing
"""
import datetime
import uuid

from traderclient.client import TraderClient


def demo():
    """demo basic usage"""
    # url = "http://192.168.100.114:7080/backtest/api/trade/v0.4/"
    url = "http://192.168.100.112:3180/backtest/api/trade/v0.3"

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
    url = "http://192.168.100.112:3180/backtest/api/trade/v0.3"

    token = uuid.uuid4().hex
    account = f"my-great-strategy-v1-{token[-4:]}"
    start = datetime.date(2015, 1, 5)
    end = datetime.date(2022, 3, 14)
    client: TraderClient = TraderClient(
        url, account, token, is_backtest=True, start=start, end=end
    )

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


if __name__ == "__main__":
    benchmark()
