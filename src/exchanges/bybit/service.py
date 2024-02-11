from constants import Exchange
from core.settings import settings
from exchanges.base.service import BaseExchangeService


class BybitService(BaseExchangeService):
    EXCHANGE = Exchange.BYBIT

    def get_api_config(self) -> dict:
        config = settings.exchanges.bybit
        return {"apiKey": config.api_key, "secret": config.api_secret}
