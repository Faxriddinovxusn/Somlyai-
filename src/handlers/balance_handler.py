"""
Balance handler — balance management commands.

/balance — show all balances
/newbalance — create a new currency balance (interactive)
/setlimit — set monthly spending limit for a currency
"""

from datetime import datetime
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.database import (
    get_user, get_user_all_balances,
    create_custom_balance, update_balance_limit,
    get_monthly_expense, get_monthly_income,
)

router = Router()

# Available colors
COLORS = {
    "🔵": "#3B82F6",
    "🟢": "#10B981",
    "🔴": "#EF4444",
    "🟡": "#F59E0B",
    "🟣": "#8B5CF6",
    "🟠": "#F97316",
    "⚪": "#6B7280",
    "🩵": "#06B6D4",
}


def format_number(num: float) -> str:
    if num < 0:
        return "-" + f"{int(abs(num)):,}".replace(",", " ")
    return f"{int(num):,}".replace(",", " ")


# ═══════════════════════════════════════
# FSM States
# ═══════════════════════════════════════

class NewBalanceState(StatesGroup):
    waiting_currency = State()
    waiting_title = State()
    waiting_initial_amount = State()
    waiting_color = State()
    waiting_limit = State()


class SetLimitState(StatesGroup):
    waiting_currency = State()
    waiting_amount = State()


# ═══════════════════════════════════════
# /balance — Balanslar ko'rish
# ═══════════════════════════════════════

@router.message(Command("balance"))
async def balance_command(message: Message):
    user_id = message.from_user.id
    balances = await get_user_all_balances(user_id)

    if not balances:
        await message.answer("Sizda hali balans yo'q. /newbalance buyrug'i bilan qo'shing.")
        return

    msg_parts = ["💰 Sizning balanslaringiz:\n", "━━━━━━━━━━━━━━━━"]

    for currency, info in balances.items():
        amount = info.get("amount", 0)
        title = info.get("title", currency)
        limit = info.get("limit")

        line = f"💵 {title} ({currency}): {format_number(amount)} {currency}"
        msg_parts.append(line)

        if limit and limit > 0:
            monthly = await get_monthly_expense(user_id, currency)
            remaining = limit - monthly
            pct = int((monthly / limit) * 100) if limit > 0 else 0

            # Progress bar
            filled = min(pct // 10, 10)
            bar = "▓" * filled + "░" * (10 - filled)
            msg_parts.append(
                f"   📊 Limit: [{bar}] {pct}%"
                f" ({format_number(monthly)}/{format_number(limit)} {currency})"
            )
            if remaining < 0:
                msg_parts.append(f"   🚨 Limit {format_number(abs(remaining))} {currency} ga oshib ketdi!")
        msg_parts.append("")

    msg_parts.append("━━━━━━━━━━━━━━━━")
    msg_parts.append("📌 /newbalance — Yangi balans qo'shish")
    msg_parts.append("📌 /setlimit — Oylik limit o'rnatish")

    await message.answer("\n".join(msg_parts))


# ═══════════════════════════════════════
# /newbalance — Yangi balans yaratish
# ═══════════════════════════════════════

@router.message(Command("newbalance"))
async def newbalance_command(message: Message, state: FSMContext):
    await state.set_state(NewBalanceState.waiting_currency)
    await message.answer(
        "🆕 Yangi balans yaratish\n\n"
        "1️⃣ Valyuta kodini kiriting:\n"
        "Masalan: UZS, USD, EUR, RUB, KZT, GBP, TRY, JPY, CNY ...\n\n"
        "Dunyodagi istalgan valyuta kodini yozishingiz mumkin."
    )


@router.message(NewBalanceState.waiting_currency)
async def process_balance_currency(message: Message, state: FSMContext):
    currency = message.text.strip().upper()
    if len(currency) < 2 or len(currency) > 5:
        await message.answer("❌ Valyuta kodi 2-5 belgi bo'lishi kerak. Qaytadan kiriting.")
        return

    # Check if already exists
    user = await get_user(message.from_user.id)
    if currency in user.get("balances", {}):
        await message.answer(
            f"⚠️ {currency} balansi allaqachon mavjud!\n"
            "Boshqa valyuta kiriting yoki /cancel bosing."
        )
        return

    await state.update_data(currency=currency)
    await state.set_state(NewBalanceState.waiting_title)
    await message.answer(
        f"2️⃣ {currency} balansi uchun nom kiriting:\n"
        f"Masalan: So'm, Dollar, Yevro, Rubl..."
    )


@router.message(NewBalanceState.waiting_title)
async def process_balance_title(message: Message, state: FSMContext):
    title = message.text.strip()
    if len(title) > 30:
        await message.answer("❌ Nom 30 belgidan oshmasin.")
        return

    await state.update_data(title=title)
    await state.set_state(NewBalanceState.waiting_initial_amount)
    await message.answer(
        f"3️⃣ Boshlang'ich miqdorni kiriting:\n"
        f"Masalan: 0, 1000000, 500\n"
        f"(Hozirda hisobingizdagi pul miqdori)"
    )


@router.message(NewBalanceState.waiting_initial_amount)
async def process_balance_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.strip().replace(" ", "").replace(",", ""))
    except ValueError:
        await message.answer("❌ Faqat raqam kiriting.")
        return

    await state.update_data(initial_amount=amount)
    await state.set_state(NewBalanceState.waiting_color)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=emoji, callback_data=f"balance_color:{hex_code}")
         for emoji, hex_code in list(COLORS.items())[:4]],
        [InlineKeyboardButton(text=emoji, callback_data=f"balance_color:{hex_code}")
         for emoji, hex_code in list(COLORS.items())[4:]],
    ])

    await message.answer("4️⃣ Rang tanlang:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("balance_color:"))
async def process_balance_color(callback: CallbackQuery, state: FSMContext):
    color = callback.data.split(":")[1]
    await state.update_data(color=color)
    await state.set_state(NewBalanceState.waiting_limit)

    await callback.message.answer(
        "5️⃣ Oylik chiqim limiti o'rnatasizmi?\n\n"
        "Limit miqdorini kiriting (raqam).\n"
        "Yoki \"yo'q\" deb yozing (limitsiz)."
    )
    await callback.answer()


@router.message(NewBalanceState.waiting_limit)
async def process_balance_limit(message: Message, state: FSMContext):
    text = message.text.strip().lower()
    limit = None

    if text not in ["yo'q", "yoq", "0", "no", "-"]:
        try:
            limit = float(text.replace(" ", "").replace(",", ""))
            if limit <= 0:
                limit = None
        except ValueError:
            await message.answer("❌ Raqam kiriting yoki \"yo'q\" deb yozing.")
            return

    data = await state.get_data()
    currency = data["currency"]
    title = data["title"]
    initial_amount = data["initial_amount"]
    color = data["color"]

    await create_custom_balance(
        telegram_id=message.from_user.id,
        currency=currency,
        title=title,
        initial_amount=initial_amount,
        color=color,
        limit=limit,
    )

    await state.clear()

    limit_text = f"{format_number(limit)} {currency}/oy" if limit else "O'rnatilmagan"
    await message.answer(
        f"✅ Yangi balans yaratildi!\n\n"
        f"💵 {title} ({currency})\n"
        f"💰 Boshlang'ich: {format_number(initial_amount)} {currency}\n"
        f"📊 Limit: {limit_text}\n\n"
        f"/balance — barcha balanslarni ko'rish"
    )


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
    await message.answer("📊 Qaysi balansga limit o'rnatmoqchisiz?", reply_markup=keyboard)


@router.callback_query(F.data.startswith("setlimit_currency:"))
async def setlimit_currency_callback(callback: CallbackQuery, state: FSMContext):
    currency = callback.data.split(":")[1]
    await state.set_state(SetLimitState.waiting_amount)
    await state.update_data(currency=currency)

    await callback.message.answer(
        f"📊 {currency} uchun oylik chiqim limitini kiriting:\n"
        f"Masalan: 5000000\n\n"
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
            f"✅ {currency} uchun oylik limit: {format_number(limit)} {currency}\n\n"
            f"Har bir chiqimdan keyin limitingiz holati ko'rsatiladi."
        )
    else:
        await message.answer(f"✅ {currency} uchun limit olib tashlandi.")


# ═══════════════════════════════════════
# /cancel — FSM bekor qilish
# ═══════════════════════════════════════

@router.message(Command("cancel"))
async def cancel_command(message: Message, state: FSMContext):
    current = await state.get_state()
    if current:
        await state.clear()
        await message.answer("❌ Amal bekor qilindi.")
    else:
        await message.answer("Hech narsa bekor qilinmadi — hozirda faol amal yo'q.")
