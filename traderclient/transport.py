import logging
import uuid
from typing import Dict

import requests

from traderclient.utils import get_cmd, status_ok

logger = logging.getLogger(__name__)


def process_response_result(rsp, cmd: str = None):
    """获取响应中的数据，并检查结果合法性

    Args:
        rsp (response): HTTP response object
        cmd (str, optional): trade instuction

    Returns:
        json or None: 如果数据符合要求，返回{'status':x, 'msg':'xxx', 'data':list or dict}，否则返回None，需要调用者自行判断
    """
    if cmd is None:
        cmd = get_cmd(rsp.url)

    content_type = rsp.headers.get("Content-Type")

    try:
        # process 20x response, check response code first
        if status_ok(rsp.status_code):
            if content_type == "application/json":
                json_data = rsp.json()
                # 返回值必须符合文档的定义
                if "status" in json_data and "msg" in json_data:
                    return json_data
                else:
                    logger.error("invalid json response: %s, %s", cmd, json_data)

            # invalid response from trade server
            if content_type.startswith("text"):
                logger.error("invalid text response, %s, %s", cmd, rsp.text)
            else:
                logger.error("invalid response, %s, %s", cmd, rsp.raw)

        # process errros, response code as 40x, 50x
        else:
            if content_type == "application/json":
                result = rsp.json()
                logger.error(
                    "exec %s failed, response code: %d, msg: %s",
                    cmd,
                    rsp.status_code,
                    result,
                )
            else:  # just save content to log file
                logger.error(
                    "exec %s failed: response code: %d, extra msg: %s",
                    cmd,
                    rsp.status_code,
                    rsp.text,
                )

    except Exception as e:
        logger.exception(e)

    return None


def get(url, params=None, headers=None):
    """发送GET请求到上游服务接口，不建议带任何参数，Header除外

    Args:
        url : 目标URL，带服务器信息
        params : JSON格式的参数清单
        headers : 额外的header选项

    Returns:
        根据需求文档，上游服务必须JSON，否则就是错误
    """
    if headers is None:
        headers = {"Request-ID": uuid.uuid4().hex}
    else:
        headers.update({"Request-ID": uuid.uuid4().hex})

    rsp = requests.get(url, params=params, headers=headers)
    action = get_cmd(url)
    result = process_response_result(rsp, action)

    return result


def post_json(url, params=None, headers=None):
    """以POST发送JSON数据请求

    Args:
        url : 目标URL，带服务器信息
        params : JSON格式的参数清单
        headers : 额外的header选项

    Returns:
        根据需求文档，上游服务必须JSON，否则就是错误
    """
    if headers is None:
        headers = {"Request-ID": uuid.uuid4().hex}
    else:
        headers.update({"Request-ID": uuid.uuid4().hex})

    rsp = requests.post(url, json=params, headers=headers)

    action = get_cmd(url)
    result = process_response_result(rsp, action)

    return result
