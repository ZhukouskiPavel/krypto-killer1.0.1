from constants import Exchange
from core.settings import settings
from exchanges.base.service import BaseExchangeService


class BitgetService(BaseExchangeService):
    EXCHANGE = Exchange.BITGET

    def get_api_config(self) -> dict:
        config = settings.exchanges.bitget
        return {"apiKey": config.api_key, "secret": config.api_secret}
