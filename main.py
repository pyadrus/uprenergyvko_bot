import configparser
import json
import math

import telebot
from telebot import types

from keyboards.user_keyboards import create_inline_keyboard, create_reply_keyboard

config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
config.read("setting/config.ini")  # Чтение файла
API_TOKEN = config.get('BOT_TOKEN', 'BOT_TOKEN')  # Получение токена

bot = telebot.TeleBot(API_TOKEN, threaded=False)


# Cloud Function Handler
def handler(event, context):
    body = json.loads(event['body'])
    update = telebot.types.Update.de_json(body)
    bot.process_new_updates([update])


# отправка сообщения

# Словарь с характеристиками проводников
with open('provod.json', 'r', encoding='utf-8') as file:
    conductors = json.load(file)

user_data = {}  # Словарь для хранения временных данных пользователей


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


@bot.message_handler(func=lambda message: message.text == "Начать расчет заново")
def restart_calculation(message):
    """Обработчик нажатия на кнопку "Начать расчет заново"."""
    markup = create_reply_keyboard()  # ReplyKeyboardMarkup с кнопками 'Начать расчет заново' и 'Выйти в главное меню'
    bot.send_message(message.chat.id, "Расчет начат заново. Введите параметры для расчета потерь на линии:")
    bot.send_message(message.chat.id, "Напряжение линии (кВ):", reply_markup=markup)
    bot.register_next_step_handler(message, get_voltage)


@bot.message_handler(func=lambda message: message.text == "Расчет потерь на линии")
def calculate_loss(message):
    """Обработчик нажатия на кнопку "Расчет потерь на линии"""
    markup = create_reply_keyboard()  # ReplyKeyboardMarkup с кнопками 'Начать расчет заново' и 'Выйти в главное меню'
    bot.send_message(message.chat.id, "Введите параметры для расчета потерь на линии:")
    bot.send_message(message.chat.id, "Напряжение линии (кВ):", reply_markup=markup)
    bot.register_next_step_handler(message, get_voltage)


def get_voltage(message):
    """Функция для получения напряжения линии"""
    try:
        voltage = float(message.text)
        user_data[message.chat.id] = {"voltage": voltage}
        bot.send_message(message.chat.id, "Длина линии (км):")
        bot.register_next_step_handler(message, get_length)
    except ValueError:
        if message.text == "Начать расчет заново":
            # Если пользователь нажал "Начать расчет заново", начнем расчет заново
            restart_calculation(message)
        elif message.text == "Выйти в главное меню":
            # Если пользователь нажал "Выйти в главное меню", возвращаемся в главное меню
            start(message)
        else:
            bot.send_message(message.chat.id, "Введите корректное значение напряжения (число):")
            bot.register_next_step_handler(message, get_voltage)


def get_length(message):
    """Функция для получения длины линии"""
    try:
        length = float(message.text)
        user_data[message.chat.id]["length"] = length
        bot.send_message(message.chat.id, "Мощность нагрузки (кВт):")
        bot.register_next_step_handler(message, get_load_power)
    except ValueError:
        if message.text == "Начать расчет заново":
            # Если пользователь нажал "Начать расчет заново", начнем расчет заново
            restart_calculation(message)
        elif message.text == "Выйти в главное меню":
            # Если пользователь нажал "Выйти в главное меню", возвращаемся в главное меню
            start(message)
        else:
            bot.send_message(message.chat.id, "Введите корректное значение длины линии (число):")
            bot.register_next_step_handler(message, get_length)


def get_load_power(message):
    """Функция для получения мощности нагрузки"""
    try:
        load_power = float(message.text)
        user_data[message.chat.id]["load_power"] = load_power
        bot.send_message(message.chat.id, "Введите значение косинуса фи (от 0 до 1 включительно):")
        bot.register_next_step_handler(message, get_power_factor)
    except ValueError:
        if message.text == "Начать расчет заново":
            # Если пользователь нажал "Начать расчет заново", начнем расчет заново
            restart_calculation(message)
        elif message.text == "Выйти в главное меню":
            # Если пользователь нажал "Выйти в главное меню", возвращаемся в главное меню
            start(message)
        else:
            bot.send_message(message.chat.id, "Введите корректное значение мощности нагрузки (число):")
            bot.register_next_step_handler(message, get_load_power)


def get_power_factor(message):
    """Функция для получения значения косинуса фи"""
    try:
        power_factor = float(message.text)
        if 0 <= power_factor <= 1:
            user_data[message.chat.id]["power_factor"] = power_factor
            markup = create_inline_keyboard(conductors)
            # Отправляем сообщение с клавиатурой на чат
            bot.send_message(message.chat.id, "Выберите проводник:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Значение косинуса фи должно быть от 0 до 1 включительно.")
            bot.register_next_step_handler(message, get_power_factor)
    except ValueError:
        if message.text == "Начать расчет заново":
            # Если пользователь нажал "Начать расчет заново", начнем расчет заново
            restart_calculation(message)
        elif message.text == "Выйти в главное меню":
            # Если пользователь нажал "Выйти в главное меню", возвращаемся в главное меню
            start(message)
        else:
            bot.send_message(message.chat.id, "Введите корректное значение косинуса фи (число от 0 до 1):")
            bot.register_next_step_handler(message, get_power_factor)


@bot.callback_query_handler(func=lambda call: call.data in conductors.keys())
def choose_conductor(call):
    """Обработчик выбора проводника из Inline-клавиатуры"""
    user_data[call.message.chat.id]["conductor"] = call.data
    calculate_losses(call.message.chat.id)


def calculate_losses(chat_id):
    """Функция для расчета потерь на линии и вывода результата"""
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
    result_message = ("Результат расчета потерь на линии:\n\n"
                      f"Напряжение линии:<u> {voltage:.2f} кВ</u>;\n"
                      f"Нагрузка:<u> {load_power:.2f} кВт</u>;\n"
                      f"Длина линии:<u> {length:.2f} км</u>;\n"
                      f"Косинус фи:<u> {power_factor:.2f}</u>;\n"
                      f"Проводник:<u> {conductor}</u>;\n"
                      f"Активное сопротивление проводника:<u> {resistance:.2f} оМ/км</u>;\n"
                      f"Рекативное сопротивление проводника:<u> {reactance:.2f} оМ/км</u>;\n"
                      f"Допустимый ток проводника<u> {load_tok:.2f} А</u>;\n"
                      f"Ток нагрузки<u> {load_tok1:.2f} А</u>;\n"
                      f"Потери составляют:<u> {result:.2f}%</u>\n")

    markup = create_reply_keyboard()  # ReplyKeyboardMarkup с кнопками 'Начать расчет заново' и 'Выйти в главное меню'

    bot.send_message(chat_id, result_message, reply_markup=markup, parse_mode='HTML')


bot.infinity_polling()
