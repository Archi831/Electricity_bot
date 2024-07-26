import telebot, json, os
import time as t
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))
def load_time_data():
    try:
        with open('time.json', 'r') as file:
            data = json.load(file)

    except:
        data = {"Today": [], "Tomorrow": []}

    return data

def load_user_data():
    try:
        with open('config.json', 'r') as file:
            data = json.load(file)

    except:
        data = {}

    return data

def get_table(day, Cherga):
    data = load_time_data()
    print(data[day][str(Cherga)])
    if len(data[day][str(Cherga)]) >= 1: 
        schedule = data[day]
        time = schedule.get(f'{Cherga}')
        table = "\n".join(f'{t[0]}:00 - {t[1]}:00 = {t[2]}год' for t in time)
    else:
        table = None
    return table

def choose_cherga(id, cher):
    if cher in ['1','2','3','4','5','6']:
        user_data = load_user_data()
        user_data[f'{id}'] = cher
        with open('config.json', 'w') as file:
            json.dump(user_data, file, indent=4)
        bot.send_message(id, f'Дякую! Ви обрали {cher} чергу')


        table = get_table("Today", cher)
        print(f'Asked for table, {id}')
        if table != None:
            bot.send_chat_action(id, 'typing')
            t.sleep(1)
            bot.send_message(id, f'Графік на сьогодні: \n{table}')
        elif table == None:
            bot.send_message(id, f'Графік на сьогодні порожній')
        
        table = get_table("Tomorrow", cher)
        if table != None:
            bot.send_chat_action(id, 'typing')
            t.sleep(1)
            bot.send_message(id, f'Графік на завтра: \n{table}')

    else:
        bot.send_message(id, 'Не зрозумів вас :(')

def set_cherga_callback(query):
    bot.answer_callback_query(query.id)
    choose_cherga(id=str(query.data)[5::], cher=str(query.data)[4])
