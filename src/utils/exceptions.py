class ImproperlyConfigured(Exception):
    pass


class BaseExchangeError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class NoTickersToProcess(BaseExchangeError):
    pass
