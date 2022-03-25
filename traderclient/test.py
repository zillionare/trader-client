# -*- coding: utf-8 -*-
# @Author   : henry
# @Time     : 2022-03-09 15:08
import datetime
import logging
from typing import List

from traderclient import TradeClient

logger = logging.getLogger(__name__)


def init_logging(level=logging.INFO):
    logger = logging.getLogger()

    handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt="---%(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(level)


url = "http://192.168.100.130:8000/api/trade/v0.1"
acct = "myquant_sim_henry1"
token = "f59e34e1-71bc-46b8-8935-c60a636b9bba"
client = TradeClient(url, acct, token)


def print_result(result):
    if result is None:
        logger.error("failed to get information")
        return None

    if result["status"] != 0:
        print(f">>>>>>>> {result['msg']}")
        return None

    print("response: \n")
    if "data" in result:
        datalist = result["data"]
        if isinstance(datalist, List):
            for data in datalist:
                print(f"{data}\n")
        else:
            print(f"{datalist}\n")
    else:
        print("no data in response")

    print("\n")


def testcase_f01_01():
    print("------------- info --------------")
    result = client.info()
    print_result(result)

    input("next case: today_entrusts ......")
    result = client.today_entrusts()
    print_result(result)

    input("next case: positions ......")
    result = client.positions()
    print_result(result)

    input("next case: balance ......")
    result = client.balance()
    print_result(result)

    input("next case: available_money ......")
    result = client.available_money()
    print_result(result)


def testcase_f01_02():
    print("------------- info --------------")
    result = client.info()
    print_result(result)

    input("next case: buy 600000.XSH......")
    result = client.buy(security="600000.XSHG", price=6.99, volume=1800)
    print_result(result)

    input("next case: positions ......")
    result = client.positions()
    print_result(result)

    print("------------- info --------------")
    result = client.info()
    print_result(result)


def testcase_f01_03():
    print("------------- info --------------")
    result = client.info()
    print_result(result)

    input("next case: buy 000020.XSHE......")
    result = client.buy(security="000020.XSHE", price=99.94, volume=100)
    print_result(result)

    input("next case: buy 001030.XSHE......")
    result = client.buy(security="001030.XSHE", price=9.94, volume=100)
    print_result(result)

    input("next case: positions ......")
    result = client.positions()
    print_result(result)

    input("next case: balance ......")
    result = client.balance()
    print_result(result)

    print("------------- info --------------")
    result = client.info()
    print_result(result)


def testcase_f02_01():
    print("------------- info --------------")
    result = client.info()
    print_result(result)

    input("next case: buy 600000.XSHG......")
    result = client.buy(security="600000.XSHG", price=6.99, volume=2100)
    print_result(result)

    input("next case: today_entrusts ......")
    result = client.today_entrusts()
    print_result(result)

    input("next case: today_entrusts ......")
    result = client.today_entrusts()
    print_result(result)


def testcase_f02_02():
    print("------------- info --------------")
    result = client.info()
    print_result(result)

    input("next case: buy 600009.XSHG......")
    result = client.buy(security="600009.XSHG", price=6.99, volume=2100)
    print_result(result)

    input("next case: today_entrusts ......")
    result = client.today_entrusts()
    print_result(result)

    input("next case: today_entrusts ......")
    result = client.today_entrusts()
    print_result(result)


def testcase_f02_03():
    print("------------- info --------------")
    result = client.info()
    print_result(result)

    input("next case: buy 601118.XSHG......")
    result = client.buy(security="601118.XSHG", price=6.99, volume=2100)
    print_result(result)

    input("next case: today_entrusts ......")
    result = client.today_entrusts()
    print_result(result)

    input("next case: cancel_all_entrust ......94c40593-9eb5-44cd-85fc-6ea1e19ce55a")
    result = client.cancel_entrust(cid="94c40593-9eb5-44cd-85fc-6ea1e19ce55a")
    print_result(result)

    input("next case: today_entrusts ......")
    result = client.today_entrusts()
    print_result(result)


def testcase_f02_04():
    print("------------- info --------------")
    result = client.info()
    print_result(result)

    input("next case: buy 600107.XSHG......")
    result = client.buy(security="600107.XSHG", price=6.76, volume=1200)
    print_result(result)

    input("next case: today_entrusts ......")
    result = client.today_entrusts()
    print_result(result)


def testcase_f02_20():
    print("------------- info --------------")
    result = client.info()
    print_result(result)

    input("next case: buy 601600.XSHG......")
    result = client.buy(security="601600.XSHG", price=6.99, volume=2100)
    print_result(result)

    input("next case: buy 003017.XSHE......")
    result = client.buy(security="003017.XSHE", price=23.14, volume=800)
    print_result(result)

    input("next case: today_entrusts ......")
    result = client.today_entrusts()
    print_result(result)

    input("next case: today_entrusts ......")
    result = client.today_entrusts()
    print_result(result)


def testcase_f02_30():
    print("------------- info --------------")
    result = client.info()
    print_result(result)

    input("next case: buy 003023.XSHE......")
    result = client.buy(security="003023.XSHE", price=24.4, volume=600)
    print_result(result)

    input("next case: today_entrusts ......")
    result = client.today_entrusts()
    print_result(result)


def testcase_f02_31():
    print("------------- info --------------")
    result = client.info()
    print_result(result)

    input("next case: buy 600107.XSHG......")
    result = client.buy(security="600107.XSHG", price=6.76, volume=15000)
    print_result(result)

    input("next case: today_entrusts ......")
    result = client.today_entrusts()
    print_result(result)


def testcase_f02_32():
    print("------------- info --------------")
    result = client.info()
    print_result(result)

    input("next case: buy 600107.XSHG......")
    result = client.buy(security="600107.XSHG", price=6.76, volume=1200)
    print_result(result)

    input("next case: today_entrusts ......")
    result = client.today_entrusts()
    print_result(result)


def testcase_f03_01():
    print("------------- info --------------")
    result = client.info()
    print_result(result)

    input("next case: market_buy 600000.XSHG......")
    result = client.market_buy(security="600000.XSHG", price=5.20, volume=10000)
    print_result(result)


def testcase_f06_01():
    print("------------- info --------------")
    result = client.info()
    print_result(result)

    input("next case: buy 003023.XSHE......")
    result = client.buy(security="003023.XSHE", price=24.4, volume=600)
    print_result(result)

    input("next case: cancel_entrust 5acd03f0-544c-4e17-8db4-a9a08bf69eb6 ......")
    result = client.cancel_entrust("5acd03f0-544c-4e17-8db4-a9a08bf69eb6")
    print_result(result)

    input("next case: today_entrusts ......")
    result = client.today_entrusts()
    print_result(result)


def testcase_f06_02():
    print("------------- info --------------")
    result = client.info()
    print_result(result)

    input("next case: buy 003023.XSHE......")
    result = client.buy(security="003023.XSHE", price=24.4, volume=600)
    print_result(result)

    input("next case: buy 000001.XSHE ......")
    result = client.buy(security="000001.XSHE", price=4.2, volume=1200)
    print_result(result)

    input("next case: cancel_all_entrust ......")
    result = client.cancel_all_entrusts()
    print_result(result)

    input("next case: today_entrusts ......")
    result = client.today_entrusts()
    print_result(result)


def testcase_f06_03():
    print("------------- info --------------")
    result = client.info()
    print_result(result)

    input("next case: buy 003023.XSHE......")
    result = client.buy(security="003023.XSHE", price=24.4, volume=600)
    print_result(result)

    input("next case: cancel_entrust ba0a8ee8-a9c6-4c52-abb7-c5bdcbe20241 ......")
    result = client.cancel_entrust("ba0a8ee8-a9c6-4c52-abb7-c5bdcbe20241")
    print_result(result)

    input("next case: today_entrusts ......")
    result = client.today_entrusts()
    print_result(result)


def testcase_f07_02():
    print("------------- info --------------")
    result = client.info()
    print_result(result)

    input("next case: buy 600107.XSHG......")
    result = client.buy(security="600107.XSHG", price=6.76, volume=1200)
    print_result(result)

    input("next case: buy 600107.XSHG......")
    result = client.buy(security="600107.XSHG", price=6.80, volume=500)
    print_result(result)


def testcase_f07_03():
    print("------------- info --------------")
    result = client.info()
    print_result(result)

    input("next case: sell 600107.XSHG......")
    result = client.sell(security="600107.XSHG", price=6.76, volume=1200)
    print_result(result)


if __name__ == "__main__":
    init_logging(logging.DEBUG)

    # testcase_f01_01()
    # testcase_f02_04()
    # testcase_f06_03()
    testcase_f03_01()

    input("next step: query account info")
    testcase_f01_01()
