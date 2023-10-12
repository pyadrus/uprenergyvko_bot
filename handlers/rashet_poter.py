import json
import math

from handlers.bot_handlers import start
from keyboards.user_keyboards import create_inline_keyboard, create_reply_keyboard
from system.bot_config import bot

# Словарь с характеристиками проводников
with open('setting/provod.json', 'r', encoding='utf-8') as file:
    conductors = json.load(file)

user_data = {}  # Словарь для хранения временных данных пользователей


@bot.message_handler(func=lambda message: message.text == "Начать расчет заново")
def restart_calculation(message):
    """
    Обработчик нажатия на кнопку "Начать расчет заново".
    Этот обработчик вызывается, когда пользователь нажимает на кнопку "Начать расчет заново".
    Он инициирует процесс начала расчета с начальных параметров, предлагая ввести напряжение линии.
    :param message: Объект, представляющий сообщение от пользователя.
    """
    markup = create_reply_keyboard()  # ReplyKeyboardMarkup с кнопками 'Начать расчет заново' и 'Выйти в главное меню'
    bot.send_message(message.chat.id, "Расчет начат заново. Введите параметры для расчета потерь на линии:")
    bot.send_message(message.chat.id, "Напряжение линии (кВ):", reply_markup=markup)
    bot.register_next_step_handler(message, get_voltage)


@bot.message_handler(func=lambda message: message.text == "Расчет потерь на линии")
def calculate_loss(message):
    """
    Обработчик нажатия на кнопку "Расчет потерь на линии".
    Этот обработчик вызывается, когда пользователь нажимает на кнопку "Расчет потерь на линии".
    Он инициирует процесс расчета потерь на линии, начиная с ввода параметра - напряжения линии.
    :param message: Объект, представляющий сообщение от пользователя.
    """
    markup = create_reply_keyboard()  # ReplyKeyboardMarkup с кнопками 'Начать расчет заново' и 'Выйти в главное меню'
    bot.send_message(message.chat.id, "Введите параметры для расчета потерь на линии:")
    bot.send_message(message.chat.id, "Напряжение линии (кВ):", reply_markup=markup)
    bot.register_next_step_handler(message, get_voltage)


def get_voltage(message):
    """
    Функция для получения напряжения линии.
    Эта функция обрабатывает введенное пользователем напряжение линии и сохраняет его в словаре user_data.
    Затем переводит пользователя на следующий шаг - ввод длины линии.
    :param message: Объект, представляющий сообщение от пользователя.
    """
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
    """
    Функция для получения длины линии.
    Эта функция обрабатывает введенную пользователем длину линии и сохраняет ее в словаре user_data.
    Затем переводит пользователя на следующий шаг - ввод мощности нагрузки.
    :param message: Объект, представляющий сообщение от пользователя.
    """
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
    """
    Функция для получения мощности нагрузки.
    Эта функция обрабатывает введенную пользователем мощность нагрузки и сохраняет ее в словаре user_data.
    Затем переводит пользователя на следующий шаг - ввод значения косинуса фи.
    :param message: Объект, представляющий сообщение от пользователя.
    """
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
    """
    Функция для получения значения косинуса фи.
    Эта функция обрабатывает введенное пользователем значение косинуса фи и сохраняет его в словаре user_data.
    Затем предоставляет пользователю клавиатуру для выбора проводника.
    :param message: Объект, представляющий сообщение от пользователя.
    """
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
    """
    Обработчик выбора проводника из Inline-клавиатуры.
    Этот обработчик вызывается при выборе пользователем проводника из Inline-клавиатуры.
    Он сохраняет выбранный проводник в словаре user_data и перенаправляет пользователя к функции calculate_losses.
    :param call: Объект, представляющий обратный вызов (callback) от Inline-клавиатуры.
    """
    user_data[call.message.chat.id]["conductor"] = call.data
    calculate_losses(call.message.chat.id)


def calculate_losses(chat_id):
    """Функция для расчета потерь на линии и вывода результата.
    Эта функция выполняет расчет потерь на линии с использованием введенных пользователем данных и выбранного проводника.
    Затем она отправляет результат расчета пользователю.
    :param chat_id: Идентификатор чата с пользователем.
    """
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


def register_calculation_handler():
    """
    Регистрация обработчиков для расчета потерь на линии.
    Эта функция регистрирует обработчики для начала расчета заново (restart_calculation), расчета потерь
    (calculate_loss) и выбора проводника (choose_conductor). Эти обработчики обеспечивают взаимодействие с пользователем
    на разных этапах расчета.
    """
    bot.register_message_handler(restart_calculation)
    bot.register_message_handler(calculate_loss)
    bot.register_message_handler(choose_conductor)
