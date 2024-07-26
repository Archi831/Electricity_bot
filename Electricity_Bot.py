import time as t

import os
import telebot
import threading

from config import choose_cherga, set_cherga_callback, load_user_data
from functions import refresh, keyboard_change_cherga, wait_typing, periodic_refresh, get_table, notify_tomorrow

token = os.getenv('TELEGRAM_BOT_TOKEN')
if not token:
    raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables")
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['change'])
def change(message):
    keyboard = keyboard_change_cherga(message)
    print(f'Change request, {message.from_user.id}')
    bot.send_message(message.from_user.id, 'Яка у вас черга?', reply_markup=keyboard)


@bot.message_handler(commands=['start'])
def start(message):
    wait_typing(message, 1)

    config = load_user_data()
    Cherga = config.get(f'{message.from_user.id}')

    if Cherga:
        table = get_table("Today", Cherga)
        if table is not None:
            print("Sent message to user ", message.from_user.id, 'Графік на сьогодні: table')
            bot.send_message(message.from_user.id, f'Графік на сьогодні: \n{table}')
        elif table is None:
            bot.send_message(message.from_user.id, f'Графік на сьогодні порожній')

        table = get_table("Tomorrow", Cherga)
        if table is not None:
            wait_typing(message, 1)
            print("Sent message to user", message.from_user.id, 'Графік на завтра: table')
            bot.send_message(message.from_user.id, f'Графік на завтра: \n{table}')

    else:
        keyboard = keyboard_change_cherga(message)
        print(f'Asked for table(no id), {message.from_user.id}')
        bot.send_message(message.from_user.id, 'Яка у вас черга?', reply_markup=keyboard)


@bot.message_handler(commands=['refresh'])
def admin(message):
    if str(message.from_user.id) == '':
        refresh()
        notify_tomorrow()

    else:
        bot.send_message(message.from_user.id, 'Запит на оновлення данних відправлено')
        bot.send_message(id, '/Refresh request')


@bot.message_handler(content_types=['text'])
def additional(message):
    print(f'{message.from_user.id} Written message: "{message.text}"')
    if message.text.isdigit():
        choose_cherga(message.from_user.id, message.text)


@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    data = query.data
    if data.startswith('set-'):
        set_cherga_callback(query)


refresh_interval = 598
admin_chat_id = '722176554'
threading.Thread(target=periodic_refresh, args=(refresh_interval, admin_chat_id), daemon=True).start()

while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=60)
    except Exception as e:
        print(f"Error: {e}")
        t.sleep(15)
