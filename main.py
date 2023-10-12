from handlers.bot_handlers import register_start_handler
from handlers.rashet_poter import register_calculation_handler
from system.bot_config import bot


def start_bot():
    bot.infinity_polling(none_stop=True)
    register_start_handler()
    register_calculation_handler()


if __name__ == '__main__':
    start_bot()
