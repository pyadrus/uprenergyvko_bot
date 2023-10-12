from telebot import types

from system.bot_config import bot


@bot.message_handler(commands=['start'])
def start(message):
    """
    Обработчик команды /start и создание главного меню.
    Этот обработчик вызывается, когда пользователь отправляет команду /start.
    Он создает клавиатурное меню с опцией "Расчет потерь на линии" и отправляет его пользователю.
    :param message: Объект, представляющий сообщение от пользователя.
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("Расчет потерь на линии")
    markup.add(item)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Выйти в главное меню")
def start(message):
    """
    Обработчик нажатия на кнопку "Выйти в главное меню".
    Этот обработчик вызывается, когда пользователь нажимает кнопку "Выйти в главное меню".
    Он также создает клавиатурное меню с опцией "Расчет потерь на линии" и отправляет его пользователю.
    :param message: Объект, представляющий сообщение от пользователя.
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("Расчет потерь на линии")
    markup.add(item)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)


def register_start_handler():
    """
    Регистрация обработчика команды /start.
    Эта функция регистрирует обработчик команды /start, чтобы бот мог реагировать на нее.
    """
    bot.register_message_handler(start)
