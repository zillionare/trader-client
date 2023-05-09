以下代码演示了如何使用trader-client:

```python
from traderclient import TraderClient
import uuid

# 请指向zillionare trader server或者backtest server
url = "http://localhost:7080/trader/api/v0.4"
account = "test-account"
token = uuid.uuid4().hex
client: TraderClient = TraderClient(url, account, token)

code = "000001.XSHE"
r = client.buy(code, 9.5, 100)
```

上述代码构建了一个实时交易客户端（即实盘交易，而非回测），并且调用了`buy`方法，购买了一手股票。注意我们使用的证券代码必须包含交易所标志。".XSHE"表示深交所，".XSHG"表示上交所。

这里的account和token需要由zillionare-trader-server来分配和配置。

在进行回测时，只需要在构建TraderClient时，传入`is_backtest` = True，并且将`url`指向回测服务器即可。回测服务器会使用您提供的`account`与`token`生成一个新的回测账户，后面所有的回测都将在这个环境下执行。

!!!info
    如果`url`指向了回测服务器，但构造TraderClient时并没有指定`is_backtest`为True，则回测服务器将复用对应的account。这种场景主要用于事后获取回测数据，请注意，不要在此情形下开始新一轮的回测。任何一轮新的回测，都始终应该使用全新的回测环境。

```python
from traderclient import TraderClient
import uuid
import datetime

url = "http://backtest_server:7080/backtest/api/trade/v0.4/"

# to start a new backtest, please always generate a new account and token
token = uuid.uuid4().hex
account = f"my-great-strategy-v1-{token[-4:]}"
start = datetime.date(2022, 3, 1)
end = datetime.date(2022, 3, 14)
client: TraderClient = TraderClient(url, account, token, is_backtest=True, start = start, end=end)

code = "000001.XSHE"
# please specify order_time if it's backtest mode
r = client.buy(code, 9.5, 100, order_time=datetime.datetime(2022,3,7,9,31))
print(r)
```
注意在回测模式下，您可以指定本金和手续费，但计算alpha等指标使用的risk_free利率则是在回测服务器上配置的，以便您可以比较不同策略的数据表现。

另一个值得注意的地方是，在回测模式下买卖股票，必须传入`order_time`，原因是，在实盘模式下，下单时间总是当前时间，因此这个参数可以省略；而在回测模式下，我们实际上是在过去的某一个时间点进行下单，而这个时间点，只有策略知道，回测服务器不可能知道，因此您必须提供给回测服务器。

在回测模式下使用其它API时，您可能需要根据具体情况，传入“当前时间”或者对应的时间点。回测模式下的“现在”，一般是指服务器最后接收的一个`buy`或者`sell`指令中的时间。

!!!Tips
    如何获取回测服务器的地址？您可以在浏览器地址栏中输入http://server:port/，这样将会返回如下提示：

    ```json
    {
        "greetings":"欢迎使用大富翁回测系统",
        "version":"0.4.1",
        "endpoint":"/backtest/api/trade/v0.4"
    }
    ```
    因此trader client初始化时，地址应该设置为http://server:port/backtest/api/trade/v0.4

## 交易

您可以通过
* [buy][traderclient.client.TraderClient.buy]
* [market_buy][traderclient.client.TraderClient.market_buy]
* [async buy_by_money][traderclient.client.TraderClient.buy_by_money]
* [sell][traderclient.client.TraderClient.sell]
* [market_sell][traderclient.client.TraderClient.market_sell]
* [sell_percent][traderclient.client.TraderClient.sell_percent]

来进行交易。

## 状态跟踪

您可以通过：

* [info][traderclient.client.TraderClient.info]来查看账户的基本信息，比如当前总资产、持仓、本金、盈利等。
* [principal 属性][traderclient.client.TraderClient.principal] 得到本金信息
* [balance][traderclient.client.TraderClient.balance] 得到账户信息，包括现金，股票市值，总资产，盈亏（绝对值），盈亏率（百分比）
* [available_money 属性][traderclient.client.TraderClient.available_money] 当前可用现金
* [positions][traderclient.client.TraderClient.positions] 获取某一天的持仓
* [available_shares][traderclient.client.TraderClient.available_shares] 来查询某个股在某个日期下可售的股票数量。

[bills][traderclient.client.TraderClient.bills] 来查看账户的持仓、交易历史记录
## 策略评估

[metrics][traderclient.client.TraderClient.metrics]方法将返回策略的各项指标，比如sharpe, sortino, calmar, win rate, max drawdown等。您还可以传入一个参考标的，backtest将对参考标的也同样计算上述指标。

在调用`metrics`之前，请先调用[stop_backtest][traderclient.client.TraderClient.stop_backtest]方法冻结回测结果。

## 超时设置
从0.3.9起，Trader Client支持设置访问服务器的超时时间。您可以通过环境变量[TRADER_CLIENT_TIMEOUT]来设置这个超时。如果未经设置，则默认使用30秒超时，但有一个例外，即如果部分API中设置了timeout时间，且这个时间大于30秒，那么将使用API调用时设置的timeout设置。
