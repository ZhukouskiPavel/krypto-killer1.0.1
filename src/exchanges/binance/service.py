from constants import Exchange
from core.settings import settings
from exchanges.base.service import BaseExchangeService


class BinanceService(BaseExchangeService):
    EXCHANGE = Exchange.BINANCE


    def get_api_config(self) -> dict:
        config = settings.exchanges.binance
        return {"apiKey": config.api_key, "secret": config.api_secret}
