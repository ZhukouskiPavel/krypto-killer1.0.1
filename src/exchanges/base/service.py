import time
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field

from constants import EXCHANGE_TO_API_MAP, SYMBOL_TEMPLATE, Exchange
from core.settings import settings
from exceptions import ImproperlyConfigured, NoTickersToProcess
from models import TickerStat
from repositories import repository
from utils.helpers import get_utc_now_in_ms

CACHE_EXPIRE_TS_IN_MS = 60 * 1 * 1000  # 10 minutes


class TickerCache(BaseModel):
    tickers: list[str]
    timestamp_ms: int = Field(default_factory=get_utc_now_in_ms)

    def is_valid(self) -> bool:
        return (get_utc_now_in_ms() - self.timestamp_ms) < CACHE_EXPIRE_TS_IN_MS


class BaseExchangeService:
    EXCHANGE: Exchange

    def __init_subclass__(cls, **kwargs: Any):
        if not cls.EXCHANGE:
            raise ImproperlyConfigured(f"{cls.__name__} must define EXCHANGE attribute")
        super().__init_subclass__(**kwargs)

    def __init__(self) -> None:
        api_class = EXCHANGE_TO_API_MAP.get(self.EXCHANGE)
        if not api_class:
            raise ImproperlyConfigured(f"API class for {self.EXCHANGE} not found")
        self.api = api_class(self.get_api_config())
        self._cached_tickers: TickerCache | None = None
        self.log_prefix = f"[{self.__class__.__name__}]"

    def get_api_config(self) -> dict:
        return {}

    async def get_tickers_stat(self) -> None:
        start = time.time()
        logger.info(
            f"{self.log_prefix} Start get_tickers_stat() for {self.EXCHANGE.value}"
        )
        tickers = await self._get_tickers_to_process()
        tickers_data = await self.api.fetch_tickers(tickers)


        await repository.ticker_stat.bulk_save(self.parse_response(tickers_data))
        logger.info(
            f"{self.log_prefix} End get_tickers_stat() for {self.EXCHANGE.value} "
            f"in {round(time.time() - start, 5)} seconds. "
            f"Processed {len(tickers_data)} tickers"
        )

    def parse_response(self, tickers_data: dict) -> list[TickerStat]:
        """
        Parser incoming list of ticker to internal object
        :param tickers_data: list of ticker data (format can be found here
        https://docs.ccxt.com/en/latest/manual.html#ticker-structure
        :return: a list of TickerStat
        """
        result = []
        for data in tickers_data.values():
            market = self.api.market(data["symbol"])

            result.append(
                TickerStat(
                    exchange=self.EXCHANGE,
                    symbol=SYMBOL_TEMPLATE.format(
                        base=market["base"], quote=market["quote"]
                    ),
                    timestamp_ms=data["timestamp"],
                    high=data["high"],
                    low=data["low"],
                    bid=data["bid"],
                    bid_volume=data["bidVolume"],
                    ask=data["ask"],
                    ask_volume=data["askVolume"],
                    vwap=data["vwap"],
                    base_volume=data["baseVolume"],
                    quote_volume=data["quoteVolume"],
                )
            )
        return result

    async def _get_tickers_to_process(self) -> list[str]:
        if not (self._cached_tickers and self._cached_tickers.is_valid()):
            all_tickers_data = await self.api.fetch_tickers()
            self._cached_tickers = TickerCache(
                tickers=self._filter_tickers(all_tickers_data)
            )
        return self._cached_tickers.tickers

    def _filter_tickers(self, all_tickers_data: dict) -> list[str]:
        tickers = []
        currency = settings.exchanges.main_currency
        for ticker, data in all_tickers_data.items():
            # Sometimes fetch_tickers return more currencies than self.markets, and
            # we get an error that exchange "does not have market symbol ..."
            # TODO: тут бы проверять еще доступность ввода и вывода монеты на кошелек на каждой бирже, но эти данные
            #  не приходят я смотрел. Метод следующий:
            #  market = exchange.market
            #  market['info']['is_deposit_enabled'] и market['info']['is_withdrawal_enabled']
            #  это из документации

            if not (ticker in self.api.markets and self.api.markets[ticker]["active"]):
                continue

            market = self.api.market(ticker)
            if currency not in (market["quote"], market["base"]):
                continue

            use_base_volume = currency == market["base"]
            volume = self._calculate_volume(data, use_base_volume)
            if volume < settings.exchanges.min_volume_to_process:
                continue
            tickers.append(ticker)

        if not tickers:
            raise NoTickersToProcess(
                f"No tickers to process from original "
                f"{len(all_tickers_data)} tickers"
            )
        logger.info(
            f"{self.log_prefix} Filtering results: "
            f"{len(tickers)}/{len(all_tickers_data)} meet expectations"
        )
        return tickers

    @staticmethod
    def _calculate_volume(data: dict, use_base_volume: bool) -> float:
        base_volume = data["baseVolume"]
        quote_volume = data["quoteVolume"]
        if use_base_volume:
            if base_volume:
                return base_volume
            # Use highest price to get minimal volume (safety measure)
            # TODO: check if it's right approach
            elif quote_volume and data["high"]:
                # E.g. we have pair USTD/BTC, we need volume in USDT, and we know that
                # volume in BTC was 3 BTC and the price was 0.01 BTC for 1 USDT ->
                # 3 / 0.01 = 300 USDT (volume in USDT)
                return quote_volume / data["high"]
        else:
            if quote_volume:
                return quote_volume
            # Use lowest price to get minimal volume (safety measure)
            # TODO: check if it's right approach
            elif base_volume and data["high"]:
                # E.g. we have pair BTC/USDT, we need volume in USDT, and we know
                # that volume in BTC was 3 BTC and the price was 100 USDT for 1 BTC ->
                # 3 * 100 = 300 USDT (volume in USDT)
                return base_volume * data["low"]
        return 0
