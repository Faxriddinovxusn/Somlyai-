"""
Limit handler — oylik limit o'rnatish.

/setlimit — set monthly spending limit for a currency
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.database import (
    get_user_all_balances,
    update_balance_limit,
)

router = Router()

def format_number(num: float) -> str:
    if num < 0:
        return "-" + f"{int(abs(num)):,}".replace(",", " ")
    return f"{int(num):,}".replace(",", " ")

class SetLimitState(StatesGroup):
    waiting_amount = State()

# ═══════════════════════════════════════
# /setlimit — Oylik limit o'rnatish
# ═══════════════════════════════════════

@router.message(Command("setlimit"))
async def setlimit_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    balances = await get_user_all_balances(user_id)

    if not balances:
        await message.answer("Sizda hali balans yo'q.")
        return

    # Show available currencies
    keyboard_rows = []
    for currency, info in balances.items():
        title = info.get("title", currency)
        current_limit = info.get("limit")
        label = f"{title} ({currency})"
        if current_limit:
            label += f" — hozirgi: {format_number(current_limit)}"
        keyboard_rows.append([
            InlineKeyboardButton(
                text=label,
                callback_data=f"setlimit_currency:{currency}"
            )
        ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    await message.answer("Qaysi balans uchun limit?", reply_markup=keyboard)


@router.callback_query(F.data.startswith("setlimit_currency:"))
async def setlimit_currency_callback(callback: CallbackQuery, state: FSMContext):
    currency = callback.data.split(":")[1]
    await state.set_state(SetLimitState.waiting_amount)
    await state.update_data(currency=currency)

    await callback.message.answer(
        f"Oylik limit miqdorini kiriting:\n"
        f"Limitni o'chirish uchun \"0\" yozing."
    )
    await callback.answer()


@router.message(SetLimitState.waiting_amount)
async def process_limit_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.strip().replace(" ", "").replace(",", ""))
    except ValueError:
        await message.answer("❌ Faqat raqam kiriting.")
        return

    data = await state.get_data()
    currency = data["currency"]

    limit = amount if amount > 0 else None
    await update_balance_limit(message.from_user.id, currency, limit)

    await state.clear()

    if limit:
        await message.answer(
            f"✅ Limit o'rnatildi:\n"
            f"{format_number(limit)} {currency}"
        )
    else:
        await message.answer(f"✅ {currency} uchun limit olib tashlandi.")

