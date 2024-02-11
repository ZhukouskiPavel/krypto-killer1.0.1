from constants import Exchange
from core.settings import settings
from exchanges.base.service import BaseExchangeService


class KrakenService(BaseExchangeService):
    EXCHANGE = Exchange.KRAKEN

    def get_api_config(self) -> dict:
        config = settings.exchanges.kraken
        return {"apiKey": config.api_key, "secret": config.api_secret}
