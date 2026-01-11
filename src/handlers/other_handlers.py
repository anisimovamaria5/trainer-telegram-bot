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
from src.google_calendar import GoogleCalendarAPI 

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
async def handle_date_selection(callback: CallbackQuery, state: FSMContext):
    """Получение свободных слотов на выбранную дату"""
    
    date_str = callback.data.split('_')[1]
    selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    await state.update_data(selected_date=selected_date)

    try: 
        calendar = GoogleCalendarAPI()
        slots = await calendar.get_available_slots(selected_date)

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
async def handle_name_input(message: Message, state: FSMContext):
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

    try:
        calendar = GoogleCalendarAPI()
        created_event = await calendar.create_event(event)
        await message.answer(
            f"✅ Запись успешно создана!\n"
            f"📅 Дата: {selected_date.strftime('%d.%m.%Y')}\n"
            f"⏰ Время: {selected_time}\n"
            f"👤 Имя: {client_name}"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка при создании записи: {str(e)}")
    
    await state.clear()

@router.message(F.text == "auth")
async def simple_auth(message: Message):
    """Авторизация в Google Calendar (автоматическая при первом запуске)"""
    try:
        # Создаем экземпляр - авторизация произойдет автоматически
        calendar = GoogleCalendarAPI()
        
        if calendar.token:
            await message.answer(
                "✅ Авторизация в Google Calendar успешна!\n\n"
                "Теперь можете использовать команду 'Расписание'."
            )
        else:
            await message.answer(
                "⚠️ Авторизация не удалась. Убедитесь, что файл credentials.json "
                "находится в корневой папке проекта."
            )
    except Exception as e:
        await message.answer(f"❌ Ошибка авторизации: {str(e)}")

@router.message(F.text.regexp(r'^[a-zA-Z0-9]{15,50}$'))
async def handle_short_code(message: Message):
    """Обработка кодов (оставлено для совместимости)"""
    code = message.text.strip()
    
    if code.lower() in ["расписание", "цены", "контакты", "адрес", "назад в меню", "auth"]:
        return
    
    await message.answer(
        "ℹ️ Для Google Calendar авторизация происходит автоматически "
        "при первом запуске через браузер."
    )

@router.message(F.text == "debug_calendar")
async def debug_calendar(message: Message):
    """Полная отладка календаря"""
    try:
        await message.answer("🔍 Начинаю диагностику Google Calendar...")
        
        calendar = GoogleCalendarAPI()
    
        if not calendar.token:
            await message.answer("❌ Нет токена авторизации")
            return
            
        await message.answer(f"✅ Токен получен")
        
        today = datetime.now().date()
        await message.answer(f"📅 Получаю события на {today.strftime('%d.%m.%Y')}...")
        
        events = await calendar.get_busy_periods(datetime.now())
        await message.answer(f"✅ Событий найдено: {len(events)}")
        
        if events:
            first_event = events[0]
            summary = first_event.get('summary', 'Без названия')
            start_time = first_event.get('start', {}).get('dateTime', 'Нет времени')
            await message.answer(f"📝 Пример события:\nНазвание: {summary}\nВремя: {start_time}")
        
        await message.answer("🔄 Получаю свободные слоты...")
        slots = await calendar.get_available_slots(today)
        await message.answer(f"✅ Свободных слотов найдено: {len(slots)}")
        
        if slots:
            for start, end in slots[:5]:
                await message.answer(f"• {start.strftime('%H:%M')} - {end.strftime('%H:%M')}")
                
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        await message.answer(f"❌ Ошибка диагностики:\n{str(e)}")
        print(f"FULL ERROR:\n{error_trace}")
