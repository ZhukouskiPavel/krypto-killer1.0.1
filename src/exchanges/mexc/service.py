from constants import Exchange
from core.settings import settings
from exchanges.base.service import BaseExchangeService


class MexcService(BaseExchangeService):
    EXCHANGE = Exchange.MEXC

    def get_api_config(self) -> dict:
        config = settings.exchanges.mexc
        return {"apiKey": config.api_key, "secret": config.api_secret}
