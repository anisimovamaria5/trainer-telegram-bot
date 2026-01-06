from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

timetable = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="кнопка")],
        [KeyboardButton(text="Назад в меню")]],
    resize_keyboard=True
)

def get_main_menu():
    keyboards = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Расписание")],
        [KeyboardButton(text="Цены"), KeyboardButton(text="Контакты"), KeyboardButton(text="Адрес")]
    ],
    resize_keyboard=True  
    )
    return keyboards
