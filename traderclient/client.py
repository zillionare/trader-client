"""Main module."""
import datetime
import logging
import uuid
from typing import Dict, List

import arrow

from traderclient.transport import get, post_json

logger = logging.getLogger(__name__)


class TradeClient:
    def __init__(self, url: str, token: str):
        """构建一个交易客户端

        Args:
            url : 服务器地址及路径，比如 http://localhost:port/trade/api/v1
            token : _description_
        """
        self._url = url.rstrip("/")
        self.token = token
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
        info = get(url, headers=self.headers)

        if info is None:
            return None

        start = info.get("start", None)
        if start is not None:
            start = arrow.get(start).date()

        end = info.get("end", None)
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
        b = get(url, headers=self.headers)

        if b is None:
            return None
        else:
            return b

    def buy(self, code: str, price: float, volume: float, **kwargs) -> Dict:
        """买入股票

        Args:
            code : 股票代码
            price : 买入价格
            volume : 买入数量
        """
        if volume != volume // 100 * 100:
            volume = volume // 100 * 100
            logger.warning("买入数量必须是100的倍数, 已取整到%d", volume)

        url = self._cmd_url("buy")
        data = {"code": code, "price": price, "volume": volume, **kwargs}

        return post_json(url, payload=data, headers=self.headers)

    def available_money(self) -> float:
        """返回当前可用资金

        Returns:
            _description_
        """
        cash = get(self._cmd_url("available_money"), headers=self.headers)
        return cash

    def positions(self) -> List:
        """返回当前持仓

        Returns:
            _description_
        """
        positions = get(self._cmd_url("positions"), headers=self.headers)
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
        shares = get(url, params=data, headers=self.headers)
        return shares

    def today_entrusts(self) -> List:
        raise NotImplementedError

    def today_trades(self) -> List:
        raise NotImplementedError

    def cancel_entrust(self, entrust_id: int) -> Dict:
        raise NotImplementedError

    def cancel_all_entrusts(self) -> Dict:
        raise NotImplementedError

    def market_buy(
        self,
        security: str,
        volume: int,
        ttype=None,
        limit_price: float = None,
        timeout: float = 0.5,
        **kwargs,
    ) -> Dict:
        assert volume == volume // 100 * 100
        raise NotImplementedError

    def sell(
        self, security: str, price: float, volume: int, timeout: float = 0.5, **kwargs
    ) -> Dict:
        assert volume == volume // 100 * 100
        raise NotImplementedError

    def market_sell(
        self,
        security: str,
        volume: int,
        ttype=None,
        limit_price: float = None,
        timeout: float = 0.5,
        **kwargs,
    ) -> Dict:
        assert volume == volume // 100 * 100
        raise NotImplementedError

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
    from traderclient.utils import enable_logging

    enable_logging("info")
    url = "http://localhost:7080/backtest/api/trade/v0.1"
    client = TradeClient(url, "abcd")
    date = datetime.datetime(2022, 3, 1, 9, 35)
    r = client.buy("002537.XSHE", 9.8, 100, order_time=date.isoformat())
    print(r)
