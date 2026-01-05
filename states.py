from aiogram.fsm.state import StatesGroup, State

class AppointmentStates(StatesGroup):
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_name = State()