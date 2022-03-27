export TZ=Asia/Shanghai

home="$(dirname "$(readlink -fm "$0")")"

# 启动backtest server
docker rm -f tox-backtest &> /dev/null
docker run --pull -d --name tox-backtest -v $home/tests/data:/config -e PORT=3180 -p 3180:3180 backtest

sleep 3
