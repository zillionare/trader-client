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
