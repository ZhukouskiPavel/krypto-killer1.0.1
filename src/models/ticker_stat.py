from decimal import Decimal

import pymongo
from beanie import Document
from pydantic import validator

from constants import Exchange
from utils.helpers import get_utc_now_in_ms


class TickerStat(Document):
    exchange: Exchange
    # E.g. USDT/EUR
    symbol: str
    timestamp_ms: int
    high: Decimal
    low: Decimal
    bid: Decimal
    bid_volume: Decimal | None
    ask: Decimal
    ask_volume: Decimal | None
    # NOTE: for now we don't process if both of volumes below are None,
    # but if one of them is None, we calculate volume based on another and
    # a price
    base_volume: Decimal | None
    quote_volume: Decimal | None

    class Settings:
        indexes = [
            pymongo.IndexModel(
                [
                    ("symbol", pymongo.ASCENDING),
                    ("timestamp_ms", pymongo.DESCENDING),
                ],
                name="symbol_ASC__timestamp_ms_DESC",
            ),
        ]

    @validator("timestamp_ms", pre=True, always=True)
    def set_timestamp_ms(cls, value: int | None) -> int:
        return value or get_utc_now_in_ms()
