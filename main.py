import telebot
from telebot import types
import time
import schedule
from threading import Thread

bot = telebot.TeleBot('TOKEN')


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("💻 Новое обращение")
    btn2 = types.KeyboardButton("🍽 Обед")
    btn3 = types.KeyboardButton("🏖 Перерыв 15 мин")
    btn4 = types.KeyboardButton("✅ Обращение завершено")
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, text="Привет, {0.first_name}! Я бот для твоей работы. Нажми на соотвутствующую кнопку и я начну отсчет времени".format(message.from_user), reply_markup=markup)


def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(1)


@bot.message_handler(func=lambda message: True)
def fio(message):
    text = message.text
    if text == "💻 Новое обращение":
        bot.send_message(message.chat.id, text="Начинаю обратный отсчет! Когда время будет на исходе ты получишь уведомление. Не затягивай!")
    if text == "✅ Обращение завершено" and len(schedule.get_jobs(message.chat.id)) >= 1:
        schedule.clear(message.chat.id)
        bot.send_message(message.chat.id, "Обращение завершено! Ты справилась! Если получишь новое сообщение - просто тыкни на соответствующую кнопку")
    elif text == "✅ Обращение завершено" and len(schedule.get_jobs(message.chat.id)) == 0:
        schedule.clear(message.chat.id)
    else:
        schedule.every(25).minutes.do(get_sending_function(message.chat.id)).tag(message.chat.id)
        schedule.every(29).seconds.do(get_sending_notification(message.chat.id)).tag(message.chat.id)
    if text == "🍽 Обед" and len(schedule.get_jobs(message.chat.id)) >= 1:
        schedule.clear(message.chat.id)
        bot.send_message(message.chat.id, "Оу, у тебя обед? Приятного аппетита! Я обязательно тебе напомню, что пора за работу")
        schedule.every(29).minutes.do(get_sending_dinner(message.chat.id)).tag(message.chat.id)
    if text == "🏖 Перерыв 15 мин" and len(schedule.get_jobs(message.chat.id)) >= 1:
        schedule.clear(message.chat.id)
        bot.send_message(message.chat.id, "Работа работой, а отдых по расписанию! Я обязательно тебе напомню, что пора за работу")
        schedule.every(14).minutes.do(get_sending_dinner(message.chat.id)).tag(message.chat.id)


def get_sending_function(chatId):
    def send_function():
        bot.send_message(chatId, "Осталось всего 5 минут! Поторопись, скоро обращение слетит!")
        return schedule.CancelJob
    return send_function


def get_sending_notification(chatId):
    def send_function():
        bot.send_message(chatId, "Осталось всего 1 минута! Поторопись, скоро обращение слетит!")
        return schedule.CancelJob
    return send_function


def get_sending_dinner(chatId):
    def send_function():
        bot.send_message(chatId, "Осталось всего 1 минута! Приготовься к работе!")
        return schedule.CancelJob
    return send_function


if __name__ == "__main__":
    scheduleThread = Thread(target=schedule_checker)
    scheduleThread.daemon = True
    scheduleThread.start()
    bot.polling()

