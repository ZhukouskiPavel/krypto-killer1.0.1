from constants import Exchange
from core.settings import settings
from exchanges.base.service import BaseExchangeService


class ExmoService(BaseExchangeService):
    EXCHANGE = Exchange.EXMO

    def get_api_config(self) -> dict:
        config = settings.exchanges.exmo
        return {"apiKey": config.api_key, "secret": config.api_secret}
