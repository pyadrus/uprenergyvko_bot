from aiogram import executor

from handlers.bot_handlers import register_start_handler
from handlers.rashet_poter import register_calculation_handler
from system.bot_config import dp


def start_bot():
    """
    Запуск бота и регистрация обработчиков сообщений.
    Эта функция запускает вашего телеграм-бота, а также регистрирует обработчики сообщений для взаимодействия с
    пользователями.
    """
    executor.start_polling(dp, skip_updates=True)
    register_start_handler()  # Регистрация обработчиков для старта бота
    register_calculation_handler()  # Регистрация обработчиков для расчета потерь на линии


if __name__ == '__main__':
    start_bot()  # Запуск бота при выполнении этого скрипта
