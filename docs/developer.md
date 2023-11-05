# 通信

客户端与服务器之间使用http进行通信。通过Authorization携带token，可以控制访问权限。通过Request-ID来防止重复提交。

服务器向客户端传回数据时，一般使用json，但这样会导致客户端对日期时间需要特别进行解析。因此，对以下API，约定使用pickle进行序列化和反序列化：

- info
- positions
- metrics

通过这些接口传输的对象，都是常见的数据类型，比如日期、数字、字符串、列表、字典和numpy数组等，不包含大富翁定义的数据类型。

# 错误处理
使用标准的HTTP status code来表示状态，如果成功则返回200。由于某些服务器当前还不能通过reason_phrase(RFC 2616)来返回解释性的错误原因，这里我们使用错误码499来进行协议扩展。当服务器有额外信息需要返回时，传回一个499的错误码，此时客户端会读取Response的body文本，抛出一个类型为coretypes.errors.trade.TradeError（及子类）的异常。

# 测试环境

zillionare-backtest为开发提供了一个基于容器的测试环境:

```
echo "初始化redis容器"
sudo docker run -d --name tox-redis -p 6379:6379 redis

echo "初始化influxdb容器"
sudo docker run -d -p 8086:8086 --name tox-influxdb influxdb
sleep 5
sudo docker exec -i tox-influxdb bash -c 'influx setup --username my-user --password my-password --org my-org --bucket my-bucket --token my-token --force'

sleep 1
docker run -d --name tox-bt -e MODE=TEST -e PORT=3180 -p 3180:3180 backtest

docker network create tox-bt-net
docker network connect --alias redis tox-bt-net tox-redis
docker network connect --alias influxdb tox-bt-net tox-influxdb
docker network connect --alias bt tox-bt-net tox-bt
```

更多详细信息，请参考[backtest-server]()

测试过程完全自动化，可以通过`tox`命令来运行。tox.ini中是这样定义的：
```
commands =
    /usr/bin/sh ./stop_service.sh
    /usr/bin/sh ./start_service.sh
    pytest -s --cov=traderclient --cov-append --cov-report=xml --cov-report term-missing tests
```
测试用例会自动寻找backtesting服务器地址并进行测试。
