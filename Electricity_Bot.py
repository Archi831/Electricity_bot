import telebot, os, threading
from functions import refresh, keyboard_change_cherga, wait_typing, periodic_refresh, get_table
from config import choose_cherga, set_cherga_callback, load_user_data, load_time_data
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
    
    if Cherga: # Checks if cherga was selected
        table = get_table("Today", Cherga)
        print(f'Asked for table, {message.from_user.id}, {message.from_user.username}, {message.from_user.first_name}')
        bot.send_message(message.from_user.id, f'Графік на сьогодні: \n{table}')
        
        wait_typing(message, 0)
        table = get_table("Tomorrow", Cherga)
        if table:
            bot.send_message(message.from_user.id, f'Графік на завтра: \n{table}')
    
    # Guides to choose cherga
    else:
        keyboard = keyboard_change_cherga(message)
        print(f'Asked for table(no id), {message.from_user.id}')
        bot.send_message(message.from_user.id, 'Яка у вас черга?', reply_markup=keyboard)

@bot.message_handler(commands=['refresh'])
def admin(message):
    if str(message.from_user.id) == '722176554':
        refresh(message.from_user.id)
    else:
        bot.send_message(message.from_user.id, 'Запит на оновлення данних відправлено')
        bot.send_message(722176554, '/Refresh request')


@bot.message_handler(content_types=['text'])
def additional(message):
    print(f'{message.from_user.id} Written message: "{message.text}"')
    if (message.text).isdigit():
        choose_cherga(message.from_user.id, message.text)


@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    data = query.data
    if data.startswith('set-'):
        set_cherga_callback(query)

refresh_interval = 598
admin_chat_id = '722176554'
threading.Thread(target=periodic_refresh, args=(refresh_interval, admin_chat_id), daemon=True).start() 


bot.polling(none_stop=True, interval=0)
