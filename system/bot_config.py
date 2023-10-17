import configparser
import logging

from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher

config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
config.read("setting/config.ini")  # Чтение файла
API_TOKEN = config.get('BOT_TOKEN', 'BOT_TOKEN')  # Получение токена бота из файла конфигурации

bot = Bot(token=API_TOKEN, parse_mode="HTML")  # Создание объекта бота с использованием полученного токена
storage = MemoryStorage()  # Хранилище
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)  # Логирования