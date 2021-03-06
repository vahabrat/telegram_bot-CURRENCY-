from ast import literal_eval
import telebot
from config import TOKEN
import requests
import db
from datetime import datetime
from datetime import timedelta
import re
import matplotlib.pylab as plt
import uuid

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands = ['list', 'lst'])
def get_currency(message):

    now = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    user_id= message.from_user.id
    recent_request_time = db.get_recent_request_time(user_id)

    if recent_request_time is not None:
        for item in recent_request_time:
            recent = datetime.strptime(item, '%Y-%m-%d %H:%M:%S')+timedelta(minutes=10)
            if now >= recent:
                res = requests.get('https://api.exchangeratesapi.io/latest?base=USD')
                data = res.json()
                currency_json = data["rates"]
                request_time = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                user_id = message.from_user.id
                db.set_recent_request_data(user_id, currency_json, request_time)
                for key, value in currency_json.items():
                    bot.send_message(message.chat.id, 'From server: ' + print_current(key, value), parse_mode="Markdown")
            else:
                recent_data = db.get_recent_request_data(user_id)
                for item in recent_data:
                    for key, value in literal_eval(item).items():
                       bot.send_message(message.chat.id, 'From database: ' + print_current(key, value), parse_mode="Markdown")
    else:
        res = requests.get('https://api.exchangeratesapi.io/latest?base=USD')
        data = res.json()
        currency_json = data["rates"]
        request_time = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        user_id = message.from_user.id
        db.set_recent_request_data(user_id, currency_json, request_time)
        for key, value in currency_json.items():
            bot.send_message(message.chat.id, 'First load: ' + print_current(key, value), parse_mode="Markdown")


@bot.message_handler(commands = ['exchange'])
def get_currency(message):

    res = requests.get('https://api.exchangeratesapi.io/latest?base=USD')
    data = res.json()
    currency_json = data["rates"]
    currency_type = re.findall('(?<= to[\s]).{3}', message.text) #return any next 3 chrachter after 'to' it means that we have to check if these 3 symbols presents in the json content

    if currency_json.get(currency_type[0]):#if currency pointed right
        input_quantity = ''.join(re.findall('(?<= \$)\d+', message.text) or re.findall('\d+(?=[\s]USD)', message.text))
        if input_quantity:
            if int(input_quantity):
                new_input_quantity = int(input_quantity)
                counted_currency = new_input_quantity * float(str(currency_json.get(currency_type[0])))
                bot.send_message(message.chat.id, '$' + str(round(counted_currency, 2)))
            else:
                bot.send_message(message.chat.id, 'Введите корректное значение количества валюты!')
        else:
            bot.send_message(message.chat.id, 'Введите количество валюты!')
    else:
        bot.send_message(message.chat.id, 'Не корректно указано название валюты!')


@bot.message_handler(commands = ['history'])
def get_history(message):
    input_quantity = ''.join(re.findall('(?<= for\s)\d+', message.text) or re.findall('\d+(?=[\s]days)', message.text))
    date = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S').date().isoformat()

    if input_quantity:
        if int(input_quantity):
            new_input_quantity = int(input_quantity)
            date_endpoint = (datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') - timedelta(days=new_input_quantity)).date().isoformat()
            symbol = ''.join(re.findall('(?<= USD/).{3}', message.text))
            res = requests.get(f'https://api.exchangeratesapi.io/history?start_at={date_endpoint}&end_at={date}&base=USD&symbols={symbol}')
            chart_json = res.json()
            chart_data_res = chart_json["rates"]
            dates, currency = [], []
            for key,value in sorted(chart_data_res.items()):
                dates.append(key)
                currency.append(value[symbol])
            fig = plt.figure()
            plt.plot(dates,currency)
            plt.xlabel("Дата (ГГГГ-ММ-ДД)")
            plt.ylabel("currency: " + symbol)
            #plt.show()
            unique_filename = str(uuid.uuid4())
            fig.savefig(f'./media/{unique_filename}.png')
            bot.send_photo(message.chat.id, photo=open(f'./media/{unique_filename}.png', 'rb'))
        else:
            bot.send_message(message.chat.id, 'Введите корректное значение количества дней!')
    else:
        bot.send_message(message.chat.id, 'Введите количество дней!')

def print_current(currency, value):
    return str(currency)+": "+str(value)


if __name__ == '__main__':
    db.init_db()
    bot.polling()


