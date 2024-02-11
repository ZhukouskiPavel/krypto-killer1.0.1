import datetime
import time

from decimal import Decimal
from itertools import combinations, permutations

import telegram
from motor.motor_asyncio import AsyncIOMotorClient
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from core.settings import DBSettings

MINUTE_INTERVAL = 3  # интервал в минутах для фильтрации актуальных данных из базы данных


async def get_message_by_id(bot, chat_id, message_id):
    try:
        message = await bot.get_chat(chat_id=chat_id, message_id=message_id)
        return message
    except Exception:
        return None


async def calculate_spread_and_save_to_csv(context, search_task_id):
    # Создаем экземпляр класса DBSettings
    while search_task_id == context.user_data.get('search_task_id'):
        db_settings = DBSettings()

        # Подключаемся к MongoDB
        client = AsyncIOMotorClient(db_settings.url)
        db = client[db_settings.name]
        collection = db['TickerStat']

        profit_from = Decimal(context.user_data['selected_profit'].split("_")[1])
        profit_to = Decimal(context.user_data['selected_profit'].split("_")[2])
        exchanges = context.user_data['selected_exchanges']
        user_id = context.user_data['user_id']
        # Получаем все записи из коллекции ticker_stats
        ticker_stats = await collection.find().to_list(length=None)

        print(type(profit_to))

        # Получаем список уникальных валютных пар
        symbol_set = set(ticker_stat['symbol'] for ticker_stat in ticker_stats)
        results = []
        # Вычисляем спред для каждой пары криптовалют
        for symbol in symbol_set:
            # заданный промежуток в мс
            minute_ago = (datetime.datetime.now() - datetime.timedelta(minutes=MINUTE_INTERVAL)).timestamp() * 1000

            # Получаем все записи для текущей валютной пары за заданное последнее время
            ticker_stats_for_symbol = await collection.find({
                'symbol': symbol,
                'timestamp_ms': {'$gt': minute_ago}
            }).to_list(length=None)

            # ticker_stats_for_symbol = await collection.find({'symbol': symbol}).to_list(length=None)

            # Получаем список уникальных бирж для текущей валютной пары
            exchange_set = set(ticker_stat['exchange'] for ticker_stat in ticker_stats_for_symbol)

            # Вычисляем спред и профит для каждой пары бирж
            for buy_exchange, sell_exchange in combinations(exchange_set, 2):
                buy_ticker_stat = next(t for t in ticker_stats_for_symbol if t['exchange'] == buy_exchange)
                sell_ticker_stat = next(t for t in ticker_stats_for_symbol if t['exchange'] == sell_exchange)
                buy_price = Decimal(buy_ticker_stat['bid'].to_decimal())
                sell_price = Decimal(sell_ticker_stat['ask'].to_decimal())
                spread = sell_price - buy_price
                profit = ((sell_price / buy_price) - 1) * 100
                if profit_from < profit < profit_to:
                    rounded_profit = round(profit, 2)
                    # Записываем результат в консоль и в csv файл
                    results.append({
                        'Symbol': symbol,
                        'Exchange to Buy': buy_exchange,
                        'Buy Price': buy_price,
                        'Exchange to Sell': sell_exchange,
                        'Sell Price': sell_price,
                        'Spread': spread,
                        'Profit': rounded_profit
                    })
                    print('Инфа идет....')
        message_text = "Результаты связок:\n"

        stop_button = InlineKeyboardButton("Остановить поиск", callback_data="stop_search")
        keyboard = InlineKeyboardMarkup([[stop_button]])

        for result in results:
            message_text += f"{result['Exchange to Buy']} -> {result['Exchange to Sell']} {result['Symbol']}:\n" \
                            f"купить за {result['Buy Price']} на {result['Exchange to Buy']},\n " \
                            f"продать за {result['Sell Price']} на {result['Exchange to Sell']},\n " \
                            f"спред: {result['Spread']}, профит: {result['Profit']}%\n\n"
        if 'message_id' in context.user_data:
            message_id = context.user_data['message_id']
            message = await get_message_by_id(context.bot, user_id, message_id)
            current_message = message.text if message else None

            if current_message != message_text:
                try:
                    context.bot.edit_message_text(chat_id=user_id, message_id=message_id,
                                                  text=message_text, reply_markup=keyboard)
                except telegram.error.BadRequest as e:
                    if "Message is not modified" in str(e):
                        # Handle the case when the message content is not modified
                        # Add your logic here to either skip the editing or modify the message in a noticeable way
                        pass
                    else:
                        # Handle other BadRequest errors
                        raise
                # await context.bot.edit_message_text(chat_id=user_id, message_id=message_id,
                #                                     text=message_text, parse_mode='Markdown', reply_markup=keyboard)


        # if 'message_id' in context.user_data:
        #     message_id = context.user_data['message_id']
        #     context.bot.edit_message_text(chat_id=user_id, message_id=message_id,
        #                                   text=message_text, parse_mode='Markdown', reply_markup=keyboard)
        #     time.sleep(30)
        else:
            message = context.bot.send_message(chat_id=user_id, text=message_text,
                                               parse_mode='Markdown', reply_markup=keyboard)
            context.user_data['message_id'] = message.message_id




# async def calculate_spread_and_save_to_csv(context, search_task_id):
#     while search_task_id == context.user_data.get('search_task_id'):
#         db_settings = DBSettings()
#
#         client = AsyncIOMotorClient(db_settings.url)
#         db = client[db_settings.name]
#         collection = db['TickerStat']
#
#         profit_from = Decimal(context.user_data['selected_profit'].split("_")[1])
#         profit_to = Decimal(context.user_data['selected_profit'].split("_")[2])
#         exchanges = context.user_data['selected_exchanges']
#         user_id = context.user_data['user_id']
#
#         ticker_stats = await collection.find().to_list(length=None)
#
#         symbol_set = set(ticker_stat['symbol'] for ticker_stat in ticker_stats)
#         results = []
#
#         for symbols in permutations(symbol_set, 3):
#             minute_ago = (datetime.datetime.now() - datetime.timedelta(minutes=MINUTE_INTERVAL)).timestamp() * 1000
#
#             ticker_stats_for_symbols = await collection.find({
#                 'symbol': {'$in': list(symbols)},
#                 'timestamp_ms': {'$gt': minute_ago}
#             }).to_list(length=None)
#
#             exchange_set = set(ticker_stat['exchange'] for ticker_stat in ticker_stats_for_symbols)
#
#             # Проверяем, есть ли все необходимые валюты в связке
#             if len(exchange_set) == 3:
#                 ticker_stats_by_exchange = {ticker_stat['exchange']: ticker_stat for ticker_stat in ticker_stats_for_symbols}
#
#                 # Ищем тикеры для каждой валюты
#                 buy_symbol, intermediate_symbol, sell_symbol = symbols
#                 buy_ticker_stat = ticker_stats_by_exchange[buy_symbol]
#                 intermediate_ticker_stat = ticker_stats_by_exchange[intermediate_symbol]
#                 sell_ticker_stat = ticker_stats_by_exchange[sell_symbol]
#
#                 buy_price = Decimal(buy_ticker_stat['bid'].to_decimal())
#                 intermediate_price = Decimal(intermediate_ticker_stat['bid'].to_decimal())
#                 sell_price = Decimal(sell_ticker_stat['ask'].to_decimal())
#
#                 # Вычисляем спред и профит
#                 spread = sell_price - buy_price
#                 profit = ((sell_price / buy_price) - 1) * 100
#
#                 if profit_from < profit < profit_to:
#                     rounded_profit = round(profit, 2)
#                     results.append({
#                         'Symbols': symbols,
#                         'Buy Exchange': buy_ticker_stat['exchange'],
#                         'Buy Price': buy_price,
#                         'Intermediate Exchange': intermediate_ticker_stat['exchange'],
#                         'Intermediate Price': intermediate_price,
#                         'Sell Exchange': sell_ticker_stat['exchange'],
#                         'Sell Price': sell_price,
#                         'Spread': spread,
#                         'Profit': rounded_profit
#                     })
#                     print('Инфа идет....')
#
#         message_text = "Результаты связок:\n"
#
#         stop_button = InlineKeyboardButton("Остановить поиск", callback_data="stop_search")
#         keyboard = InlineKeyboardMarkup([[stop_button]])
#
#         for result in results:
#             message_text += f"{result['Buy Exchange']} -> {result['Intermediate Exchange']} -> {result['Sell Exchange']}: \n" \
#                             f"купить {result['Symbols'][0]} за {result['Buy Price']} на {result['Buy Exchange']},\n " \
#                             f"обменять на {result['Symbols'][1]} по цене {result['Intermediate Price']} на {result['Intermediate Exchange']},\n " \
#                             f"продать {result['Symbols'][2]} за {result['Sell Price']} на {result['Sell Exchange']},\n " \
#                             f"спред: {result['Spread']}, профит: {result['Profit']}%\n\n"
#
#             if 'message_id' in context.user_data:
#                 message_id = context.user_data['message_id']
#                 context.bot.edit_message_text(chat_id=user_id, message_id=message_id,
#                                               text=message_text, parse_mode='Markdown', reply_markup=keyboard)
#             else:
#                 message = context.bot.send_message(chat_id=user_id, text=message_text,
#                                                    parse_mode='Markdown', reply_markup=keyboard)
#                 context.user_data['message_id'] = message.message_id

