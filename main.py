import telebot
from telebot import types
import time
import schedule
from threading import Thread
import datetime

bot = telebot.TeleBot('TOKEN')
schedule1 = schedule.Scheduler()
schedule2 = schedule.Scheduler()

counter_solved = {}
counter_adjacent = {}
counter_other = {}

shifts = ['Your shifts were', 'Closest upcoming', 'Ближайшие смены:', 'Твои смены измен']
pauses = ['Смена', 'Shift']

delta = datetime.timedelta(minutes=5)


phrases = {'new_appeal': "Начинаю обратный отсчет! Когда время будет на исходе ты получишь уведомление.",
           'end_appeal': "Обращение завершено! Если получишь новое обращение - просто нажми на соответствующую кнопку",
           'dinner_or_pause': "Работа работой, а отдых по расписанию! Я тебе напомню, когда пора взяться за работу.",
           'start_work_day': "Рабочий день начнется через 5 минут",
           'dinner_time': "Обед начнется через 5 минут",
           'pause_time': "Перерыв начнется через 5 минут",
           'end_work_day': "Рабочий день закончится через 5 минут",
           'almost_the_end_appeal_time': "Осталось 5 минут! Скоро обращение слетит!",
           'end_appeal_time': "Осталась 1 минута! Приготовься ловить!",
           'end_pause': "Осталась 1 минута! Приготовься к работе!",
           'excellent_ticket': "Отличное время для решения тикета закончилось",
           'good_ticket': "Хорошее время для решения тикета закончилось",
           'request_statistics': "Рабочий день закончился! Когда закончишь обращение нажми '+' и я пришлю статистику за день",
           'accepted': "Понял-принял)",
          }


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("💻 Новое обращение")
    btn2 = types.KeyboardButton("🍽 Обед 30 мин")
    btn3 = types.KeyboardButton("🏖 Перерыв 15 мин")
    btn4 = types.KeyboardButton("✅ Решено")
    btn5 = types.KeyboardButton("✅ Смежники")
    btn6 = types.KeyboardButton("✅ Остальные")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
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
    bot.send_message(message.chat.id, text="Если закончишь работать над обращением раньше, то нажми одну из 3 кнопок"
                                           " '✅ Решено', '✅ Смежники' или '✅ Остальные'  и никаких напоминаний не придет")
    bot.send_message(message.chat.id, text="Когда настанет время отдохнуть или перекусить - нажми '🍽 Обед 30 мин' и я "
                                           "пришлю напоминание за 1 минуту до конца обеда, или нажми "
                                           "'🏖 Перерыв 15 мин' и я  напомню за 1 минуту до конца перерыва")
    bot.send_message(message.chat.id, text="В конце рабочего дня пришли мне '+' и я покажу статистику за смену")


def schedule_checker():
    while True:
        schedule.run_pending()
        schedule1.run_pending()
        schedule2.run_pending()
        time.sleep(1)


@bot.message_handler(func=lambda message: True)
def fio(message):
    global counter_solved, counter_other, counter_adjacent
    text = message.text
    if text == "💻 Новое обращение":
        bot.send_message(message.chat.id, text=phrases['new_appeal'])
        schedule.clear(message.chat.id)
        schedule.every(5).minutes.do(get_sending_function(message.chat.id, phrases['excellent_ticket'])).tag(message.chat.id)
        schedule.every(7).minutes.do(get_sending_function(message.chat.id, phrases['good_ticket'])).tag(message.chat.id)
        schedule.every(25).minutes.do(get_sending_function(message.chat.id, phrases['almost_the_end_appeal_time'])).tag(message.chat.id)
        schedule.every(29).minutes.do(get_sending_function(message.chat.id, phrases['end_appeal_time'])).tag(message.chat.id)
    if text == "✅ Решено" and len(schedule.get_jobs(message.chat.id)) >= 1:
        counter_solved[message.chat.id] = counter_solved.get(message.chat.id, 0) + 1
        schedule.clear(message.chat.id)
        bot.send_message(message.chat.id, text=phrases['end_appeal'])
    elif text == "✅ Решено" and len(schedule.get_jobs(message.chat.id)) == 0:
        counter_solved[message.chat.id] = counter_solved.get(message.chat.id, 0) + 1
        schedule.clear(message.chat.id)
    elif text == "✅ Смежники" and len(schedule.get_jobs(message.chat.id)) >= 1:
        counter_adjacent[message.chat.id] = counter_adjacent.get(message.chat.id, 0) + 1
        schedule.clear(message.chat.id)
        bot.send_message(message.chat.id, text=phrases['end_appeal'])
    elif text == "✅ Смежники" and len(schedule.get_jobs(message.chat.id)) == 0:
        counter_adjacent[message.chat.id] = counter_adjacent.get(message.chat.id, 0) + 1
        schedule.clear(message.chat.id)
    elif text == "✅ Остальные" and len(schedule.get_jobs(message.chat.id)) >= 1:
        counter_other[message.chat.id] = counter_other.get(message.chat.id, 0) + 1
        schedule.clear(message.chat.id)
        bot.send_message(message.chat.id, text=phrases['end_appeal'])
    elif text == "✅ Остальные" and len(schedule.get_jobs(message.chat.id)) == 0:
        counter_other[message.chat.id] = counter_other.get(message.chat.id, 0) + 1
        schedule.clear(message.chat.id)
    elif text[:16] in shifts:
        f_str = text.split('\n')
        bot.send_message(message.chat.id, text=phrases['accepted'])
        try:
            work_time = f_str[1][-14:len(f_str[1])]
            start_time, end_time = time_extraction(work_time)
            schedule2.clear(message.chat.id)
            schedule2.every().day.at(f"{start_time.time()}").do(
                get_sending_function(message.chat.id, phrases['start_work_day'])).tag(message.chat.id)
            schedule2.every().day.at(f"{end_time.time()}").do(
                get_sending_function(message.chat.id, phrases['end_work_day'])).tag(message.chat.id)
            schedule2.every().day.at(f"{(end_time + delta).time()}").do(ask_about_endday(message.chat.id)).tag(message.chat.id)
        except:
            work_time = f_str[2][-14:len(f_str[2])]
            start_time, end_time = time_extraction(work_time)
            schedule2.clear(message.chat.id)
            schedule2.every().day.at(f"{start_time.time()}").do(
                get_sending_function(message.chat.id, phrases['start_work_day'])).tag(message.chat.id)
            schedule2.every().day.at(f"{end_time.time()}").do(
                get_sending_function(message.chat.id, phrases['end_work_day'])).tag(message.chat.id)
            schedule2.every().day.at(f"{(end_time + delta).time()}").do(ask_about_endday(message.chat.id)).tag(message.chat.id)
    elif text[:5] in pauses:
        bot.send_message(message.chat.id, text=phrases['accepted'])
        start_times = []
        f_str = text.split('\n')
        for i in range(1, len(f_str)):
            try:
                pause_time = f_str[i][-14:len(f_str[i])]
                start_time, _ = time_extraction(pause_time)
                start_times.append(start_time)
                schedule1.clear(message.chat.id)
            except:
                continue
        for i in range(len(start_times)):
            schedule1.every().day.at(f"{start_times[i].time()}").do(get_sending_function(message.chat.id, phrases['pause_time'])).tag(message.chat.id)
    elif text == "🍽 Обед 30 мин":
        schedule.clear(message.chat.id)
        bot.send_message(message.chat.id, phrases['dinner_or_pause'])
        schedule.every(29).minutes.do(get_sending_function(message.chat.id, phrases['end_pause'])).tag(message.chat.id)
    elif text == "🏖 Перерыв 15 мин":
        schedule.clear(message.chat.id)
        bot.send_message(message.chat.id, phrases['dinner_or_pause'])
        schedule.every(14).minutes.do(get_sending_function(message.chat.id, phrases['end_pause'])).tag(message.chat.id)
    if not schedule.get_jobs() and not schedule1.get_jobs() and not schedule2.get_jobs() and text.lower() == "+":
        schedule2.every(1).seconds.do(get_day_statistics(message.chat.id)).tag(message.chat.id)

    now = datetime.datetime.now()
    current_time = now.strftime("%d.%m.%Y %H:%M:%S")
    print(current_time)
    print(schedule.get_jobs())
    print(schedule1.get_jobs())
    print(schedule2.get_jobs())
    print()


def get_day_statistics(chatId):
    def send_function():
        global counter_solved, counter_adjacent, counter_other
        text_message = f"Сегодня было обработано:\nРешено: {counter_solved.get(chatId, 0)} обращений\n" \
                       f"Смежники: {counter_adjacent.get(chatId, 0)} обращений\n" \
                       f"Остальные: {counter_other.get(chatId, 0)} обращений\n" \
                       f"Всего оплачиваемых: {counter_solved.get(chatId, 0) + counter_adjacent.get(chatId, 0)}"
        bot.send_message(chatId, text_message)
        counter_solved[chatId] = 0
        counter_adjacent[chatId] = 0
        counter_other[chatId] = 0
        return schedule.CancelJob

    return send_function


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


def get_sending_function(chatId, text):
    def send_function():
        bot.send_message(chatId, text)
        return schedule.CancelJob

    return send_function


def ask_about_endday(chatId):
    def send_function():
        bot.send_message(chatId, phrases['request_statistics'])
        schedule1.clear(chatId)
        schedule2.clear(chatId)
        return schedule.CancelJob
    return send_function


if __name__ == "__main__":
    scheduleThread = Thread(target=schedule_checker)
    scheduleThread.daemon = True
    scheduleThread.start()

    while True:
        try:
            bot.polling(none_stop=True)

        except Exception as e:
            now = datetime.datetime.now()
            current_time = now.strftime("%d.%m.%Y %H:%M:%S")
            print(current_time)
            print(e)
            time.sleep(15)
