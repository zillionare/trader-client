# -*- coding: utf-8 -*-
# @Author   : henry
# @Time     : 2022-03-09 15:08


def status_ok(code: int):
    return code in [200, 201, 204]


def get_cmd(url: str):
    cmd = url.split("/")[-1]
    return {
        "info": "获取账户信息",
        "balance": "获取账户余额",
        "available_money": "获取可用资金",
        "position": "获取持仓信息",
        "buy": "买入股票",
        "sell": "卖出股票",
        "available_shares": "获取可用持仓",
        "today_entrusts": "获取当日委托",
        "today_trades": "获取当日成交",
        "cancel_entrust": "撤单",
        "cancel_all_entrust": "全部撤单",
        "market_buy": "市价买入",
        "market_sell": "市价卖出",
        "sell_percent": "按比例卖出股票",
        "sell_all": "全部卖出",
        "get_trades_in_range": "获取指定时间段的成交记录",
        "get_entrusts_in_range": "获取指定时间段的委托记录",
    }.get(cmd, "未知命令")
