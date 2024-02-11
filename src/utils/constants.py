from enum import StrEnum
from pathlib import Path

import ccxt.async_support as ccxt

PROJECT_ROOT = Path(__file__).parent.parent
SYMBOL_TEMPLATE = "{base}/{quote}"


class Exchange(StrEnum):
    GATE = "GATE"
    HUOBI = "HUOBI"
    KUKOIN = "KUKOIN"
    OKX = "OKX"
    COINBASE = "COINBASE"
    BINANCE = "BINANCE"
    BYBIT = "BYBIT"
    MEXC = "MEXC"
    KRAKEN = "KRAKEN"
    BITFINEX = "BITFINEX"
    EXMO = "EXMO"
    BITGET = "BITGET"


EXCHANGE_TO_API_MAP = {
    Exchange.GATE: ccxt.gate, # no networks
    Exchange.HUOBI: ccxt.huobi, # есть сети!!!
    Exchange.KUKOIN: ccxt.kucoin, # no networks
    Exchange.OKX: ccxt.okx, # no networks -вообще возвращает None
    Exchange.COINBASE: ccxt.coinbase, # no networks
    Exchange.BINANCE: ccxt.binance, # no networks -вообще возвращает None
    Exchange.BYBIT: ccxt.bybit, # no networks -вообще возвращает None
    Exchange.MEXC: ccxt.mexc, # есть сети!!!
    Exchange.KRAKEN: ccxt.kraken, # no networks
    Exchange.BITFINEX: ccxt.bitfinex, # возвращает пустой словарь
    Exchange.EXMO: ccxt.exmo, #  нету сетей но в словаре comments можно встретиттьь упоминание о сетя но не на всех валютах
    Exchange.BITGET: ccxt.bitget,  # есть сети!!!

}
