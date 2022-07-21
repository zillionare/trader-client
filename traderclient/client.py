import datetime
import logging
from typing import Dict, List, Optional, Union

import arrow
import numpy as np

from traderclient.datatypes import OrderSide, OrderStatus, OrderType
from traderclient.transport import delete, get, post_json

logger = logging.getLogger(__name__)


class TraderClient:
    """大富翁实盘和回测的客户端。

    在使用客户端时，需要先构建客户端实例，再调用其他方法，并处理[traderclient.errors.TradeError][]的异常，可以通过`status_code`和`message`来获取错误信息。如果是回测模式，一般会在回测结束时调用`metrics`方法来查看策略评估结果。如果要进一步查看信息，可以调用`bills`方法来获取历史持仓、交易记录和每日资产数据。

    """

    def __init__(
        self, url: str, acct: str, token: str, is_backtest: bool = False, **kwargs
    ):
        """构建一个交易客户端

        当`is_backtest`为True时，会自动在服务端创建新账户。

        Info:
            如果`url`指向了回测服务器，但`is_backtest`设置为False，且如果提供的账户acct,token在服务器端存在，则将重用该账户，该账户之前的一些数据仍将保留，这可能导致某些错误，特别是继续进行测试时，时间发生rewind的情况。一般情况下，这种情况只用于获取之前的测试数据。

        Args:
            url : 服务器地址及路径，比如 http://localhost:port/trade/api/v1
            acct : 子账号
            token : 子账号对应的服务器访问令牌
            is_backtest : 是否为回测模式，默认为False。

        Keyword Args:
            principal: float 初始资金，默认为1_000_000
            commission: float 手续费率，默认为1e-4
            start: datetime.date 回测开始日期，必选
            end: datetime.date 回测结束日期，必选
        """
        self._url = url.rstrip("/")
        self._token = token
        self._account = acct
        self.headers = {"Authorization": self._token}
        self.headers["Account"] = self._account

        self._is_backtest = is_backtest

        if is_backtest:
            principal = kwargs.get("principal", 1_000_000)
            commission = kwargs.get("commission", 1e-4)
            start = kwargs.get("start")
            end = kwargs.get("end")
            if start is None or end is None:
                raise ValueError("start and end must be specified in backtest mode")

            self._start_backtest(acct, token, principal, commission, start, end)

    def _cmd_url(self, cmd: str) -> str:
        return f"{self._url}/{cmd}"

    def _start_backtest(
        self,
        acct: str,
        token: str,
        principal: float,
        commission: float,
        start: datetime.date,
        end: datetime.date,
    ):
        """在回测模式下，创建一个新账户

        Args:
            acct : 账号名
            token : 账号对应的服务器访问令牌
            principal : 初始资金
            commission : 手续费率
            start : 回测开始日期
            end : 回测结束日期
        """
        url = self._cmd_url("start_backtest")
        data = {
            "name": acct,
            "token": token,
            "principal": principal,
            "commission": commission,
            "start": start.isoformat(),
            "end": end.isoformat(),
        }

        post_json(url, data)

    def info(self) -> Dict:
        """账户的当前基本信息，比如账户名、资金、持仓和资产等

        !!! info
            在回测模式下，info总是返回`last_trade`对应的那天的信息，因为这就是回测时的当前日期。

        Returns:
            dict: 账户信息

            - name: str, 账户名
            - principal: float, 初始资金
            - assets: float, 当前资产
            - start: datetime.date, 账户创建时间
            - last_trade: datetime.datetime, 最后一笔交易时间
            - available: float, 可用资金
            - market_value: 股票市值
            - pnl: 盈亏(绝对值)
            - ppnl: 盈亏(百分比)，即pnl/principal
            - positions: 当前持仓，dtype为[position_dtype](https://zillionare.github.io/backtesting/0.3.2/api/trade/#backtest.trade.datatypes.position_dtype)的numpy structured array

        """
        url = self._cmd_url("info")
        return get(url, headers=self.headers)

    def balance(self) -> Dict:
        """取该账号对应的账户余额信息

        Returns:
            Dict: 账户余额信息

            - available: 现金
            - market_value: 股票市值
            - assets: 账户总资产
            - pnl: 盈亏(绝对值)
            - ppnl: 盈亏(百分比)，即pnl/principal

        """
        url = self._cmd_url("info")
        r = get(url, headers=self.headers)

        return {
            "available": r["available"],
            "market_value": r["market_value"],
            "assets": r["assets"],
            "pnl": r["pnl"],
            "ppnl": r["ppnl"],
        }

    @property
    def account(self) -> str:
        return self._account

    @property
    def available_money(self) -> float:
        """取当前账户的可用金额。策略函数可能需要这个数据进行仓位计算

        Returns:
            float: 账户可用资金
        """
        url = self._cmd_url("info")
        r = get(url, headers=self.headers)
        return r.get("available")

    @property
    def principal(self) -> float:
        """账户本金

        Returns:
            本金
        """
        if self._is_backtest:
            return self._principal

        url = self._cmd_url("info")
        r = get(url, headers=self.headers)
        return r.get("principal")

    def positions(self, dt: datetime.date = None) -> np.ndarray:
        """取该子账户当前持仓信息

        Warning:
            在回测模式下，持仓信息不包含alias字段

        Args:
            dt: 指定日期，默认为None，表示取当前日期（最新）的持仓信息，trade server暂不支持此参数
        Returns:
            np.ndarray: dtype为[position_dtype](https://zillionare.github.io/backtesting/0.3.2/api/trade/#backtest.trade.datatypes.position_dtype)的numpy structured array
        """
        url = self._cmd_url("positions")

        r = get(url, params={"date": dt}, headers=self.headers)

        return r

    def available_shares(self, security: str) -> int:
        """返回某支股票当前可用数量

        在回测模式下，使用持仓表最后一日的记录进行过滤。

        Args:
            security: 股票代码

        Returns:
            int: 指定股票今日可卖数量，无可卖即为0
        """
        url = self._cmd_url("positions")

        r = get(url, headers=self.headers)

        found = r[r["security"] == security]
        if found.size == 1:
            return found["sellable"][0].item()
        elif found.size == 0:
            return 0
        else:
            logger.warning("found more than one position entry in response: %s", found)

    def today_entrusts(self) -> List:
        """查询账户当日所有委托，包括失败的委托

        此API在回测模式下不可用。

        Returns:
            List: 委托信息数组，各元素字段参考buy
        """
        url = self._cmd_url("today_entrusts")

        return get(url, headers=self.headers)

    def cancel_entrust(self, cid: str) -> Dict:
        """撤销委托

        此API在回测模式下不可用。
        Args:
            cid (str): 交易服务器返回的委托合同号

        Returns:
            Dict: 被取消的委托的信息，参考`buy`的结果
        """
        url = self._cmd_url("cancel_entrust")

        data = {"cid": cid}
        return post_json(url, params=data, headers=self.headers)

    def cancel_all_entrusts(self) -> List:
        """撤销当前所有未完成的委托，包括部分成交，不同交易系统实现不同

        此API在回测模式下不可用。
        Returns:
            List: 所有被撤的委托单信息，每个委托单的信息同buy
        """
        url = self._cmd_url("cancel_all_entrusts")

        return post_json(url, headers=self.headers)

    def buy(
        self,
        security: str,
        price: float,
        volume: int,
        timeout: float = 0.5,
        order_time: Union[str, datetime.datetime] = None,
        **kwargs,
    ) -> Dict:
        """证券买入

        Notes:
            注意如果是回测模式，还需要传入order_time，因为回测模式下，服务器是不可能知道下单这一刻的时间的。注意在回测模式下，返回字段少于实盘。

            使用回测服务器时，无论成交实际上是在哪些时间点发生的，都使用order_time。在实盘模式下，则会分别返回create_at, recv_at两个字段

        Args:
            security (str): 证券代码
            price (float): 买入价格（限价）。在回测时，如果price指定为None，将转换为市价买入
            volume (int): 买入股票数
            timeout (float, optional): 默认等待交易反馈的超时为0.5秒
            order_time Union[str, datetime.datetime]: 下单时间。在回测模式下使用。

        Returns:
            Dict: 成交返回
                实盘返回以下字段：

                {
                    "cid" : "xxx-xxxx-xxx",    # 券商给出的合同编号，内部名为entrust_no
                    "security": "000001.XSHE",
                    "name": "平安银行",
                    "price": 5.10,                  # 委托价格
                    "volume": 1000,                 # 委托量
                    "order_side": 1,                # 成交方向，1买，-1卖
                    "order_type": 1,                # 成交方向，1限价，2市价
                    "status": 3,                    # 执行状态，1已报，2部分成交，3成交，4已撤
                    "filled": 500,                 # 已成交量
                    "filled_vwap": 5.12,        # 已成交均价，不包括税费
                    "filled_value": 2560,        # 成交额，不包括税费
                    "trade_fees": 12.4,            # 交易税费，包括佣金、印花税、杂费等
                    "reason": "",                        # 如果委托失败，原因？
                    "created_at": "2022-03-23 14:55:00.1000",    # 委托时间，带毫秒值
                    "recv_at": "2022-03-23 14:55:00.1000",        # 交易执行时间，带毫秒值
                }

            回测时将只返回以下字段:

                {
                    "tid": 成交号
                    "eid": 委托号
                    "security": 证券代码
                    "order_side": 成交方向，1买，-1卖
                    "price": 成交价格
                    "filled": 已成交量
                    "time": 成交时间
                    "trade_fees": 交易费用
                }

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

        if self._is_backtest:
            assert order_time is not None, "order_time is required in backtest mode"
            if isinstance(order_time, datetime.datetime):
                order_time = order_time.strftime("%Y-%m-%d %H:%M:%S")
            parameters["order_time"] = order_time

        r = post_json(url, params=parameters, headers=self.headers)

        for key in ("time", "created_at", "recv_at"):
            if key in r:
                r[key] = arrow.get(r[key]).naive

        return r

    def market_buy(
        self,
        security: str,
        volume: int,
        order_type: OrderType = OrderType.MARKET,
        limit_price: float = None,
        timeout: float = 0.5,
        order_time: Union[str, datetime.datetime] = None,
        **kwargs,
    ) -> Dict:
        """市价买入股票

        Notes:

            同花顺终端需要改为涨跌停限价，掘金客户端支持市价交易，掘金系统默认五档成交剩撤消。

            在回测模式下，市价买入相当于持涨停价进行撮合。
            在回测模式下，必须提供order_time参数。

        Args:
            security (str): 证券代码
            volume (int): 买入数量
            order_type (OrderType, optional): 市价买入类型，缺省为五档成交剩撤.
            limit_price (float, optional): 剩余转限价的模式下，设置的限价
            timeout (float, optional): 默认等待交易反馈的超时为0.5秒
            order_time Union[str, datetime.datetime]: 下单时间。在回测模式下使用。

        Returns:
            Dict: 成交返回，详见`buy`方法
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
            "limit_price": limit_price,
            **kwargs,
        }

        if self._is_backtest:
            assert order_time is not None, "order_time is required in backtest mode"
            if isinstance(order_time, datetime.datetime):
                order_time = order_time.strftime("%Y-%m-%d %H:%M:%S")
            parameters["order_time"] = order_time

        r = post_json(url, params=parameters, headers=self.headers)

        for key in ("time", "created_at", "recv_at"):
            if key in r:
                r[key] = arrow.get(r[key]).naive

        return r

    def sell(
        self,
        security: str,
        price: float,
        volume: int,
        timeout: float = 0.5,
        order_time: Union[str, datetime.datetime] = None,
        **kwargs,
    ) -> Union[List, Dict]:
        """以限价方式卖出股票

        Notes:
            如果是回测模式，还需要传入order_time，因为回测模式下，服务器是不可能知道下单这一刻的时间的。如果服务器是回测服务器，则返回的数据为多个成交记录的列表（即使只包含一个数据）

        Args:
            security (str): 证券代码
            price (float): 买入价格（限价）。在回测中如果指定为None,将转换为市价卖出
            volume (int): 买入股票数
            timeout (float, optional): 默认等待交易反馈的超时为0.5秒
            order_time Union[str, datetime.datetime]: 下单时间。在回测模式下使用。

        Returns:
            Union[List, Dict]: 成交返回，详见`buy`方法，trade server只返回一个委托单信息
        """
        # todo: check return type?
        url = self._cmd_url("sell")
        parameters = {
            "security": security,
            "price": price,
            "volume": volume,
            "timeout": timeout,
            **kwargs,
        }

        if self._is_backtest:
            assert order_time is not None, "order_time is required in backtest mode"
            if isinstance(order_time, datetime.datetime):
                order_time = order_time.strftime("%Y-%m-%d %H:%M:%S")
            parameters["order_time"] = order_time

        r = post_json(url, params=parameters, headers=self.headers)
        for key in ("created_at", "recv_at"):
            if key in r:
                r[key] = arrow.get(r[key]).naive

        if self._is_backtest:
            for rec in r:
                rec["time"] = arrow.get(rec["time"]).naive

        return r

    def market_sell(
        self,
        security: str,
        volume: int,
        order_type: OrderType = OrderType.MARKET,
        limit_price: float = None,
        timeout: float = 0.5,
        order_time: Union[str, datetime.datetime] = None,
        **kwargs,
    ) -> Union[List, Dict]:
        """市价卖出股票

        Notes:
            同花顺终端需要改为涨跌停限价，掘金客户端支持市价交易，掘金系统默认五档成交剩撤

            如果是回测模式，则市价卖出意味着以跌停价挂单进行撮合。

            目前模拟盘和实盘模式下没有实现限价。

        Args:
            security (str): 证券代码
            volume (int): 卖出数量
            order_type (OrderType, optional): 市价卖出类型，缺省为五档成交剩撤.
            limit_price (float, optional): 剩余转限价的模式下，设置的限价
            timeout (float, optional): 默认等待交易反馈的超时为0.5秒
            order_time Union[str, datetime.datetime]: 下单时间。在回测模式下使用。
        Returns:
            Union[List, Dict]: 成交返回，详见`buy`方法，trade server只返回一个委托单信息
        """
        url = self._cmd_url("market_sell")
        parameters = {
            "security": security,
            "price": 0,
            "volume": volume,
            "order_type": order_type,
            "timeout": timeout,
            "limit_price": limit_price,
            **kwargs,
        }

        if self._is_backtest:
            assert order_time is not None, "order_time is required in backtest mode"
            if isinstance(order_time, datetime.datetime):
                order_time = order_time.strftime("%Y-%m-%d %H:%M:%S")
            parameters["order_time"] = order_time

        r = post_json(url, params=parameters, headers=self.headers)
        for key in ("time", "created_at", "recv_at"):
            if key in r:
                r[key] = arrow.get(r[key]).naive

        return r

    def sell_percent(
        self,
        security: str,
        price: float,
        percent: float,
        timeout: int = 0.5,
        order_time: Union[str, datetime.datetime] = None,
        **kwargs,
    ) -> Union[List, Dict]:
        """按比例卖出特定的股票（基于可卖股票数），比例的数字由调用者提供

        Notes:
            注意实现中存在取整问题。比如某支股票当前有500股可卖，如果percent=0.3，则要求卖出150股。实际上卖出的将是100股。

        Args:
            security (str): 特定的股票代码
            price (float): 市价卖出，价格参数可为0
            percent (float): 调用者给出的百分比，(0, 1]
            time_out (int, optional): 缺省超时为0.5秒
            order_time: 下单时间。在回测模式下使用。

        Returns:
            Union[List, Dict]: 股票卖出委托单的详细信息，于sell指令相同
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
            "percent": percent,
        }

        if self._is_backtest:
            assert order_time is not None, "order_time is required in backtest mode"
            if isinstance(order_time, datetime.datetime):
                order_time = order_time.strftime("%Y-%m-%d %H:%M:%S")
            parameters["order_time"] = order_time

        r = post_json(url, params=parameters, headers=self.headers)
        for key in ("time", "created_at", "recv_at"):
            if key in r:
                r[key] = arrow.get(r[key]).naive

        return r

    def sell_all(self, percent: float, timeout: float = 0.5) -> List:
        """将所有持仓按percent比例进行减仓，用于特殊情况下的快速减仓（基于可买股票数）

        此API在回测模式下不可用。

        Args:
            percent (float): 调用者给出的百分比，(0, 1]
            time_out (int, optional): 缺省超时为0.5秒

        Returns:
            List: 所有卖出股票的委托单信息，于sell指令相同
        """
        if percent <= 0 or percent > 1:
            return None

        url = self._cmd_url("sell_all")
        parameters = {"percent": percent, "timeout": timeout}

        return post_json(url, params=parameters, headers=self.headers)

    def metrics(
        self,
        start: datetime.date = None,
        end: datetime.date = None,
        baseline: str = None,
    ) -> Dict:
        """获取指定时间段[start, end]间的账户指标评估数据

        Args:
            start: 起始日期
            end: 结束日期
            baseline: the security code for baseline

        Returns:
            Dict: 账户指标评估数据

            - start 回测起始时间
            - end   回测结束时间
            - window 资产暴露时间
            - total_tx 发生的配对交易次数
            - total_profit 总盈亏
            - total_profit_rate 总盈亏率
            - win_rate 胜率
            - mean_return 每笔配对交易平均回报率
            - sharpe    夏普比率
            - max_drawdown 最大回撤
            - sortino
            - calmar
            - annual_return 年化收益率
            - volatility 波动率
            - baseline: dict
                - win_rate
                - sharpe
                - max_drawdown
                - sortino
                - annual_return
                - total_profit_rate
                - volatility

        """
        url = self._cmd_url("metrics")
        params = {
            "start": start.strftime("%Y-%m-%d") if start else None,
            "end": end.strftime("%Y-%m-%d") if end else None,
            "baseline": baseline,
        }
        return get(url, headers=self.headers, params=params)

    def bills(self) -> Dict:
        """获取账户的交易、持仓、市值流水信息。

        Returns:
            Dict: 账户的交易、持仓、市值流水信息

            - trades
            - positions
            - assets
            - tx
        """
        url = self._cmd_url("bills")
        return get(url, headers=self.headers)

    def get_assets(
        self,
        start: Union[str, datetime.date] = None,
        end: Union[str, datetime.date] = None,
    ) -> np.ndarray:
        """获取账户在[start, end]时间段内的资产信息。

        此数据可用以资产曲线的绘制。

        Args:
            start: 起始日期
            end: 结束日期

        Returns:
            np.ndarray: 账户在[start, end]时间段内的资产信息，是一个dtype为[rich_assets_dtype](https://zillionare.github.io/backtesting/0.4.0/api/trade/#backtest.trade.datatypes.rich_assets_dtype)的numpy structured array
        """
        url = self._cmd_url("assets")
        return get(url, headers=self.headers, params={"start": start, "end": end})

    def stop_backtest(self):
        """停止回测。

        此API仅在回测模式下可用。其作用是冻结回测账户，并计算回测的各项指标。在未调用本API前，调用`metrics`也能同样获取到回测的各项指标，但如果需要多次调用`metrics`，则账户在冻结之后，由于指标不再需要更新，因而速度会更快。

        另外，在[zillionare-backtest](https://zillionare.github.io/backtesting/)的未来版本中,将可能使用本方法来实现回测数据的持久化保存，因此，建议您从现在起就确保在回测后调用本方法。

        """
        url = self._cmd_url("stop_backtest")
        return post_json(url, headers=self.headers)

    @staticmethod
    def list_accounts(url_prefix: str, admin_token: str) -> List:
        """列举服务器上所有账户（不包含管理员账户）

        此命令需要管理员权限。

        Args:
            url_prefix : 服务器地址及前缀
            admin_token : 管理员token

        Returns:
            账户列表，每个元素信息即`info`返回的信息
        """
        url_prefix = url_prefix.rstrip("/")
        url = f"{url_prefix}/accounts"
        headers = {"Authorization": admin_token}
        return get(url, headers=headers)

    @staticmethod
    def delete_account(url_prefix: str, account_name: str, token: str) -> int:
        """删除账户

        仅回测模式下实现。

        此API不需要管理员权限。只要知道账户名和token即可删除账户。对管理员要删除账户的，可以先通过管理员账户列举所有账户，得到账户和token后再删除。

        Args:
            url_prefix (str): 服务器地址及前缀
            account_name (str): 待删除的账户名
            token (str): 账户token

        Returns:
            服务器上剩余账户个数
        """
        url_prefix = url_prefix.rstrip("/")
        url = f"{url_prefix}/accounts"
        headers = {"Authorization": token}
        return delete(url, headers=headers, params={"name": account_name})
