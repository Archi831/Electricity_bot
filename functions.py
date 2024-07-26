import telebot, subprocess, os
import time as t
from datetime import datetime
from config import load_time_data, load_user_data
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))

def refresh(id):
    subprocess.run(["python", "scraper.py"])

def keyboard_change_cherga(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    
    keyboard.row(
        telebot.types.InlineKeyboardButton('1', callback_data=f'set-1{message.from_user.id}'),
        telebot.types.InlineKeyboardButton('2', callback_data=f'set-2{message.from_user.id}'),
        telebot.types.InlineKeyboardButton('3', callback_data=f'set-3{message.from_user.id}')
    )
    
    keyboard.row(
        
        telebot.types.InlineKeyboardButton('4', callback_data=f'set-4{message.from_user.id}'),
        telebot.types.InlineKeyboardButton('5', callback_data=f'set-5{message.from_user.id}'),
        telebot.types.InlineKeyboardButton('6', callback_data=f'set-6{message.from_user.id}')
    )

    return keyboard

def wait_typing(message, time):
    bot.send_chat_action(message.chat.id, 'typing')
    t.sleep(time)

def periodic_refresh(interval, chat_id):
    HasData = True
    while True:
        refresh(chat_id)
        data = load_time_data()
        user_data = load_user_data()
        #notify_tomorrow func
        if (len(data["Tomorrow"]["1"]) >= 1 and not HasData) or (len(data["Tomorrow"]["2"]) >= 1 and not HasData) or (len(data["Tomorrow"]["3"]) >= 1 and not HasData):
            notify_tomorrow()
            HasData = True
        elif (len(data["Tomorrow"]["1"]) < 1) and (len(data["Tomorrow"]["2"]) < 1) and (len(data["Tomorrow"]["3"]) < 1):
            HasData = False

        #notify_Xminutes func
        for Cherga in range(1,7):
            schedule = data["Today"]
            time = schedule.get(f'{Cherga}')
            H, M = map(int, datetime.now().strftime("%H %M").split())
            for i in range(len(time)):
                if (int(time[i][0]) - H == 1) and ( (60-M) < 35) and ( (60-M) > 25) and  (H>7 and H<23):
                    for user_id, cherga in user_data.items():
                        try:
                            if int(Cherga) == int(cherga):
                                table = get_table("Today", cherga)
                                if table:
                                    print(f'Soon {Cherga}, {user_id}')
                                    bot.send_message(user_id, f'В {cherga} черзі незабаром вимкнуть світло \n{time[i][0]}:00 - {time[i][1]}:00')
                        except Exception as e:
                            print(f"Failed to send message to {user_id}: {e}")

        if M%10 > 2 and M%10 < 8:
            t.sleep((10-(M%10))*59)
        else:
            t.sleep(interval)

def notify_tomorrow():
    user_data = load_user_data()
    for user_id, Cherga in user_data.items():
        print(user_id, Cherga)
        try:
            table = get_table("Tomorrow", Cherga)
            if table != None:
                bot.send_message(int(user_id), f'Графік на завтра: \n{table}')
            else:
                bot.send_message(int(user_id), f'Графік на завтра порожній')

        except Exception as e:
            print(f"Failed to send message to {user_id}: {e}")

def get_table(day, Cherga):
    data = load_time_data()
    if len(data[day][str(Cherga)]) >= 1: 
        schedule = data[day]
        time = schedule.get(f'{Cherga}')
        table = "\n".join(f'{t[0]}:00 - {t[1]}:00 = {t[2]}год' for t in time)
    else:
        table = None
    return table
