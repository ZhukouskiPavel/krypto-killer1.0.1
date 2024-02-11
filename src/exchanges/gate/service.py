from constants import Exchange
from core.settings import settings
from exchanges.base.service import BaseExchangeService


class GateService(BaseExchangeService):
    EXCHANGE = Exchange.GATE

    def get_api_config(self) -> dict:
        config = settings.exchanges.gate
        return {"apiKey": config.api_key, "secret": config.api_secret}
