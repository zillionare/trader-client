import logging
import os
import pickle
import uuid
from typing import Any, Dict

import httpx

from traderclient.utils import get_cmd, status_ok

from .errors import TradeError

logger = logging.getLogger(__name__)


def timeout(params: dict = None) -> int:
    """determine timeout value for httpx request

    if there's envar "TRADER_CLIENT_TIMEOUT", it will precedes, then the max of user timeout and default 30

    Args:
        params : user specified in request

    Returns:
        timeout
    """
    if os.environ.get("TRADER_CLIENT_TIMEOUT"):
        return int(os.environ.get("TRADER_CLIENT_TIMEOUT"))

    if params is None or params.get("timeout") is None:
        return 30

    return max(params.get("timeout"), 30)


def process_response_result(rsp: httpx.Response, cmd: str = None) -> Any:
    """获取响应中的数据，并检查结果合法性

    Args:
        rsp (response): HTTP response object
        cmd (str, optional): trade instuction

    Raises:
        traderclient.errors.Error: 如果服务器返回状态码不为2xx，则抛出错误
    """
    if cmd is None:
        cmd = get_cmd(str(rsp.url))

    content_type = rsp.headers.get("Content-Type")

    # process 20x response, check response code first
    if status_ok(rsp.status_code):
        if content_type == "application/json":
            return rsp.json()
        elif content_type.startswith("text"):
            return rsp.text
        else:
            return pickle.loads(rsp.content)

    # http 1.1 allow us to extend http status code, so we choose 499 as our error code. The upstream server is currently built on top of sanic, it doesn't support customer reason phrase (always return "Unknown Error" if the status code is extened. So we have to use body to carry on reason phrase.
    if rsp.status_code == 499:
        logger.warning("%s failed: %s, %s", cmd, rsp.status_code, rsp.text)
        raise TradeError(rsp.status_code, rsp.text)
    else:
        rsp.raise_for_status()


def get(url, params=None, headers=None) -> Any:
    """发送GET请求到上游服务接口

    Args:
        url : 目标URL，带服务器信息
        params : JSON格式的参数清单
        headers : 额外的header选项

    """
    if headers is None:
        headers = {"Request-ID": uuid.uuid4().hex}
    else:
        headers.update({"Request-ID": uuid.uuid4().hex})

    rsp = httpx.get(url, params=params, headers=headers, timeout=timeout(params))

    action = get_cmd(url)
    result = process_response_result(rsp, action)

    return result


def post_json(url, params=None, headers=None) -> Any:
    """以POST发送JSON数据请求

    Args:
        url : 目标URL，带服务器信息
        params : JSON格式的参数清单
        headers : 额外的header选项

    """
    if headers is None:
        headers = {"Request-ID": uuid.uuid4().hex}
    else:
        headers.update({"Request-ID": uuid.uuid4().hex})

    rsp = httpx.post(url, json=params, headers=headers, timeout=timeout(params))

    action = get_cmd(url)
    result = process_response_result(rsp, action)

    return result


def delete(url, params=None, headers=None) -> Any:
    """从服务器上删除资源

    Args:
        url : 目标URL，带服务器信息
        params : 查询参数
        headers : 额外的header选项

    Returns:
    """
    if headers is None:
        headers = {"Request-ID": uuid.uuid4().hex}
    else:
        headers.update({"Request-ID": uuid.uuid4().hex})

    rsp = httpx.delete(url, params=params, headers=headers, timeout=timeout(params))

    action = get_cmd(url)
    result = process_response_result(rsp, action)

    return result
