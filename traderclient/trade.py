# -*- coding: utf-8 -*-
# @Author   : henry
# @Time     : 2022-03-09 15:08
import datetime
import uuid
from enum import IntEnum
from termios import VLNEXT


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


class OrderRequest:
    request_id: str  # 交易请求号，客户端自行生成，每笔交易的唯一识别号
    security: str  # 股票代码，输入时填数字即可，自动转换
    price: float  # 交易价格，包括同花顺市价转换成的限价
    volume: int  # 交易数量，100的整数倍，除非成交的时候有零头
    order_side: OrderSide  # 交易方向，买卖
    order_type: OrderType  # 限价，市价
    created_at: datetime.datetime  # 交易发起时间


class OrderResponse:
    entrust_id: str  # 委托单号，交易终端返回
    order_status: OrderStatus  # 委托状态：已报，已成，部成，已撤，无效等等
    avg_price: float  # 成交均价
    filled_vol: int  # 成交量
    filled_amount: int  # 成交额
    commission: float  # 佣金和税费
    updated_at: datetime.datetime  # 交易更新时间

    def __init__(self):
        self.entrust_id = ""
        self.order_status = OrderStatus.ERROR
        self.avg_price = 0
        self.filled_vol = 0
        self.filled_amount = 0
        self.commission = 0
        self.updated_at = datetime.datetime.now()


class TradeOrder:
    """交易委托详细信息，客户端通过此对象保存交易数据"""

    order_req: OrderRequest  # 交易请求信息
    order_rsp: OrderResponse  # 委托信息

    def __init__(self):
        self.order_req = OrderRequest()
        self.order_rsp = OrderResponse()

    def set_limit_price(self, limit_price: float):
        self.order_req.price = limit_price

    def toDict(self):
        return {
            "request_id": self.order_req.request_id,
            "security": self.order_req.security,
            "price": self.order_req.price,
            "volume": self.order_req.volume,
            "order_side": int(self.order_req.order_side),
            "bid_type": int(self.order_req.bid_type),
            "created_at": self.order_req.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "entrust_id": self.order_rsp.entrust_id,
            "order_status": int(self.order_rsp.order_status),
            "avg_price": self.order_rsp.avg_price,
            "filled_vol": self.order_rsp.filled_vol,
            "filled_amount": self.order_rsp.filled_amount,
            "commission": self.order_rsp.commission,
            "updated_at": self.order_rsp.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
