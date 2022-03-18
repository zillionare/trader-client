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
    stock_name,
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

    def _cmd_url(self, cmd: str) -> str:
        return f"{self._url}/{cmd}"

    def handle_failure_response(self, result: Dict):
        """_summary_

        Args:
            result : _description_
        """
        if result["status"] != 0:
            logger.error(
                "调用失败，状态码: %s, 错误信息：%s, extra info: %s",
                result["status"],
                result["msg"],
                result.get("data", ""),
            )
            return None

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
        data = {"code": stock_name(code)}

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
        raise NotImplementedError

    def today_trades(self) -> List:
        raise NotImplementedError

    def cancel_entrust(self, entrust_id: int) -> Dict:
        raise NotImplementedError

    def cancel_all_entrusts(self) -> Dict:
        raise NotImplementedError

    def buy(self, order: TradeOrder, **kwargs) -> Dict:
        """买入股票

        Args:
            order : 委托信息
        """

        order_request = order.order_req

        volume = order_request.volume
        if volume != volume // 100 * 100:
            volume = volume // 100 * 100
            logger.warning("买入数量必须是100的倍数, 已取整到%d", volume)

        url = self._cmd_url("buy")

        # 更新买入时间戳
        order_request.created_at = datetime.datetime.now()
        order_time = order_request.created_at.strftime("%Y-%m-%d %H:%M:%S")

        order_request.order_side = OrderSide.BUY
        order_request.bid_type = BidType.LIMIT
        data = {
            "code": order_request.code,
            "price": order_request.price,
            "volume": order_request.volume,
            "order_time": order_time,
            **kwargs,
        }

        return post_json(url, payload=data, headers=self.headers)

    def market_buy(
        self,
        order: TradeOrder,
        timeout: float = 0.5,
        **kwargs,
    ) -> Dict:
        order_request = order.order_req

        volume = order_request.volume
        if volume != volume // 100 * 100:
            volume = volume // 100 * 100
            logger.warning("买入数量必须是100的倍数, 已取整到%d", volume)

        url = self._cmd_url("market_buy")

        # 更新买入时间戳
        order_request.created_at = datetime.datetime.now()
        order_time = order_request.created_at.strftime("%Y-%m-%d %H:%M:%S")

        order_request.order_side = OrderSide.BUY
        order_request.bid_type = BidType.MARKET
        data = {
            "code": order_request.code,
            "price": order_request.price,
            "volume": order_request.volume,
            "order_time": order_time,
            "timeout": timeout,
            **kwargs,
        }

        return post_json(url, payload=data, headers=self.headers)

    def sell(self, order: TradeOrder, timeout: float = 0.5, **kwargs) -> Dict:
        order_request = order.order_req

        # 卖出数量可以是零头
        volume = order_request.volume

        url = self._cmd_url("sell")

        # 更新时间戳
        order_request.created_at = datetime.datetime.now()
        order_time = order_request.created_at.strftime("%Y-%m-%d %H:%M:%S")

        order_request.order_side = OrderSide.BUY
        order_request.bid_type = BidType.LIMIT
        data = {
            "code": order_request.code,
            "price": order_request.price,
            "volume": volume,
            "order_time": order_time,
            "timeout": timeout,
            **kwargs,
        }

        return post_json(url, payload=data, headers=self.headers)

    def market_sell(
        self,
        order: TradeOrder,
        timeout: float = 0.5,
        **kwargs,
    ) -> Dict:
        order_request = order.order_req

        # 卖出数量可以是零头
        volume = order_request.volume

        url = self._cmd_url("market_sell")

        # 更新时间戳
        order_request.created_at = datetime.datetime.now()
        order_time = order_request.created_at.strftime("%Y-%m-%d %H:%M:%S")

        order_request.order_side = OrderSide.SELL
        order_request.bid_type = BidType.MARKET
        data = {
            "code": order_request.code,
            "price": order_request.price,
            "volume": volume,
            "order_time": order_time,
            "timeout": timeout,
            **kwargs,
        }

        return post_json(url, payload=data, headers=self.headers)

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


if __name__ == "__main__":
    pass
