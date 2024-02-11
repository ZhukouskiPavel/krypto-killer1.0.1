from constants import Exchange
from core.settings import settings
from exchanges.base.service import BaseExchangeService


class KucoinService(BaseExchangeService):
    EXCHANGE = Exchange.KUKOIN

    def get_api_config(self) -> dict:
        config = settings.exchanges.kucoin
        return {"apiKey": config.api_key, "secret": config.api_secret}
