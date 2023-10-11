from telebot import types


def create_inline_keyboard(conductors):
    """Создание InlineKeyboardMarkup для клавиатуры выбора проводника"""
    markup = types.InlineKeyboardMarkup()  # Создаем объект InlineKeyboardMarkup для клавиатуры
    buttons = []  # Создаем пустой список для хранения кнопок
    for conductor in conductors.keys():  # Перебираем элементы из словаря conductors
        # Создаем кнопку с текстом проводника и callback_data равным имени проводника
        button = types.InlineKeyboardButton(conductor, callback_data=conductor)
        buttons.append(button)  # Добавляем кнопку в список buttons
    row_width = 4  # Задаем количество кнопок в каждой строке
    # Разбиваем кнопки на строки, каждая строка содержит row_width (в данном случае, 4) кнопки
    for i in range(0, len(buttons), row_width):
        # Создаем строку кнопок, передавая ей кнопки из списка buttons с использованием среза
        markup.row(*buttons[i:i + row_width])
    return markup


def create_reply_keyboard():
    """Функция для создания ReplyKeyboardMarkup с кнопками 'Начать расчет заново' и 'Выйти в главное меню'"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Начать расчет заново")
    item2 = types.KeyboardButton("Выйти в главное меню")
    markup.add(item1, item2)
    return markup


if __name__ == '__main__':
    create_reply_keyboard()
