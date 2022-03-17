import logging


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


def stock_name(code: str):
    # code: 002537
    # return "002537.XSHE

    if len(code) != 6:
        return "000000.XXXX"
    if code[0] == "0":
        return f"{code}.XSHE"
    if code[0] == "6":
        return f"{code}.XSHG"

    return "000000.XXXX"
