"""Main module."""
import datetime
import logging
import uuid
from typing import Dict, List

from traderclient.errors import CreateAccountError
from traderclient.trade import OrderSide, OrderStatus, OrderType
from traderclient.transport import get, post_json

logger = logging.getLogger(__name__)


class TradeClient:
    def __init__(
        self, url: str, acct: str, token: str, is_backtest: bool = False, **kwargs
    ):
        """构建一个交易客户端

        当`is_backtest`为True时，会自动在服务端创建新账户。此时kwargs必须传入capital和commission。

        Info:
            如果`url`指向了回测服务器，但`is_backtest`设置为False，如果提供的账户acct,token在服务器端存在，则将重用该账户，该账户之前的一些数据仍将保留，这可能导致某些错误，特别是继续进行测试时，时间发生rewind的情况。

        Args:
            url : 服务器地址及路径，比如 http://localhost:port/trade/api/v1
            acct : 子账号
            token : 子账号对应的服务器访问令牌
            is_backtest : 是否为回测模式，默认为False。

        Keyword Args:
            capital : 初始资金，默认为1_000_000
            commission : 手续费率，默认为1.5e-4

        Raises:
            CreateAccountError 如果创建账户失败，则会抛出些异常。
        """
        self._url = url.rstrip("/")
        self.token = token
        self.account = acct
        self.headers = {"Authorization": self.token}
        self.headers["Account"] = self.account

        self._is_backtest = is_backtest

        if is_backtest:
            capital = kwargs.get("capital", 1_000_000)
            commission = kwargs.get("commission", 1.5e-4)

            self._create_account(acct, token, capital, commission)

    def _cmd_url(self, cmd: str) -> str:
        return f"{self._url}/{cmd}"

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

    def _create_account(self, acct: str, token: str, capital: float, commission: float):
        """在回测模式下，创建一个新账户

        Args:
            acct : 子账号名
            token : 子账号对应的服务器访问令牌
            capital : 初始资金
            commission : 手续费率
        """
        url = self._cmd_url("accounts")
        data = {
            "name": acct,
            "token": token,
            "capital": capital,
            "commission": commission,
        }

        result = post_json(url, data, headers=self.headers)
        if result is None:
            raise CreateAccountError("failed to create account")

    def info(self) -> Dict:
        """获取账户信息

        Returns:
            主要字段：账号名，当前资产，本金，最后一笔交易时间，交易笔数，账户创建时间
        """
        url = self._cmd_url("info")
        result = get(url, headers=self.headers)
        if result is None:
            logger.error("info: failed to get information")
            return None

        return result

    def balance(self) -> Dict:
        """取该子账号对应的账户余额信息

        Returns:
            主要字段：参考盈亏，可用资金，股票市值，总资产，盈亏比例，子账户ID
        """
        url = self._cmd_url("balance")
        result = get(url, headers=self.headers)
        if result is None:
            logger.error("balance: failed to get information")
            return None

        return result

    def available_money(self) -> float:
        """取当前之账户可用金额。策略函数可能需要这个数据进行仓位计算

        Returns:
            float: 账户可用资金
        """
        url = self._cmd_url("available_money")
        result = get(url, headers=self.headers)
        if result is None:
            logger.error("available_money: failed to get information")
            return None

        return result

    def positions(self) -> List:
        """取该子账户当前持仓信息

        Returns:
            List: 单个股票的信息为，代码，名称，总股数，可卖数，成本均价
        """
        url = self._cmd_url("positions")
        result = get(url, headers=self.headers)
        if result is None:
            logger.error("positions: failed to get information")
            return None

        return result

    def available_shares(self, security: str) -> int:
        """返回某支股票当前可用数量

        Args:
            security : 股票代码

        Returns:
            int: 指定股票今日可卖数量，无可卖即为0
        """
        url = self._cmd_url("available_shares")
        data = {"security": security}

        result = post_json(url, params=data, headers=self.headers)
        if result is None:
            logger.error("positions: failed to get information")
            return None

        return result

    def today_entrusts(self) -> List:
        """查询账户当日所有委托，包括失败的委托

        Returns:
            List: 委托信息数组，字段参考buy
        """
        url = self._cmd_url("today_entrusts")

        result = get(url, headers=self.headers)
        if result is None:
            logger.error("today_entrusts: failed to get information")
            return None

        return result

    def today_trades(self) -> List:
        """查询当日所有成交的委托

        Returns:
            List: 委托信息，参考buy的结果
        """
        url = self._cmd_url("today_trades")

        result = get(url, headers=self.headers)
        if result is None:
            logger.error("today_trades: failed to get information")
            return None

        return result

    def cancel_entrust(self, cid: str) -> Dict:
        """撤销委托

        Args:
            cid (str): 交易服务器返回的委托合同号

        Returns:
            Dict: _description_
        """
        url = self._cmd_url("cancel_entrust")

        data = {"cid": cid}
        result = post_json(url, params=data, headers=self.headers)
        if result is None:
            logger.error("cancel_entrust: failed to get information")
            return None

        return result

    def cancel_all_entrusts(self) -> Dict:
        """撤销当前所有未完成的委托，包括部分成交，不同交易系统实现不同

        Returns:
            Dict: 被撤的委托单信息，同buy
        """
        url = self._cmd_url("cancel_all_entrusts")

        result = post_json(url, headers=self.headers)
        if result is None:
            logger.error("cancel_all_entrust: failed to get information")
            return None

        return result

    def buy(
        self, security: str, price: float, volume: int, timeout: float = 0.5, **kwargs
    ) -> Dict:
        """证券买入

        Args:
            security (str): 证券代码
            price (float): 买入价格（限价）
            volume (int): 买入股票数
            timeout (float, optional): 默认等待交易反馈的超时为0.5秒

        Returns:
            Dict: _description_
        """
        if volume != volume // 100 * 100:
            volume = volume // 100 * 100
            logger.warning("买入数量必须是100的倍数, 已取整到%d", volume)

        url = self._cmd_url("buy")
        parameters = {
            "security": security,
            "price": price,
            "volume": volume,
            "timeout": timeout,
            **kwargs,
        }

        result = post_json(url, params=parameters, headers=self.headers)
        if result is None:
            logger.error("buy: failed to get information")
            return None

        return result

    def market_buy(
        self,
        security: str,
        volume: int,
        order_type: OrderType = OrderType.MARKET,
        limit_price: float = None,
        timeout: float = 0.5,
        **kwargs,
    ) -> Dict:
        """市价买入股票，同花顺终端需要改为涨跌停限价，掘金客户端支持市价交易，掘金系统默认五档成交剩撤

        Args:
            security (str): 证券代码
            volume (int): 买入数量
            order_type (OrderType, optional): 市价买入类型，缺省为五档成交剩撤.
            limit_price (float, optional): 剩余转限价的模式下，设置的限价
            timeout (float, optional): 默认等待交易反馈的超时为0.5秒

        Returns:
            Dict: _description_
        """

        if volume != volume // 100 * 100:
            volume = volume // 100 * 100
            logger.warning("买入数量必须是100的倍数, 已取整到%d", volume)

        url = self._cmd_url("market_buy")
        parameters = {
            "security": security,
            "price": 0,
            "volume": volume,
            "order_type": order_type,
            "timeout": timeout,
            **kwargs,
        }
        if limit_price is not None:
            parameters["limit_price"] = limit_price

        result = post_json(url, params=parameters, headers=self.headers)
        if result is None:
            logger.error("market_buy: failed to get information")
            return None

        return result

    def sell(
        self, security: str, price: float, volume: int, timeout: float = 0.5, **kwargs
    ) -> Dict:
        """以限价方式卖出股票

        Args:
            security (str): 证券代码
            price (float): 买入价格（限价）
            volume (int): 买入股票数
            timeout (float, optional): 默认等待交易反馈的超时为0.5秒
        """
        url = self._cmd_url("sell")
        parameters = {
            "security": security,
            "price": price,
            "volume": volume,
            "timeout": timeout,
            **kwargs,
        }

        result = post_json(url, params=parameters, headers=self.headers)
        if result is None:
            logger.error("sell: failed to get information")
            return None

        return result

    def market_sell(
        self,
        security: str,
        volume: int,
        order_type: OrderType = OrderType.MARKET,
        limit_price: float = None,
        timeout: float = 0.5,
        **kwargs,
    ) -> Dict:
        """市价卖出股票，同花顺终端需要改为涨跌停限价，掘金客户端支持市价交易，掘金系统默认五档成交剩撤

        Args:
            security (str): 证券代码
            volume (int): 卖出数量
            order_type (OrderType, optional): 市价卖出类型，缺省为五档成交剩撤.
            limit_price (float, optional): 剩余转限价的模式下，设置的限价
            timeout (float, optional): 默认等待交易反馈的超时为0.5秒
        """
        url = self._cmd_url("market_sell")
        parameters = {
            "security": security,
            "price": 0,
            "volume": volume,
            "order_type": order_type,
            "timeout": timeout,
            **kwargs,
        }
        if limit_price is not None:
            parameters["limit_price"] = limit_price

        result = post_json(url, params=parameters, headers=self.headers)
        if result is None:
            logger.error("market_sell: failed to get information")
            return None

        return result

    def sell_percent(
        self, security: str, price: float, percent: float, timeout: int = 0.5
    ) -> Dict:
        """按资产比例卖出特定的股票（基于可买股票数），比例的数字由调用者提供

        Args:
            security (str): 特定的股票代码
            price (float): 市价卖出，价格参数可为0
            percent (float): 调用者给出的百分比，(0, 1]
            time_out (int, optional): 缺省超时为0.5秒

        Returns:
            Dict: 股票卖出委托单的详细信息，于sell指令相同
        """
        if percent <= 0 or percent > 1:
            return None
        if len(security) < 6:
            return None

        url = self._cmd_url("sell_percent")
        parameters = {
            "security": security,
            "price": price,
            "timeout": timeout,
        }

        result = post_json(url, params=parameters, headers=self.headers)
        if result is None:
            logger.error("sell_percent: failed to get information")
            return None

        return result

    def sell_all(self, percent: float, timeout: float = 0.5) -> List:
        """将所有持仓按percent比例进行减仓，用于特殊情况下的快速减仓（基于可买股票数）

        Args:
            percent (float): 调用者给出的百分比，(0, 1]
            time_out (int, optional): 缺省超时为0.5秒

        Returns:
            List: 所有卖出股票的委托单信息，于sell指令相同
        """
        if percent <= 0 or percent > 1:
            return None

        url = self._cmd_url("sell_all")
        parameters = {
            "percent": percent,
            "timeout": timeout,
        }

        result = post_json(url, params=parameters, headers=self.headers)
        if result is None:
            logger.error("sell_all: failed to get information")
            return None

        return result

    def get_trades_in_range(self, start: datetime.date, end: datetime.date) -> List:
        if start is None and end is not None:
            logger.error("get_trades_in_range, start or end cannot be None")
            return None
        if start is not None and end is None:
            logger.error("get_trades_in_range, start or end cannot be None")
            return None
        if start > end:
            logger.error("get_trades_in_range, end is early than start!")
            return None

        url = self._cmd_url("get_trades_in_range")
        parameters = {}
        if start is not None:
            parameters["start"] = start.strftime("%Y-%m-%d %H:%M:%S")
        if end is not None:
            parameters["end"] = end.strftime("%Y-%m-%d %H:%M:%S")

        result = post_json(url, params=parameters, headers=self.headers)
        if result is None:
            logger.error("get_trades_in_range: failed to get information")
            return None

        return result

    def get_entrusts_in_range(self, start: datetime.date, end: datetime.date) -> List:
        if start is None and end is not None:
            logger.error("get_entrusts_in_range, start or end cannot be None")
            return None
        if start is not None and end is None:
            logger.error("get_entrusts_in_range, start or end cannot be None")
            return None
        if start > end:
            logger.error("get_entrusts_in_range, end is early than start!")
            return None

        url = self._cmd_url("get_entrusts_in_range")
        parameters = {}
        if start is not None:
            parameters["start"] = start.strftime("%Y-%m-%d %H:%M:%S")
        if end is not None:
            parameters["end"] = end.strftime("%Y-%m-%d %H:%M:%S")

        result = post_json(url, params=parameters, headers=self.headers)
        if result is None:
            logger.error("get_entrusts_in_range: failed to get information")
            return None

        return result

    def metrics(self, start: datetime.date = None, end: datetime.date = None) -> Dict:
        """获取指定时间段的账户指标评估数据

        Args:
            start : _description_.
            end : _description_.

        Returns:
            _description_
        """
        url = self._cmd_url("metrics")
        result = get(url, headers=self.headers)
        if result is None:
            logger.error("info: failed to get information")
            return None

        return result["data"]
