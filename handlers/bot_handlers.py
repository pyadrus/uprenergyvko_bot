from telebot import types

from system.bot_config import bot


@bot.message_handler(commands=['start'])
def start(message):
    """Обработчик команды /start и создание главного меню"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("Расчет потерь на линии")
    markup.add(item)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Выйти в главное меню")
def start(message):
    """Обработчик нажатия на кнопку "Начать расчет заново"."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("Расчет потерь на линии")
    markup.add(item)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)


def register_start_handler():
    bot.register_message_handler(start)

