from constants import Exchange
from core.settings import settings
from exchanges.base.service import BaseExchangeService


class BitfinexService(BaseExchangeService):
    EXCHANGE = Exchange.BITFINEX

    def get_api_config(self) -> dict:
        config = settings.exchanges.bitfinex
        return {"apiKey": config.api_key, "secret": config.api_secret}
