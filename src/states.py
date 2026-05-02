"""
FSM States for Somly AI Bot.
"""

from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_location = State()
    waiting_for_region = State()
    waiting_for_country = State()
    waiting_for_contact = State()

class ExportStates(StatesGroup):
    waiting_for_custom_date = State()

class TransactionAmbiguity(StatesGroup):
    waiting_for_amount = State()
    waiting_for_type = State()
    waiting_for_debt_date = State()
    editing_anomaly_amount = State()
    confirm_large_amount = State()
    confirm_past_due_date = State()
    waiting_for_person_name = State()
