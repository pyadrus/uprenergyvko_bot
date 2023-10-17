import json
import math

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from handlers.bot_handlers import start_key
from keyboards.user_keyboards import create_inline_keyboard, create_reply_keyboard
from system.bot_config import dp, bot

# Словарь с характеристиками проводников
with open('setting/provod.json', 'r', encoding='utf-8') as file:
    conductors = json.load(file)

# Загрузка списка идентификаторов авторизованных пользователей из JSON-файла
with open('setting/authorized_users.json', 'r') as auth_file:
    authorized_users = json.load(auth_file)


class MyStates(StatesGroup):
    GET_VOLTAGE = State()
    GET_LENGTH = State()
    GET_LOAD_POWER = State()
    GET_POWER_FACTOR = State()


@dp.message_handler(lambda message: message.text == "Начать расчет заново")
async def restart_calculation(message: types.Message, state: FSMContext):
    """
    Обработчик нажатия на кнопку "Начать расчет заново".
    Этот обработчик вызывается, когда пользователь отправляет сообщение "Начать расчет заново". Он проверяет,
    имеет ли пользователь доступ к боту на основе его идентификатора (ID). Если пользователь имеет доступ, бот завершает
    текущее состояние машины состояний (если таковое имеется) и сбрасывает все данные машины состояний до значений
    по умолчанию. Затем он создает клавиатурное меню с кнопками "Начать расчет заново" и "Выйти в главное меню" и
    отправляет сообщения с инструкциями для пользователя. Наконец, устанавливает состояние машины состояний на GET_VOLTAGE,
    чтобы начать новый расчет потерь на линии.
    :param message: Объект, представляющий сообщение от пользователя.
    :param state: Объект состояния машины состояний (FSMContext), который может использоваться для управления состояниями
                  в боте (в данном случае, состояние сбрасывается).
    """
    user_id = message.from_user.id
    # Проверка доступа пользователя
    if user_id in authorized_users:
        await state.finish()  # Завершаем текущее состояние машины состояний
        await state.reset_state()  # Сбрасываем все данные машины состояний, до значения по умолчанию
        markup = create_reply_keyboard()  # ReplyKeyboardMarkup с кнопками 'Начать расчет заново' и 'Выйти в главное меню'
        await bot.send_message(message.chat.id, "Расчет начат заново. Введите параметры для расчета потерь на линии:")
        await bot.send_message(message.chat.id, "Напряжение линии (кВ):", reply_markup=markup)
        # Устанавливаем состояние машины состояний на GET_VOLTAGE
        await MyStates.GET_VOLTAGE.set()
    else:
        await message.answer("У вас нет доступа к этому боту.")


@dp.message_handler(lambda message: message.text == "Расчет потерь на линии")
async def calculate_loss(message: types.Message):
    """
    Обработчик нажатия на кнопку "Расчет потерь на линии".
    Этот обработчик вызывается, когда пользователь отправляет сообщение "Расчет потерь на линии". Он проверяет,
    имеет ли пользователь доступ к боту на основе его идентификатора (ID). Если пользователь имеет доступ, бот создает
    клавиатурное меню с кнопками "Начать расчет заново" и "Выйти в главное меню" и отправляет сообщения с инструкциями
    для пользователя. Затем бот устанавливает состояние машины состояний на GET_VOLTAGE, чтобы начать процесс
    ввода параметров для расчета потерь на линии.
    :param message: Объект, представляющий сообщение от пользователя.
    """
    user_id = message.from_user.id
    # Проверка доступа пользователя
    if user_id in authorized_users:
        markup = create_reply_keyboard()  # ReplyKeyboardMarkup с кнопками 'Начать расчет заново' и 'Выйти в главное меню'
        await bot.send_message(message.chat.id, "Введите параметры для расчета потерь на линии:")
        await bot.send_message(message.chat.id, "Напряжение линии (кВ):", reply_markup=markup)
        # Устанавливаем состояние машины состояний на GET_VOLTAGE
        await MyStates.GET_VOLTAGE.set()
    else:
        await message.answer("У вас нет доступа к этому боту.")


@dp.message_handler(state=MyStates.GET_VOLTAGE)
async def get_voltage(message: types.Message, state: FSMContext):
    """
    Обработчик для получения значения напряжения линии.
    Эта функция ожидает получить значение напряжения линии от пользователя. Если пользователь введет корректное число,
    она сохранит это значение в данных состояния машины состояний и перейдет к запросу длины линии (состояние GET_LENGTH).
    :param message: Объект, представляющий сообщение от пользователя.
    :param state: Объект состояния машины состояний (FSMContext), который используется для управления состояниями в боте.
    """
    try:
        voltage = float(message.text)
        await state.update_data(voltage=voltage)
        await bot.send_message(message.chat.id, "Длина линии (км):")
        await MyStates.GET_LENGTH.set()
    except ValueError:
        if message.text == "Начать расчет заново":
            # Если пользователь нажал "Начать расчет заново", начнем расчет заново
            await restart_calculation(message, state)
        elif message.text == "Выйти в главное меню":
            # Если пользователь нажал "Выйти в главное меню", возвращаемся в главное меню
            await start_key(message, state)
        else:
            await bot.send_message(message.chat.id, "Введите корректное значение (число):")


@dp.message_handler(state=MyStates.GET_LENGTH)
async def get_length(message: types.Message, state: FSMContext):
    """
    Обработчик для получения значения длины линии.
    Эта функция ожидает получить значение длины линии от пользователя. Если пользователь введет корректное число,
    она сохранит это значение в данных состояния машины состояний и перейдет к запросу мощности нагрузки (состояние GET_LOAD_POWER).
    :param message: Объект, представляющий сообщение от пользователя.
    :param state: Объект состояния машины состояний (FSMContext), который используется для управления состояниями в боте.
    """
    try:
        length = float(message.text)
        await state.update_data(length=length)
        await bot.send_message(message.chat.id, "Мощность нагрузки (кВт):")
        await MyStates.GET_LOAD_POWER.set()
    except ValueError:
        if message.text == "Начать расчет заново":
            await restart_calculation(message, state)
        elif message.text == "Выйти в главное меню":
            # Если пользователь нажал "Выйти в главное меню", возвращаемся в главное меню
            await start_key(message, state)
        else:
            await bot.send_message(message.chat.id, "Введите корректное значение (число):")


@dp.message_handler(state=MyStates.GET_LOAD_POWER)
async def get_load_power(message: types.Message, state: FSMContext):
    """
    Обработчик для получения значения мощности нагрузки.
    Эта функция ожидает получить значение мощности нагрузки от пользователя. Если пользователь введет корректное число,
    она сохранит это значение в данных состояния машины состояний и перейдет к запросу косинуса фи (состояние GET_POWER_FACTOR).
    :param message: Объект, представляющий сообщение от пользователя.
    :param state: Объект состояния машины состояний (FSMContext), который используется для управления состояниями в боте.
    """
    try:
        load_power = float(message.text)
        await state.update_data(load_power=load_power)
        await bot.send_message(message.chat.id, "Введите значение косинуса фи (от 0 до 1 включительно):")
        await MyStates.GET_POWER_FACTOR.set()  # Set the next state
    except ValueError:
        if message.text == "Начать расчет заново":
            await restart_calculation(message, state)
        elif message.text == "Выйти в главное меню":
            # Если пользователь нажал "Выйти в главное меню", возвращаемся в главное меню
            await start_key(message, state)
        else:
            await bot.send_message(message.chat.id, "Введите корректное значение (число):")


@dp.message_handler(state=MyStates.GET_POWER_FACTOR)
async def get_power_factor(message: types.Message, state: FSMContext):
    """
    Обработчик для получения значения косинуса фи.
    Эта функция ожидает получить значение косинуса фи от пользователя. Если пользователь введет корректное число в
    диапазоне от 0 до 1 включительно, она сохранит это значение в данных состояния машины состояний и предоставит
    пользователю клавиатуру с вариантами проводников (create_inline_keyboard(conductors)) для выбора.
    :param message: Объект, представляющий сообщение от пользователя.
    :param state: Объект состояния машины состояний (FSMContext), который используется для управления состояниями в боте.
    """
    try:
        power_factor = float(message.text)
        if 0 <= power_factor <= 1:
            await state.update_data(power_factor=power_factor)
            markup = create_inline_keyboard(conductors)
            # Отправляем сообщение с клавиатурой на чат
            await bot.send_message(message.chat.id, "Выберите проводник:", reply_markup=markup)
        else:
            await bot.send_message(message.chat.id, "Значение косинуса фи должно быть от 0 до 1 включительно.")
            await MyStates.GET_POWER_FACTOR.set()
    except ValueError:
        if message.text == "Начать расчет заново":
            await restart_calculation(message, state)
        elif message.text == "Выйти в главное меню":
            # Если пользователь нажал "Выйти в главное меню", возвращаемся в главное меню
            await start_key(message, state)
        else:
            await bot.send_message(message.chat.id, "Введите корректное значение косинуса фи (число от 0 до 1):")


@dp.callback_query_handler(lambda call: call.data in conductors.keys(), state=MyStates.GET_POWER_FACTOR)
async def choose_conductor(call, state: FSMContext):
    """
    Обработчик для выбора проводника из вариантов.
    Эта функция вызывается, когда пользователь выбирает проводник из предоставленных вариантов (представленных в
    словаре conductors). Она обновляет данные пользователя, добавляя выбранный проводник в данные, а затем переходит
    к расчету потерь.
    :param call: Объект, представляющий callback-запрос от пользователя.
    :param state: Объект состояния машины состояний (FSMContext), который используется для управления состояниями в боте.
    """
    user_data = await state.get_data()
    user_data["conductor"] = call.data  # Обновите «проводник» в данных пользователя.
    await state.update_data(**user_data)
    # На этом этапе состояние «проводника» обновляется, и можно приступать к расчету.
    await calculate_losses(call.message, state)


async def calculate_losses(message: types.Message, state: FSMContext):
    """
    Функция для расчета потерь на линии и отправки результата пользователю.
    Эта функция принимает данные из состояния машины состояний и выполняет расчет потерь на линии. Затем она отправляет
    результат расчета пользователю в виде сообщения.
    :param message: Объект, представляющий сообщение от пользователя.
    :param state: Объект состояния машины состояний (FSMContext), который содержит данные для расчета потерь.
    """
    data = await state.get_data()
    voltage = data["voltage"]
    length = data["length"]
    load_power = data["load_power"]
    conductor = data.get("conductor")
    power_factor = data["power_factor"]
    resistance, reactance, load_tok = conductors[conductor]
    # Расчет потерь на линии
    result = load_power * (
                power_factor * resistance + reactance * ((1 - power_factor ** 2) ** 0.5)) * reactance * length / (
                         10 * voltage ** 2)
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
    await bot.send_message(message.chat.id, result_message, reply_markup=markup, parse_mode='HTML')


def register_calculation_handler():
    """Регистрация обработчиков"""
    dp.register_message_handler(calculate_loss)
    dp.register_message_handler(choose_conductor)
