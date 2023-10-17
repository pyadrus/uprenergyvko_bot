from aiogram import types
import json
from system.bot_config import dp
from aiogram.dispatcher import FSMContext

# Загрузка списка идентификаторов авторизованных пользователей из JSON-файла
with open('setting/authorized_users.json', 'r') as auth_file:
    authorized_users = json.load(auth_file)


@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext):
    """
    Обработчик команды /start и создание главного меню.
    Этот обработчик вызывается, когда пользователь отправляет команду /start.
    Он проверяет, имеет ли пользователь доступ к боту на основе его идентификатора (ID). Если пользователь
    имеет доступ, бот завершает текущее состояние машины состояний (если таковое имеется) и создает клавиатурное меню
    с опцией "Расчет потерь на линии", которое отправляется пользователю. Если у пользователя нет доступа,
    он получает уведомление о том, что у него нет доступа к этому боту.
    :param message: Объект, представляющий сообщение от пользователя.
    :param state: Объект состояния машины состояний (FSMContext), который может использоваться для управления состояниями
                  в боте (в данном случае, состояние сбрасывается).
    """
    user_id = message.from_user.id
    print(user_id)
    print("Authorized Users:", authorized_users)
    print("User ID:", user_id)
    if int(user_id) in authorized_users:
        await state.finish()  # Завершаем текущее состояние машины состояний
        await state.reset_state()  # Сбрасываем все данные машины состояний, до значения по умолчанию
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("Расчет потерь на линии")
        markup.add(item)
        await message.answer("Выберите действие:", reply_markup=markup)
    else:
        await message.answer("У вас нет доступа к этому боту.")


@dp.message_handler(lambda message: message.text == "Выйти в главное меню")
async def start_key(message: types.Message, state: FSMContext):
    """
    Обработчик нажатия на кнопку "Выйти в главное меню".
    Этот обработчик вызывается, когда пользователь отправляет сообщение "Выйти в главное меню". Он проверяет,
    имеет ли пользователь доступ к боту на основе его идентификатора (ID). Если пользователь имеет доступ, бот завершает
    текущее состояние машины состояний (если таковое имеется) и создает клавиатурное меню с опцией "Расчет потерь на
    линии", которое отправляется пользователю. Если у пользователя нет доступа, он получает уведомление о том, что у
    него нет доступа к этому боту.
    :param message: Объект, представляющий сообщение от пользователя.
    :param state: Объект состояния машины состояний (FSMContext), который может использоваться для управления
                  состояниями в боте (в данном случае, состояние сбрасывается).
    """
    user_id = message.from_user.id
    if user_id in authorized_users:
        await state.finish()  # Завершаем текущее состояние машины состояний
        await state.reset_state()  # Сбрасываем все данные машины состояний, до значения по умолчанию
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("Расчет потерь на линии")
        markup.add(item)
        await message.answer("Выберите действие:", reply_markup=markup)
    else:
        await message.answer("У вас нет доступа к этому боту.")


def register_start_handler():
    """
    Регистрация обработчика команды /start.
    Эта функция регистрирует обработчики для команды /start и нажатия кнопки "Выйти в главное меню", чтобы бот мог
    реагировать на них и выполнять соответствующие действия.
    """
    dp.register_message_handler(start)  # Регистрация обработчика для команды /start
    dp.register_message_handler(start_key)  # Регистрация обработчика для кнопки "Выйти в главное меню"
