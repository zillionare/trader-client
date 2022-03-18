import logging
import uuid

import requests

logger = logging.getLogger(__name__)


def status_ok(code):
    return code in [200, 201, 204]


def get_cmd(url):
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


def get_result(rsp, cmd: str = None):
    if cmd is None:
        cmd = get_cmd(rsp.url)

    content_type = rsp.headers.get("Content-Type")

    try:
        # process 200 response
        if status_ok(rsp.status_code):
            if content_type == "application/json":
                json_data = rsp.json()
                if "status" in json_data:
                    logger.info("recv trade response, %s, %s", cmd, json_data)
                    return json_data

            # invalid response from trade server
            if content_type.startswith("text"):
                logger.info("recv trade response, %s, %s", cmd, rsp.text)
                return None
            else:
                logger.info("invalid response, %s, %s", cmd, rsp.raw)
                return None

        # process errros
        else:
            if content_type == "application/json":
                result = rsp.json()
                logger.error("执行%s失败，状态码: %d, 错误信息: %s", cmd, rsp.status_code, result)
            else:
                logger.info("%s失败：状态：%s, 附加信息:%s", cmd, rsp.status_code, rsp.text)
    except Exception as e:
        logger.exception(e)

    return None


def get(url, params=None, headers=None):
    """the GET verb

    Args:
        url : _description_
        params : _description_.
        headers : _description_.

    Returns:
        根据返回头的content-type，分别返回json, text或者bytes
    """
    headers.update({"Request-ID": uuid.uuid4().hex})

    r = requests.get(url, params=params, headers=headers)
    return get_result(r, get_cmd(url))


def post_json(url, payload=None, headers=None):
    """以POST发送JSON数据请求

    Args:
        url : 目标URL，带服务器信息
        payload : JSON格式的参数清单
        headers : 额外的header选项

    Returns:
        根据返回头的content-type，分别返回json, text或者bytes
    """

    headers.update({"Request-ID": uuid.uuid4().hex})
    rsp = requests.post(url, json=payload, headers=headers)

    return get_result(rsp, get_cmd(url))
