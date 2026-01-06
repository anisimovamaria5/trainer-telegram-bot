from datetime import datetime, timedelta, time
import json
import os
from aiogram import Bot, Router, F
from setuptools import Command
from telebot import types
from aiogram.types import CallbackQuery
from src.keysboards import get_main_menu
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.states import AppointmentStates
from src.yandex_calendar import YandexCalendarAPI


router = Router()


@router.message(F.text == "Цены")
async def send_prices(message: Message):
    """Отправка информации о ценах"""

    await message.answer('Индивидуальная тренировка - 2000 руб.')


@router.message(F.text == "Контакты")
async def send_contact(message: Message):
    """Отправка контактного телефона"""

    await message.answer('+7922**')


@router.message(F.text == "Адрес")
async def send_address(message: Message):
    """Отправка адреса в виде ссылки на 2GIS"""

    await message.answer('https://go.2gis.com/YDhYM')


@router.message(F.text == "Назад в меню")
async def back_in_menu(message: Message):
    """Возврат в главное меню"""

    await message.answer('Возвращаемся в меню', 
                         reply_markup=get_main_menu())


@router.message(F.text == "Расписание")
async def handle_schedule(message: Message, state: FSMContext):
    """Получение расписания из календаря для записи"""

    builder = InlineKeyboardBuilder()
    today = datetime.now().date()

    for i in range(8):
        date = today + timedelta(i)
        builder.add(InlineKeyboardButton(
            text=date.strftime('%d.%m.%Y'),
            callback_data=f'date_{date}'
        ))
    builder.adjust(3)
    await message.answer('Выберете подходящий день', 
                         reply_markup=builder.as_markup())
    await state.set_state(AppointmentStates.waiting_for_date)


@router.callback_query(F.data.startswith("date_"), AppointmentStates.waiting_for_date)
async def handle_date_selection(callback: CallbackQuery, state: FSMContext, yandex_calendar: YandexCalendarAPI):
    """Получение свободных слотов на выбранную дату"""
    
    date_str = callback.data.split('_')[1]
    selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    await state.update_data(selected_date=selected_date)

    try: 
        slots = await yandex_calendar.get_available_slots(selected_date)

        if not slots:
            await callback.message.edit_text('"Нет свободных слотов на эту дату. Выберите другую дату')

        builder = InlineKeyboardBuilder()
        for start, end in slots:
            builder.add(InlineKeyboardButton(
                text=f'{start.strftime("%H:%M")} - {end.strftime("%H:%M")}',
                callback_data=f'time_{start.strftime("%H:%M")}'
            ))   
        builder.adjust(2)
        await callback.message.edit_text(f'Свободные слоты на {selected_date.strftime("%d.%m.%Y")}:',
                                         reply_markup=builder.as_markup()) 
        await state.set_state(AppointmentStates.waiting_for_time)
    except Exception as e:
        await callback.message.answer('Ошибка при получении расписания')


@router.callback_query(F.data.startswith("time_"), AppointmentStates.waiting_for_time)
async def handle_time_selection(callback: CallbackQuery, state:FSMContext):
    """Сохранение выбранного времени и запрос имени"""
    
    time_str = callback.data.split('_')[1]
    user_data = await state.get_data()
    selected_date = user_data['selected_date']
    
    await state.update_data(selected_time=time_str)
    await callback.message.answer('Введите ваше имя для записи:')
    await state.set_state(AppointmentStates.waiting_for_name)

@router.message(AppointmentStates.waiting_for_name)
async def handle_name_input(message: Message, state: FSMContext, bot: Bot, yandex_calendar: YandexCalendarAPI):
    """Создание события в календаре и завершение записи"""
    
    user_data = await state.get_data()
    selected_date = user_data['selected_date']
    selected_time = user_data['selected_time']
    client_name = message.text

    event_datetime = datetime.combine(
        selected_date,
        datetime.strptime(selected_time, '%H:%M').time()
    )
    event = {
        'summary': f'Запись {client_name}',
        'start': {
            'dateTime': event_datetime.isoformat(),
            "timeZone": "Asia/Yekaterinburg"
        },
        'end': {
            'dateTime': (event_datetime + timedelta(hours=1)).isoformat(),
            "timeZone": "Asia/Yekaterinburg"
        }
    }

    created_event = await yandex_calendar.create_event(event)
    await message.answer(
            f"✅ Запись успешно создана!\n"
            f"📅 Дата: {selected_date.strftime('%d.%m.%Y')}\n"
            f"⏰ Время: {selected_time}\n"
            f"👤 Имя: {client_name}"
    )
    await state.clear()

@router.message(F.text == "auth")
async def simple_auth(message: Message, yandex_calendar: YandexCalendarAPI):
    """Начало процесса авторизации через Яндекс OAuth"""

    if yandex_calendar.token:
        try:
            today = datetime.now().date()
            events = await yandex_calendar.get_busy_periods(today)
            await message.answer(
                f"✅ Токен уже активен!\n"
                f"Событий сегодня: {len(events)}\n"
                f"Можешь использовать 'Расписание'"
            )
            return
        except:
            pass
    
    auth_url = await yandex_calendar.get_auth_url()
    
    await message.answer(
        "🔐 Для авторизации:\n\n"
        "1. Перейди по ссылке:\n"
        f"<code>{auth_url}</code>\n\n"
        "2. Разреши доступ к календарю\n"
        "3. Скопируй код из адресной строки\n"
        "4. Отправь его мне\n\n"
    )

@router.message(F.text.regexp(r'^[a-zA-Z0-9]{15,50}$'))
async def handle_short_code(message: Message, yandex_calendar: YandexCalendarAPI):
    """Обмен кода авторизации на токен доступа"""
    
    code = message.text.strip()
    
    if code.lower() in ["расписание", "цены", "контакты", "адрес", "назад в меню", "auth"]:
        return
    
    await message.answer("🔄 Получаю токен...")
    
    success = await yandex_calendar.get_token(code)
    if success:
        await message.answer(
            "✅ Токен получен и сохранен!\n\n"
        )
    else:
        await message.answer("❌ Не удалось получить токен. Попробуй еще раз.")
