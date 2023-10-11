import telebot
from telebot import types
import json
import math
import random
import configparser


config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
config.read("setting/config.ini")  # Чтение файла
bot_token = config.get('BOT_TOKEN', 'BOT_TOKEN')  # Получение токена

bot = telebot.TeleBot(bot_token, threaded=False)


# Cloud Function Handler
def handler(event, context):
    body = json.loads(event['body'])
    update = telebot.types.Update.de_json(body)
    bot.process_new_updates([update])


# отправка сообщения

# Словарь с характеристиками проводников
with open('provod.json', 'r', encoding='utf-8') as file:
    conductors = json.load(file)

# Словарь для хранения временных данных пользователей
user_data = {}


@bot.message_handler(commands=['start'])
def start(message):
    """Обработчик команды /start и создание главного меню"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("Расчет потерь на линии")
    markup.add(item)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Расчет потерь на линии")
def calculate_loss(message):
    """Обработчик нажатия на кнопку "Расчет потерь на линии"""
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Введите параметры для расчета потерь на линии:")
    bot.send_message(message.chat.id, "Напряжение линии (кВ):", reply_markup=markup)
    bot.register_next_step_handler(message, get_voltage)


# Функция для получения напряжения линии
def get_voltage(message):
    try:
        voltage = float(message.text)
        user_data[message.chat.id] = {"voltage": voltage}
        bot.send_message(message.chat.id, "Длина линии (км):")
        bot.register_next_step_handler(message, get_length)
    except ValueError:
        bot.send_message(message.chat.id, "Введите корректное значение напряжения (число):")
        bot.register_next_step_handler(message, get_voltage)


# Функция для получения длины линии
def get_length(message):
    try:
        length = float(message.text)
        user_data[message.chat.id]["length"] = length
        bot.send_message(message.chat.id, "Мощность нагрузки (кВт):")
        bot.register_next_step_handler(message, get_load_power)
    except ValueError:
        bot.send_message(message.chat.id, "Введите корректное значение длины линии (число):")
        bot.register_next_step_handler(message, get_length)


# Функция для получения мощности нагрузки
def get_load_power(message):
    try:
        load_power = float(message.text)
        user_data[message.chat.id]["load_power"] = load_power
        bot.send_message(message.chat.id, "Введите значение косинуса фи (от 0 до 1 включительно):")
        bot.register_next_step_handler(message, get_power_factor)
    except ValueError:
        bot.send_message(message.chat.id, "Введите корректное значение мощности нагрузки (число):")
        bot.register_next_step_handler(message, get_load_power)


# Функция для получения значения косинуса фи
def get_power_factor(message):
    try:
        power_factor = float(message.text)
        if 0 <= power_factor <= 1:
            user_data[message.chat.id]["power_factor"] = power_factor
            markup = types.InlineKeyboardMarkup()
            for conductor in conductors.keys():
                button = types.InlineKeyboardButton(conductor, callback_data=conductor)
                markup.add(button)
            bot.send_message(message.chat.id, "Выберите проводник:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Значение косинуса фи должно быть от 0 до 1 включительно.")
            bot.register_next_step_handler(message, get_power_factor)
    except ValueError:
        bot.send_message(message.chat.id, "Введите корректное значение косинуса фи (число от 0 до 1):")
        bot.register_next_step_handler(message, get_power_factor)


# Обработчик выбора проводника из инлайн-клавиатуры
@bot.callback_query_handler(func=lambda call: call.data in conductors.keys())
def choose_conductor(call):
    user_data[call.message.chat.id]["conductor"] = call.data
    calculate_losses(call.message.chat.id)


# Функция для расчета потерь на линии и вывода результата
def calculate_losses(chat_id):
    data = user_data[chat_id]
    voltage = data["voltage"]
    length = data["length"]
    load_power = data["load_power"]
    conductor = data["conductor"]
    power_factor = data["power_factor"]

    resistance, reactance, load_tok = conductors[conductor]

    # Расчет потерь на линии

    result = (10 ** 8) * (
                resistance * power_factor + reactance * math.sin(math.acos(power_factor)) * load_power * length) / (
                         ((voltage * 1000) ** 2) * power_factor)
    load_tok1 = (load_power) / (voltage * power_factor * math.sqrt(3))
    result_message = f"Результат расчета потерь на линии:\n"
    result_message += f"Напряжение линии: {voltage:.2f} кВ; \n"
    result_message += f"Нагрузка: {load_power:.2f} кВт; \n"
    result_message += f"Длина линии: {length:.2f} км; \n"
    result_message += f"Косинус фи: {power_factor:.2f}; \n"
    result_message += f"Проводник: {conductor}:\n"
    result_message += f"Активное сопротивление проводника: {resistance:.2f} оМ/км; \n"
    result_message += f"Рекативное сопротивление проводника: {reactance:.2f} оМ/км; \n"
    result_message += f"Допустимый ток проводника {load_tok:.2f} А; \n"
    result_message += f"Ток нагрузки {load_tok1:.2f} А; \n"
    result_message += f"Потери состовляют: {result:.2f}%\n"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Начать расчет заново")
    item2 = types.KeyboardButton("Выити в главное меню")
    markup.add(item1, item2)

    bot.send_message(chat_id, result_message, reply_markup=markup)


# Обработчик кнопок "Начать расчет заново" и "Выити в главное меню"
@bot.message_handler(func=lambda message: message.text in ["Начать расчет заново", "Выити в главное меню"])
def handle_buttons(message):
    if message.text == "Начать расчет заново":
        bot.send_message(message.chat.id, "Расчет потерь на линии")
        calculate_loss(message)
    elif message.text == "Выити в главное меню":
        start(message)
