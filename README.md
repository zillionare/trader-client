# 大富翁交易客户端

trade-client是大富翁量化框架中用来交易的客户端。它对回测和实盘提供了几乎相同的接口，从而使得经过回测的策略，可以无缝切换到实盘环境中。

## 功能

* 进行实盘和回测交易
* 获取账号基本信息，比如本金、资产、持仓、盈亏及盈亏比等。
* 交易函数，比如买入（限价和市价）、卖出（限价和市价）、撤单等
* 查询委托、成交、持仓（当日和指定日期）
* 查询一段时间内的账户评估指标，比如sharpe, sortino, calmar, voliality, win rate, max drawdown等。
* 查询参照标的同期指标。

!!!Warning
    在回测模式下，注意可能引起账户数据改变的操作，比如`buy`、`sell`等，必须严格按时间顺序执行，比如下面的例子：
    ```
    client.buy(..., order_time=datetime.datetime(2022, 3, 1, 9, 31))
    client.buy(..., order_time=datetime.datetime(2022, 3, 4, 14, 31))
    client.buy(..., order_time=datetime.datetime(2022, 3, 4, 14, 32))
    client.sell(..., order_time=datetime.datetime(2022, 3, 7, 9, 31))
    ```
    是正确的执行顺序，但下面的执行顺序必然产生错误的结果(实际上服务器也会进行检测并报错误)
    ```
    client.buy(..., order_time=datetime.datetime(2022, 3, 1, 14, 31))
    client.buy(..., order_time=datetime.datetime(2022, 3, 1, 9, 31))
    client.sell(..., order_time=datetime.datetime(2022, 3, 7, 9, 31))
    ```
    策略需要自行决定是否允许这样的情况发生，以及如果发生失，会产生什么样的后果。

## Credits

This package was created with [zillionare/python project wizard](https://zillionare.github.io/python-project-wizard) project template.
