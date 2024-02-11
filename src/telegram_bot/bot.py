import asyncio
import uuid

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler

from get_spread.spread import calculate_spread_and_save_to_csv


# user_id = None
EXCHANGE_MULTI_SELECTION, PROFIT_SELECTION = range(2)
CONVERSATION_END = ConversationHandler.END


is_script_configured = False


def start(update, context):
    # global user_id
    user_id = update.effective_chat.id
    context.user_data['user_id'] = user_id
    keyboard = [
        [InlineKeyboardButton("Начать настройку скрипта", callback_data='exchange_selection')],
        [InlineKeyboardButton("Отмена", callback_data='cancel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Привет! Настрой скрипт, чтобы начать поиск связок!",
                             reply_markup=reply_markup)

    # Set the state to EXCHANGE_MULTI_SELECTION
    return EXCHANGE_MULTI_SELECTION


def exchange_selection(update, context):
    exchanges = ['Binance', 'Bitfinex', 'Bitget', 'Bybit', 'Bittrex', 'Coinbase', 'Exmo', 'Gate', 'Huobi', 'Kraken',
                 'Kucoin', 'Mexc', 'Okx']
    query = update.callback_query
    query.answer()
    selected_exchanges = context.user_data.get('selected_exchanges', [])  # Получаем ранее выбранные биржи

    exchange = query.data

    if exchange in selected_exchanges:
        selected_exchanges.remove(exchange)  # Если биржа уже выбрана, удаляем ее из списка выбранных
    elif exchange == 'cancel':
        context.user_data.pop('selected_exchanges', None)  # Удаляем выбранные биржи из user_data
        context.bot.edit_message_text(chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      text="Вы отменили настройку скрипта")
        return CONVERSATION_END
    elif exchange != 'end':
        selected_exchanges.append(exchange)  # В противном случае, добавляем ее в список выбранных

    context.user_data['selected_exchanges'] = selected_exchanges  # Сохраняем выбранные биржи в user_data

    if exchange == 'end':
        keyboard = [
            [InlineKeyboardButton("От 3% до 6%", callback_data="profit_3_6")],
            [InlineKeyboardButton("От 6% до 9%", callback_data="profit_6_9")],
            [InlineKeyboardButton("От 9% до 20%", callback_data="profit_9_20")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        context.bot.edit_message_text(chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      text="Выберите процент прибыли от сделки:",
                                      reply_markup=reply_markup)
        return PROFIT_SELECTION
    elif exchange.startswith("profit"):
        context.bot.edit_message_text(chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      text="Скрипт начал поиск связок.")

        return CONVERSATION_END
    else:
        keyboard = [
            [InlineKeyboardButton(exchange, callback_data=exchange)]
            for exchange in exchanges
            if exchange not in selected_exchanges
        ]
        keyboard.append([InlineKeyboardButton("Завершить выбор", callback_data="end")])
        keyboard.append([InlineKeyboardButton("Отмена", callback_data='cancel')])

        reply_markup = InlineKeyboardMarkup(keyboard)

        selected_exchanges_text = '\n'.join(exchange for exchange in selected_exchanges
                                            if exchange != 'exchange_selection')
        message_text = f"Выберите одну или несколько бирж: \n\nВыбранные биржи:\n{selected_exchanges_text}"
        context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,
                                      text=message_text, reply_markup=reply_markup)
        return EXCHANGE_MULTI_SELECTION


def profit_selection(update, context):
    search_task_id = str(uuid.uuid4())
    context.user_data['search_task_id'] = search_task_id
    query = update.callback_query
    query.answer()
    profit_range = query.data
    context.user_data['selected_profit'] = profit_range
    # Вызываем функцию для расчета спреда и сохранения в CSV
    message_text = "Скрипт начал поиск связок."
    if profit_range.startswith("profit"):
        # Modify the text for a specific case
        message_text = "Скрипт начал поиск связок. Началась обработка данных."
    query.edit_message_text(text=message_text)

    loop = asyncio.new_event_loop()  # Создаем новый цикл событий
    asyncio.set_event_loop(loop)  # Устанавливаем его как текущий цикл событий

    async def run_calculation():
        await calculate_spread_and_save_to_csv(context, search_task_id)

    # Запускаем асинхронную задачу в новом цикле событий
    loop.run_until_complete(run_calculation())

    # Завершаем и закрываем цикл событий
    loop.close()
    asyncio.set_event_loop(None)  # Сбрасываем текущий цикл событий

    # global is_script_configured
    # is_script_configured = True
    # if is_script_configured:
    #     # Вызов функции только если скрипт настроен
    #     while is_script_configured:
    #         asyncio.run(calculate_spread_and_save_to_csv(context))
    #     # asyncio.run(calculate_spread_and_save_to_csv(context))
    return CONVERSATION_END


def cancel(update, context):
    # global user_id
    user_id = None
    query = update.callback_query
    query.edit_message_text(text="Вы отменили настройку скрипта")
    # Удаляем выбранные биржи из user_data
    context.user_data.pop('selected_exchanges', None)
    context.user_data.pop('search_task_id', None)

    return CONVERSATION_END


def run_bot():
#заменить токен
    updater = Updater("5920288353:AAHbusPs1cfI04UnID-LsFUOvg9QGKmuTd8", use_context=True)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            EXCHANGE_MULTI_SELECTION: [CallbackQueryHandler(exchange_selection)],
            PROFIT_SELECTION: [CallbackQueryHandler(profit_selection)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conv_handler)

    dp.add_handler(CallbackQueryHandler(cancel, pattern='^cancel$'))
    updater.start_polling()
    updater.idle()
