# History

## 0.1.0 (2022-03-07)

* First release on PyPI.

## 0.3.5 (2022-05-27)
* Use http status code to determine if the request was successful, rather than wrap status in payload, and raise TradeError if there's exception.
* Rename capital to principal, tradeclient to TraderClient
* Use binary to convey data between server/client for interface `position`, `info`, `metrics`
* `balance`, `available_money`, `assets` interface will all goto `/info` endpoint
* `position` and `available_shares` interface will all goto `/position` endpoint
* Add documentation

## 0.3.6 (2022-06-01)
* loose version constraints of httpx
## 0.3.7 (2022-06-02)
* fixed: sell_percent missed parameter order_time

## 0.3.8 (2022-06-05)
* add get_assets, which is needed when plot equity curve

## 0.3.9 (2022-06-06)
* add timeout when trader client talk to server.
* add stop_backtest API
* this version will match zillionare-backtest >= 0.4.1. When it's talk to that version, order_time must be strictly ordered in ascending order (in seconds or even less granularity).

## 0.3.10 (2022-07-21)
* fixed #7
