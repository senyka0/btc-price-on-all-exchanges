import asyncio
import ccxt.async_support as AsyncCcxt
import telebot
from telebot import types
import pandas as pd
bot = telebot.TeleBot('') #your bot token

async def loop(exchange_id):
    exchange = getattr(AsyncCcxt, exchange_id)()
    try:
        price = await exchange.fetch_ticker('BTC/USDT')
        await exchange.close()
        return {'exchange': exchange_id, 'price': price}
    except:
        await exchange.close()
        pass
async def run(exchanges):
    coroutines = [loop(exchange_id) for exchange_id in exchanges]
    return await asyncio.gather(*coroutines)




@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Price of BTC on all exchnges 🔄')
    markup.add(item1)
    bot.send_message(message.chat.id, "/start", reply_markup=markup)
@bot.message_handler(content_types=['text'])
def message(message):
    if message.text == 'Price of BTC on all exchnges 🔄':
        exchanges = AsyncCcxt.exchanges
        result = [{'exchange': i['exchange'], 'price': i['price']['last']} for i in filter(None, asyncio.run(run(exchanges)))]
        df = pd.DataFrame(result).sort_values(by=['price'], ascending=False).dropna()
        bot.send_message(message.chat.id, df.to_string(index=False))
        bot.send_message(message.chat.id, f'{df.iloc[-1]["exchange"]} ==> {df.iloc[0]["exchange"]}\n\n{df.iloc[-1]["price"]} ==> {df.iloc[0]["price"]}\n\n💵Profit: {(df.iloc[0]["price"]-df.iloc[-1]["price"])/df.iloc[-1]["price"]*100} %')
bot.infinity_polling()
