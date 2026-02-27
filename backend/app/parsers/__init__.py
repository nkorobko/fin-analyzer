"""CSV parsers for Israeli banks"""
from .base import BaseParser
from .leumi import LeumiParser
from .hapoalim import HapoalimParser
from .discount import DiscountParser
from .max import MaxParser
from .cal import CalParser

__all__ = [
    'BaseParser',
    'LeumiParser',
    'HapoalimParser',
    'DiscountParser',
    'MaxParser',
    'CalParser',
]
