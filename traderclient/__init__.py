"""Top-level package for zillionare-trader-client."""

__author__ = """Aaron Yang"""
__email__ = "code@jieyu.ai"
__version__ = "0.1.0"

from traderclient.client import TradeClient
from traderclient.trade import OrderSide, OrderStatus, OrderType

__all__ = (
    TradeClient,
    OrderStatus,
    OrderSide,
    OrderType,
)
