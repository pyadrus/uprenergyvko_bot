from handlers.bot_handlers import register_start_handler
from handlers.rashet_poter import register_calculation_handler
from system.bot_config import bot


def start_bot():
    """
    Запуск бота и регистрация обработчиков сообщений.
    Эта функция запускает вашего телеграм-бота, а также регистрирует обработчики сообщений для взаимодействия с
    пользователями.
    """
    bot.infinity_polling(none_stop=True)  # Запуск бота с бесконечным опросом сообщений (non-stop)
    register_start_handler()  # Регистрация обработчиков для старта бота
    register_calculation_handler()  # Регистрация обработчиков для расчета потерь на линии


if __name__ == '__main__':
    start_bot()  # Запуск бота при выполнении этого скрипта
