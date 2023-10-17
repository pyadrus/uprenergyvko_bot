import json
import math

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from keyboards.user_keyboards import create_inline_keyboard, create_reply_keyboard
from system.bot_config import dp, bot

# Словарь с характеристиками проводников
with open('setting/provod.json', 'r', encoding='utf-8') as file:
    conductors = json.load(file)


class MyStates(StatesGroup):
    GET_VOLTAGE = State()
    GET_LENGTH = State()
    GET_LOAD_POWER = State()
    GET_POWER_FACTOR = State()


@dp.message_handler(lambda message: message.text == "Начать расчет заново")
async def restart_calculation(message: types.Message):
    """Обработчик нажатия на кнопку "Начать расчет заново"."""
    markup = create_reply_keyboard()  # ReplyKeyboardMarkup с кнопками 'Начать расчет заново' и 'Выйти в главное меню'
    await bot.send_message(message.chat.id, "Расчет начат заново. Введите параметры для расчета потерь на линии:")
    await bot.send_message(message.chat.id, "Напряжение линии (кВ):", reply_markup=markup)
    await MyStates.GET_VOLTAGE.set()


@dp.message_handler(lambda message: message.text == "Расчет потерь на линии")
async def calculate_loss(message: types.Message):
    markup = create_reply_keyboard()  # ReplyKeyboardMarkup с кнопками 'Начать расчет заново' и 'Выйти в главное меню'
    await bot.send_message(message.chat.id, "Введите параметры для расчета потерь на линии:")
    await bot.send_message(message.chat.id, "Напряжение линии (кВ):", reply_markup=markup)
    await MyStates.GET_VOLTAGE.set()


@dp.message_handler(state=MyStates.GET_VOLTAGE)
async def get_voltage(message: types.Message, state: FSMContext):
    """Функция для получения напряжения линии."""
    try:
        voltage = float(message.text)
        await state.update_data(voltage=voltage)
        await bot.send_message(message.chat.id, "Длина линии (км):")
        await MyStates.GET_LENGTH.set()
    except ValueError:
        if message.text == "Начать расчет заново":
            # Если пользователь нажал "Начать расчет заново", начнем расчет заново
            await restart_calculation(message)
        # elif message.text == "Выйти в главное меню":
        #     # Если пользователь нажал "Выйти в главное меню", возвращаемся в главное меню
        #     await start(message)
        else:
            await bot.send_message(message.chat.id, "Введите корректное значение напряжения (число):")


@dp.message_handler(state=MyStates.GET_LENGTH)
async def get_length(message: types.Message, state: FSMContext):
    """Функция для получения длины линии."""
    length = float(message.text)
    await state.update_data(length=length)
    await bot.send_message(message.chat.id, "Мощность нагрузки (кВт):")
    await MyStates.GET_LOAD_POWER.set()


@dp.message_handler(state=MyStates.GET_LOAD_POWER)
async def get_load_power(message: types.Message, state: FSMContext):
    load_power = float(message.text)
    await state.update_data(load_power=load_power)
    await bot.send_message(message.chat.id, "Введите значение косинуса фи (от 0 до 1 включительно):")
    await MyStates.GET_POWER_FACTOR.set()  # Set the next state


@dp.message_handler(state=MyStates.GET_POWER_FACTOR)
async def get_power_factor(message: types.Message, state: FSMContext):
    """Функция для получения значения косинуса фи."""
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
        await bot.send_message(message.chat.id, "Введите корректное значение косинуса фи (число от 0 до 1):")
        await bot.get_send_progress_handler(message.chat.id)(MyStates.GET_POWER_FACTOR)


@dp.callback_query_handler(lambda call: call.data in conductors.keys(), state=MyStates.GET_POWER_FACTOR)
async def choose_conductor(call, state: FSMContext):
    user_data = await state.get_data()
    user_data["conductor"] = call.data  # Update the 'conductor' in the user data
    await state.update_data(**user_data)
    # At this point, 'conductor' is updated in the state, and you can proceed with the calculation.
    await calculate_losses(call.message, state)


async def calculate_losses(message: types.Message, state: FSMContext):
    data = await state.get_data()
    voltage = data["voltage"]
    length = data["length"]
    load_power = data["load_power"]
    conductor = data.get("conductor")
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
    await bot.send_message(message.chat.id, result_message, reply_markup=markup, parse_mode='HTML')


def register_calculation_handler():
    """Регистрация обработчиков"""
    dp.register_message_handler(calculate_loss)
    dp.register_message_handler(choose_conductor)
