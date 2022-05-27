class TradeError(Exception):
    """交易中的异常

    当捕获异常后，可以通过status_code和message属性来获取错误代码和详细错误信息。
    """

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

    def __str__(self):
        return f"{self.message}: {self.args}"
