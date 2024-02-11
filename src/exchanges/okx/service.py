from constants import Exchange
from core.settings import settings
from exchanges.base.service import BaseExchangeService


class OkxService(BaseExchangeService):
    EXCHANGE = Exchange.OKX

    def get_api_config(self) -> dict:
        config = settings.exchanges.okx
        return {"apiKey": config.api_key, "secret": config.api_secret}
