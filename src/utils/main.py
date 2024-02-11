from __future__ import annotations

import asyncio
import threading
from functools import lru_cache

from loguru import logger

from core.logging import configure_logging
from exceptions import BaseExchangeError
from exchanges.base.service import BaseExchangeService
from exchanges.binance.service import BinanceService
from exchanges.bitfinex.service import BitfinexService
from exchanges.bitget.service import BitgetService
from exchanges.bybit.service import BybitService
from exchanges.coinbase.service import CoinbaseService
from exchanges.exmo.service import ExmoService
from exchanges.gate.service import GateService
from exchanges.huobi.service import HuobiService
from exchanges.kraken.service import KrakenService
from exchanges.kucoin.service import KucoinService
from exchanges.mexc.service import MexcService
from exchanges.okx.service import OkxService
from models import init_db
from telegram_bot.bot import run_bot

TICKERS_POLL_INTERVAL_IN_SECONDS = 30


@lru_cache
def _get_services() -> list[BaseExchangeService]:
    return [
        GateService(),  # registered api_key // --ERROR--
        HuobiService(),  # registered api_key
        KucoinService(), # registered api_key // --ERROR--
        OkxService(),  # registered api_key
        CoinbaseService(), # registered api_key // --ERROR--
        BinanceService(),  # registered api_key
        BybitService(), # registered api_key  // --ERROR--
        MexcService(), # registered api_key 90-days(02.03.2022)  // --ERROR--
        KrakenService(),  # registered api_key
        BitfinexService(), # registered api_key // --ERROR--
        ExmoService(),  # registered api_key
        BitgetService(),  # registered api_key
    ]


async def _get_tickers_stat() -> None:
    services = _get_services()
    tasks = [service.get_tickers_stat() for service in services]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result, service in zip(results, services):
        if not isinstance(result, Exception):
            continue
        if isinstance(result, BaseExchangeError):
            logger.error(f"{service.log_prefix} {result.message}")
        else:
            logger.opt(exception=result).error(
                f"{service.log_prefix} Error during getting tickers stat: {result}"
            )


async def main():
    await init_db()

    while True:
        await _get_tickers_stat()
        await asyncio.sleep(TICKERS_POLL_INTERVAL_IN_SECONDS)


if __name__ == "__main__":

    configure_logging()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        pass

# def start_bot():
#     updater.start_polling()
#     updater.idle()

# async def main():
#     await init_db()
#
#     while True:
#         await _get_tickers_stat()
#         await calculate_spread_and_save_to_csv()
#         await asyncio.sleep(TICKERS_POLL_INTERVAL_IN_SECONDS)
#
#
# async def run_all():
#     tasks = [asyncio.create_task(main())]
#     tasks += [asyncio.create_task(start_bot())]
#     await asyncio.gather(*tasks)
#
#
# if __name__ == "__main__":
#     configure_logging()
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#
#     try:
#         loop.run_until_complete(run_all())
#     except KeyboardInterrupt:
#         pass


