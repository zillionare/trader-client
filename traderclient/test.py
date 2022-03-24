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

    input("next case: positions ......")
    result = client.balance()
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


def testcase_f10_01():
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


def testcase_f10_02():
    print("------------- info --------------")
    result = client.info()
    print_result(result)

    input("next case: buy 003023.XSHE......")
    result = client.buy(security="003023.XSHE", price=24.4, volume=600)
    print_result(result)

    input("next case: cancel_all_entrust ......13ae6632-d3ec-4a65-8876-1654df68eb17")
    result = client.cancel_entrust(cid="13ae6632-d3ec-4a65-8876-1654df68eb17")
    print_result(result)

    input("next case: today_entrusts ......")
    result = client.today_entrusts()
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


def testcase_f02_03():
    print("------------- info --------------")
    result = client.info()
    print_result(result)

    input("next case: buy 600000.XSHG......")
    result = client.buy(security="600000.XSHG", price=6.99, volume=2100)
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

    input("next case: buy 600000.XSHG......")
    result = client.buy(security="600000.XSHG", price=6.99, volume=14400)
    print_result(result)

    input("next case: today_entrusts ......")
    result = client.today_entrusts()
    print_result(result)


if __name__ == "__main__":
    init_logging(logging.DEBUG)

    # testcase_f02_04()
    testcase_f01_02()
