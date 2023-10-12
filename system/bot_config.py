import configparser

import telebot

config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
config.read("setting/config.ini")  # Чтение файла
API_TOKEN = config.get('BOT_TOKEN', 'BOT_TOKEN')  # Получение токена бота из файла конфигурации

bot = telebot.TeleBot(API_TOKEN, threaded=False)  # Создание объекта бота с использованием полученного токена
