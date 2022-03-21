"""Main module."""
import datetime
import logging
import uuid
from typing import Dict, List

import arrow

from traderclient.trade import (
    BidType,
    OrderRequest,
    OrderResponse,
    OrderSide,
    OrderStatus,
    TradeOrder,
)
from traderclient.transport import get, post_json

logger = logging.getLogger(__name__)


class TradeClient:
    def __init__(self, url: str, acct: str, token: str):
        """构建一个交易客户端

        Args:
            url : 服务器地址及路径，比如 http://localhost:port/trade/api/v1
            acct : 子账号
            token : 子账号对应的服务器访问令牌
        """
        self._url = url.rstrip("/")
        self.token = token
        self.account = acct
        self.headers = {"Authorization": f"Token {self.token}"}
        self.order = None

    def _cmd_url(self, cmd: str) -> str:
        return f"{self._url}/{cmd}"

    def set_trade_entrust(self, code: str, volume: int, price: float = 0):
        """构建新的委托信息，之前的委托对象会扔弃（重新初始化）

        Args:
            code (str): 股票代码
            volume (int): 委托量
            price (float, optional): 委托价格，市价委托时一般为0

        Returns:
            TradeOrder: 返回新建的委托对象
        """
        self.order = TradeOrder(code, volume, price)
        return self.order

    def get_trade_order(self):
        # 通常情况下无需使用此方法返回委托对象

        return self.order

    def handle_failure_response(self, result: Dict):
        """处理状态不为0的响应信息，暂时只记入日志

        Args:
            result : 上游服务返回的字典数据
        """

        if result["status"] != 0:
            logger.error(
                "exec failed, status: %d, error msg: %s, extra info: %s",
                result["status"],
                result["msg"],
                result.get("data", ""),
            )

        return None

    def update_trade_info(self, data: Dict):
        """从上游服务返回数据中加载委托的执行信息

        Args:
            data (Dict): {'status':0, 'msg':'OK', 'data': data}中的data
        """

        order_response = self.order.order_rsp

        # 委托号，委托状态（2部分成交，3全部成交）
        order_response.entrust_id = data["cid"]
        order_response.order_status = data["status"]

        # 成交均价，成交量，成交额，手续费（包含佣金、印花税、杂费）
        order_response.avg_price = data["price"]
        order_response.filled_vol = data["volume"]
        order_response.filled_amount = data["value"]
        order_response.commission = data["trade_fees"]

        # 带毫秒的时间信息
        order_response.updated_at = datetime.datetime.strptime(
            data["date"], "%Y-%m-%d %H:%M:%S.%f"
        )

    def info(self) -> Dict:
        """获取账户信息"""
        url = self._cmd_url("info")
        result = get(url, headers=self.headers)

        if result is None:
            logger.error("cannot get account information")
            return None

        status = result["status"]
        if status != 0:
            logger.error("failed to get account information")
            return None

        info = result["data"]
        start = info.get("start", None)
        if start is not None:
            start = arrow.get(start).date()

        end = info.get("last_trade", None)
        if end is not None:
            end = arrow.get(end).date()

        return {
            "name": info["name"],
            "assets": info["assets"],
            "capital": info["capital"],
            "start": start,
            "last_trade": end,
            "trades": info["trades"],
        }

    def balance(self) -> Dict:
        """获取账户余额信息

        Returns:
            _description_
        """
        url = self._cmd_url("balance")
        result = get(url, headers=self.headers)

        if result is None:
            logger.error("cannot get balance information")
            return None

        status = result["status"]
        if status != 0:
            logger.error("failed to get balance information")
            return None

        info = result["data"]
        return info

    def available_money(self) -> float:
        """返回当前可用资金

        Returns:
            _description_
        """
        url = self._cmd_url("available_money")
        result = get(url, headers=self.headers)

        if result is None:
            logger.error("cannot get available money")
            return None

        status = result["status"]
        if status != 0:
            logger.error("failed to get available money")
            return None

        info = result["data"]
        return info

    def positions(self) -> List:
        """返回当前持仓

        Returns:
            _description_
        """
        url = self._cmd_url("positions")
        result = get(url, headers=self.headers)

        if result is None:
            logger.error("cannot get available money")
            return None

        status = result["status"]
        if status != 0:
            logger.error("failed to get available money")
            return None

        positions = result["data"]
        return positions

    def available_shares(self, code: str = None) -> List:
        """返回某支股票当前可用数量

        Args:
            code : 股票代码，如果为None，则返回所有股票的可用数量

        Returns:
            _description_
        """
        url = self._cmd_url("available_shares")
        data = {"code": code}

        result = post_json(url, payload=data, headers=self.headers)
        if result is None:
            logger.error("cannot get available shares")
            return None

        status = result["status"]
        if status != 0:
            logger.error("failed to get available shares")
            return None

        shares = result["data"]
        return shares

    def today_entrusts(self) -> List:
        url = self._cmd_url("today_entrusts")

        result = get(url, headers=self.headers)
        if result is None:
            logger.error("cannot get today entrusts")
            return None

        status = result["status"]
        if status != 0:
            logger.error("failed to get today entrusts")
            return None

        entrusts = result["data"]
        return entrusts

    def today_trades(self) -> List:
        url = self._cmd_url("today_trades")

        result = get(url, headers=self.headers)
        if result is None:
            logger.error("cannot get today trades")
            return None

        status = result["status"]
        if status != 0:
            logger.error("failed to get today trades")
            return None

        trades = result["data"]
        return trades

    def cancel_entrust(self, entrust_id: int) -> Dict:
        url = self._cmd_url("cancel_entrust")

        data = {"request_id": entrust_id}
        result = post_json(url, payload=data, headers=self.headers)
        if result is None:
            logger.error("cannot cancel entrust")
            return None

        status = result["status"]
        if status != 0:
            logger.error("failed to cancel entrust")
            return None

        return result

    def cancel_all_entrusts(self) -> Dict:
        url = self._cmd_url("cancel_all_entrust")

        result = get(url, headers=self.headers)
        if result is None:
            logger.error("cannot cancel all entrust")
            return None

        status = result["status"]
        if status != 0:
            logger.error("failed to cancel all entrust")
            return None

        return result

    def trade_operation(self, url: str, timeout: float, **kwargs):
        order_request = self.order.order_req
        self.headers.update({"Request-ID": order_request.request_id})

        # 更新操作时间戳
        order_request.created_at = datetime.datetime.now()

        # 设置payload
        data = {
            "code": order_request.code,
            "price": order_request.price,
            "volume": order_request.volume,
            "timeout": timeout,
            **kwargs,
        }

        result = post_json(url, payload=data, headers=self.headers)
        if result is None:
            return None

        status = result["status"]
        if status != 0:
            return self.handle_failure_response()

        data = result["data"]
        # 更新委托信息
        self.update_trade_info(data)

        return result

    def buy(self, timeout: float = 0.5, **kwargs) -> Dict:
        """买入股票

        Args:
            timeout : 等待交易接口返回的超时设定，默认0.5秒
        """
        order_request = self.order.order_req
        volume = order_request.volume
        if volume != volume // 100 * 100:
            volume = volume // 100 * 100
            logger.warning("买入数量必须是100的倍数, 已取整到%d", volume)

        url = self._cmd_url("buy")
        order_request.order_side = OrderSide.BUY
        order_request.bid_type = BidType.LIMIT

        return self.trade_operation(url, timeout, **kwargs)

    def market_buy(self, timeout: float = 0.5, **kwargs) -> Dict:
        """市价买入股票，同花顺终端需要改为涨跌停限价，掘金客户端支持市价交易，掘金系统默认五档成交剩撤

        Args:
            timeout : 等待交易接口返回的超时设定，默认0.5秒
        """
        order_request = self.order.order_req
        volume = order_request.volume
        if volume != volume // 100 * 100:
            volume = volume // 100 * 100
            logger.warning("买入数量必须是100的倍数, 已取整到%d", volume)

        url = self._cmd_url("market_buy")
        order_request.order_side = OrderSide.BUY
        order_request.bid_type = BidType.MARKET

        return self.trade_operation(url, timeout, **kwargs)

    def sell(self, timeout: float = 0.5, **kwargs) -> Dict:
        """以限价方式卖出股票

        Args:
            timeout : 等待交易接口返回的超时设定，默认0.5秒
        """
        order_request = self.order.order_req

        # 卖出数量可以是零头

        url = self._cmd_url("sell")
        order_request.order_side = OrderSide.BUY
        order_request.bid_type = BidType.LIMIT

        return self.trade_operation(url, timeout, **kwargs)

    def market_sell(self, timeout: float = 0.5, **kwargs) -> Dict:
        """市价卖出股票，同花顺终端需要改为涨跌停限价，掘金客户端支持市价交易，掘金系统默认五档成交剩撤

        Args:
            timeout : 等待交易接口返回的超时设定，默认0.5秒
        """
        order_request = self.order.order_req

        # 卖出数量可以是零头

        url = self._cmd_url("market_sell")
        order_request.order_side = OrderSide.SELL
        order_request.bid_type = BidType.MARKET

        return self.trade_operation(url, timeout, **kwargs)

    def sell_percent(
        self, security: str, price: float, percent: float, time_out: int = 0.5
    ) -> Dict:
        assert percent > 0 and percent <= 1
        raise NotImplementedError

    def sell_all(self, percent: float, timeout: float = 0.5) -> Dict:
        assert percent > 0 and percent <= 1
        raise NotImplementedError

    def get_trades_in_range(self, start: datetime.date, end: datetime.date) -> List:
        raise NotImplementedError

    def get_entrusts_in_range(self, start: datetime.date, end: datetime.date) -> List:
        raise NotImplementedError
