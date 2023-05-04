
echo "将移除start_service启动的本地环境中的backtest服务"
sudo docker rm -f tox-redis
sudo docker rm -f tox-influxdb
sudo docker rm -f tox-bt
sudo docker network rm tox-bt-net
exit 0
