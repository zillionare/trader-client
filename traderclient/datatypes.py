# -*- coding: utf-8 -*-
# @Author   : henry
# @Time     : 2022-03-09 15:08
from enum import IntEnum


class OrderSide(IntEnum):
    BUY = 1  # 股票买入
    SELL = -1  # 股票卖出


class OrderType(IntEnum):
    LIMIT = 1  # 限价委托
    MARKET = 2  # 市价委托


class OrderStatus(IntEnum):
    ERROR = -1  # 异常
    NO_DEAL = 1  # 未成交
    PARTIAL_TRANSACTION = 2  # #部分成交
    ALL_TRANSACTIONS = 3  # 全部成交
    CANCEL_ALL_ORDERS = 4  # 全部撤单
