# -*- coding: utf-8 -*-
# @Author   : henry
# @Time     : 2022-03-09 15:08
import logging


def status_ok(code: int):
    return code in [200, 201, 204]


def enable_logging(level: str = "info"):
    logger = logging.getLogger()

    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    level = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }.get(level.lower(), logging.INFO)

    logger.setLevel(level)


def get_cmd(url: str):
    cmd = url.split("/")[-1]
    return {
        "accounts": "创建/查询/删除账户",
        "info": "获取账户信息",
        "position": "获取持仓信息",
        "buy": "买入股票",
        "sell": "卖出股票",
        "available_shares": "获取可用持仓",
        "today_entrusts": "获取当日委托",
        "today_trades": "获取当日成交",
        "cancel_entrust": "撤单",
        "cancel_all_entrusts": "全部撤单",
        "market_buy": "市价买入",
        "market_sell": "市价卖出",
        "sell_percent": "按比例卖出股票",
        "sell_all": "全部卖出",
        "get_trades_in_range": "获取指定时间段的成交记录",
        "get_entrusts_in_range": "获取指定时间段的委托记录",
        "metrics": "账户评估指标",
        "start_backtest": "启动回测",
        "bills": "交割单",
    }.get(cmd, "未知命令")
