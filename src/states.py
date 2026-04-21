"""
FSM States for Somly AI Bot.
"""

from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_contact = State()

class ExportStates(StatesGroup):
    waiting_for_custom_date = State()
