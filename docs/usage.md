以下代码演示了如何使用trader-client:

```python
from traderclient import TraderClient
import uuid

# 请指向zillionare trader server或者backtest server
url = "http://localhost:7080/trader/api/v0.3"
account = "test-account"
token = uuid.uuid4().hex
client: TraderClient = TraderClient(url, account, token)

code = "000001.XSHE"
r = client.buy(code, 9.5, 100)
```

上述代码构建了一个实时交易客户端（即实盘交易或者模拟盘交易，对应于回测），并且调用了`buy`方法，购买了一手股票。注意我们使用的证券代码必须包含交易所标志。".XSHE"表示深交所，".XSHG"表示上交所。

这里的account和token需要由zillionare-trader-server来分配和配置。

在进行回测时，只需要在构建TraderClient时，传入`is_backtest` = True，并且将`url`指向回测服务器即可。回测服务器会使用您提供的`account`与`token`生成一个新的回测账户，后面所有的回测都将在这个环境下执行。

!!!info
    如果`url`指向了回测服务器，但构造TraderClient时并没有指定`is_backtest`为True，则回测服务器将复用对应的account。这种场景主要用于事后获取回测数据，请注意，不要在此情形下开始新一轮的回测。任何一轮新的回测，都始终应该使用全新的回测环境。

```python
from traderclient import TraderClient
import uuid
import datetime

url = "http://localhost:7080/backtest-trader/api/v0.2"
account = "my great strategy-v1"
token = uuid.uuid4().hex
client: TraderClient = TraderClient(url, account, token, is_backtest=True, principal=1_000_000, commission=1.5e-4)

code = "000001.XSHE"
r = client.buy(code, 9.5, 100, order_time=datetime.datetime(2022, 5, 9, 9, 31))
```
注意在回测模式下，您可以指定本金和手续费，但计算alpha等指标使用的risk_free利率则是在回测服务器上配置的，以便您可以比较不同策略的数据表现。

另一个值得注意的地方是，在回测模式下买卖股票，必须传入`order_time`，原因是，在实盘模式下，下单时间总是当前时间，而在回测模式下，我们实际上是在过去的某一个时间点进行下单，而这个时间点，只有策略知道，回测服务器不可能知道。

在回测模式下使用其它API时，您可能需要根据具体情况，传入“当前时间”或者对应的时间点。回测模式下的“现在”，一般是指服务器最后接收的一个`buy`或者`sell`指令中的时间。

## 交易

您可以通过[buy][traderclient.client.TraderClient.buy], [market_buy][traderclient.client.TraderClient.market_buy], [sell][traderclient.client.TraderClient.sell], [market_sell][traderclient.client.TraderClient.market_sell]和[sell_percent][traderclient.client.TraderClient.sell_percent]来进行交易。

## 状态跟踪

您可以通过[info][traderclient.client.TraderClient.info]来查看账户的基本信息，比如当前总资产、持仓、本金、盈利等。如果您只想得到单个信息，您也可以使用[principal][traderclient.client.TraderClient.principal]、[balance][traderclient.client.TraderClient.balance]、[available_money][traderclient.client.TraderClient.available_money]来获取。

[positions][traderclient.client.TraderClient.positions]提供了持仓信息，您还可以通过[available_shares][traderclient.client.TraderClient.available_shares]来查询个股当前可售的股票数量。

[bills][traderclient.client.TraderClient.bills]来查看账户的持仓、交易历史记录。
## 策略评估

[metrics][traderclient.client.TraderClient.metrics]方法将返回策略的各项指标，比如sharpe, sortino, calmar, win rate, max drawdown等。您还可以传入一个参考标的，backtest将对参考标的也同样计算上述指标。
