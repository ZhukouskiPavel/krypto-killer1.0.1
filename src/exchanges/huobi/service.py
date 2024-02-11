from constants import Exchange
from core.settings import settings
from exchanges.base.service import BaseExchangeService


class HuobiService(BaseExchangeService):
    EXCHANGE = Exchange.HUOBI

    def get_api_config(self) -> dict:
        config = settings.exchanges.huobi
        return {"apiKey": config.api_key, "secret": config.api_secret}
