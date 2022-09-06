import telebot
from telebot import types
import time
import schedule
from threading import Thread
import datetime

bot = telebot.TeleBot('Token')
schedule1 = schedule.Scheduler()


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("💻 Новое обращение")
    btn2 = types.KeyboardButton("🍽 Обед 30 мин")
    btn3 = types.KeyboardButton("🏖 Перерыв 15 мин")
    btn4 = types.KeyboardButton("✅ Обращение завершено")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, text="Привет, {0.first_name}! Я бот для твоей работы. Сейчас я расскажу тебе о "
                                           "своих возможностях".format(message.from_user), reply_markup=markup)
    bot.send_message(message.chat.id, text="Накануне рабочего дня ты можешь переслать мне из рабочего бота сообщение "
                                           "с временем твоей следующей смены. За 5 минут до начала и конца рабочего "
                                           "дня я пришлю тебе напоминание")
    bot.send_message(message.chat.id, text="Если ты хочешь, чтобы я напомнил тебе о твоих перерывах, просто перешли"
                                           " из рабочего бота сообщение с временем твоих перерывов и я так же напомню"
                                           " за 5 минут до их начала")
    bot.send_message(message.chat.id, text="Когда ты получишь новое обращение - просто нажми на кнопку "
                                           "'💻 Новое обращение' и я отправлю тебе напоминание за 5 минут и за 1 минуту до "
                                           "того, как обращение слетит")
    bot.send_message(message.chat.id, text="Если закончишь работать над обращением раньше, то нажми кнопку"
                                           " '✅ Обращение завершено' и никаких напоминаний не придет")
    bot.send_message(message.chat.id, text="Когда настанет время отдохнуть или перекусить - нажми '🍽 Обед 30 мин' и я "
                                           "пришлю напоминание за 1 минуту до конца обеда, или нажми "
                                           "'🏖 Перерыв 15 мин' и я  напомню за 1 минуту до конца перерыва")



def schedule_checker():
    while True:
        schedule.run_pending()
        schedule1.run_pending()
        time.sleep(1)


@bot.message_handler(func=lambda message: True)
def fio(message):
    dinner_or_pause = "Работа работой, а отдых по расписанию! Я тебе напомню, когда пора взяться за работу."
    new_appeal = "Начинаю обратный отсчет! Когда время будет на исходе ты получишь уведомление."
    end_appeal = "Обращение завершено! Если получишь новое обращение - просто нажми на соответствующую кнопку"
    text = message.text
    if text == "💻 Новое обращение":
        bot.send_message(message.chat.id, text=new_appeal)
        schedule.clear(message.chat.id)
        schedule.every(25).minutes.do(get_sending_function(message.chat.id)).tag(message.chat.id)
        schedule.every(29).minutes.do(get_sending_notification(message.chat.id)).tag(message.chat.id)
    if text == "✅ Обращение завершено" and len(schedule.get_jobs(message.chat.id)) >= 1:
        schedule.clear(message.chat.id)
        bot.send_message(message.chat.id, text=end_appeal)
    elif text == "✅ Обращение завершено" and len(schedule.get_jobs(message.chat.id)) == 0:
        schedule.clear(message.chat.id)
    elif len(text) > 21:
        f_str = text.split('\n')
        if f_str[0].strip() == "Ближайшие смены:":
            bot.send_message(message.chat.id, text='Понял принял')
            work_time = f_str[1][-14:len(f_str[1])]
            start_time, end_time = time_extraction(work_time)
            schedule1.every().day.at(f"{start_time.time()}").do(send_start_time(message.chat.id, "Рабочий день начнется")).tag(message.chat.id)
            schedule1.every().day.at(f"{end_time.time()}").do(send_start_time(message.chat.id, "Рабочий день закончится")).tag(message.chat.id)
        elif f_str[0][:5] == "Смена":
            bot.send_message(message.chat.id, text='Понял принял')
            start_times = []
            for i in range(1, len(f_str)):
                pause_time = f_str[i][-14:len(f_str[i])]
                start_time, _ = time_extraction(pause_time)
                start_times.append(start_time)
            for i in range(len(start_times)):
                schedule1.every().day.at(f"{start_times[i].time()}").do(send_start_time(message.chat.id, "Перерыв")).tag(message.chat.id)
    elif text == "🍽 Обед 30 мин":
        schedule.clear(message.chat.id)
        bot.send_message(message.chat.id, dinner_or_pause)
        schedule.every(29).minutes.do(get_sending_dinner(message.chat.id)).tag(message.chat.id)
    elif text == "🏖 Перерыв 15 мин":
        schedule.clear(message.chat.id)
        bot.send_message(message.chat.id, dinner_or_pause)
        schedule.every(14).minutes.do(get_sending_dinner(message.chat.id)).tag(message.chat.id)



    print(schedule.get_jobs())
    print(schedule1.get_jobs())

def time_extraction(work_time):
    start_time, end_time = work_time.split(' - ')
    st_h, st_m = list(map(int, start_time.split(':')))
    end_h, end_m = list(map(int, end_time.split(':')))
    start_iso_time, end_iso_time = datetime.time(st_h, st_m), datetime.time(end_h, end_m)
    start_date = datetime.date.today()
    end_date = datetime.date.today()
    start_dt = datetime.datetime.combine(start_date, start_iso_time) - datetime.timedelta(minutes=5)
    end_dt = datetime.datetime.combine(end_date, end_iso_time) - datetime.timedelta(minutes=5)
    return start_dt, end_dt


def send_start_time(chatId, type_notification):
    def send_function():
        bot.send_message(chatId, f"{type_notification} через 5 минут!")
        return schedule.CancelJob
    return send_function


def get_sending_function(chatId):
    def send_function():
        bot.send_message(chatId, "Осталось 5 минут! Скоро обращение слетит!")
        return schedule.CancelJob
    return send_function


def get_sending_notification(chatId):
    def send_function():
        bot.send_message(chatId, "Осталась 1 минута! Приготовься ловить!")
        return schedule.CancelJob
    return send_function


def get_sending_dinner(chatId):
    def send_function():
        bot.send_message(chatId, "Осталась 1 минута! Приготовься к работе!")
        return schedule.CancelJob
    return send_function


if __name__ == "__main__":
    scheduleThread = Thread(target=schedule_checker)
    scheduleThread.daemon = True
    scheduleThread.start()

    bot.polling()

