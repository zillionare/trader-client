# 大富翁交易客户端


<p align="center">
<a href="https://pypi.python.org/pypi/zillionare-trader-client">
    <img src="https://img.shields.io/pypi/v/zillionare-trader-client.svg"
        alt = "Release Status">
</a>

</p>

trade-client是大富翁量化框架中用来交易的客户端。它对回测和实盘提供了几乎相同的接口，从而使得经过回测的策略，可以无缝切换到实盘环境中。

## 功能

* 进行实盘和回测交易
* 获取账号基本信息，比如本金、资产、持仓、盈亏及盈亏比等。
* 交易函数，比如买入（限价和市价）、卖出（限价和市价）、撤单等
* 查询委托、成交、持仓（当日和指定日期）
* 查询一段时间内的账户评估指标，比如sharpe, sortino, calmar, voliality, win rate, max drawdown等。
* 查询参照标的同期指标。

## Credits

This package was created with [zillionare/python project wizard](https://zillionare.github.io/python-project-wizard) project template.
