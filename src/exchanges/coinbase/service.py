from constants import Exchange
from core.settings import settings
from exchanges.base.service import BaseExchangeService


class CoinbaseService(BaseExchangeService):
    EXCHANGE = Exchange.COINBASE

    def get_api_config(self) -> dict:
        config = settings.exchanges.coinbase
        return {"apiKey": config.api_key, "secret": config.api_secret}
