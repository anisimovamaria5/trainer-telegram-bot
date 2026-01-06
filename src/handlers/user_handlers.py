from aiogram import Router
from aiogram.filters import Command
from telebot import types
from src.keysboards import get_main_menu, timetable

router = Router()

@router.message(Command("start"))
async def process_start_command(message: types.Message):
    """Приветствие пользователя и показ главного меню"""
    
    await message.answer('Привет!\nМеня зовут ...', 
                         reply_markup=get_main_menu())

