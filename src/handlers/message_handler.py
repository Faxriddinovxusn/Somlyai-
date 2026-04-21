"""
Message handler — core of the bot.
Processes text messages through AI and saves transactions/debts.
"""

from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from src.database import (
    insert_transaction, insert_debt,
    update_user_balance, get_user_balance,
    get_monthly_expense, get_user, ensure_balance_exists,
    get_custom_categories,
)
from src.services.groq_service import groq_service
from src.services.scheduler import schedule_one_time_reminder

router = Router()


def format_number(num: float) -> str:
    """1234567 → '1 234 567'"""
    if num < 0:
        return "-" + f"{int(abs(num)):,}".replace(",", " ")
    return f"{int(num):,}".replace(",", " ")


def parse_display_date(date_str: str) -> str:
    """YYYY-MM-DD → DD.MM.YYYY"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")
    except Exception:
        return date_str


async def check_limit_warning(telegram_id: int, currency: str, new_expense_total: float) -> str:
    """
    Limitni tekshirish.
    Returns warning string or empty string.
    """
    user = await get_user(telegram_id)
    bal_info = user.get("balances", {}).get(currency, {})
    limit = bal_info.get("limit")

    if not limit or limit <= 0:
        return ""

    pct = new_expense_total / limit
    remaining = limit - new_expense_total

    if pct >= 1.0:
        return (
            f"\n\n🚨 Limit tugadi! Bu oy "
            f"{format_number(new_expense_total)} {currency} sarfladingiz"
        )
    elif pct >= 0.8:
        return (
            f"\n\n⚠️ Diqqat! Oylik limitingizning 80% sarfladingiz"
        )
    else:
        return f"\n📊 Limit: {format_number(new_expense_total)}/{format_number(limit)} {currency}"


def build_debt_keyboard(debt_id: str) -> InlineKeyboardMarkup:
    """Qarz uchun inline tugmalar."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Qaytdi", callback_data=f"debt_paid:{debt_id}"),
            InlineKeyboardButton(text="⏰ Muddat uzayt", callback_data=f"debt_extend:{debt_id}"),
            InlineKeyboardButton(text="🗑 O'chir", callback_data=f"debt_delete:{debt_id}"),
        ]
    ])


@router.message(F.text)
async def process_text_message(message: Message):
    await handle_transaction_text(message, message.text)


async def handle_transaction_text(message: Message, text: str):
    """
    Main processing pipeline:
    1. AI parse
    2. Route by intent
    3. Save & respond with formatted message
    """
    user_id = message.from_user.id
    current_date = datetime.now().strftime("%Y-%m-%d")

    user = await get_user(user_id)
    language = user.get("language", "uz")

    # Shaxsiy kategoriyalarni olish
    custom_cats = await get_custom_categories(user_id)
    custom_cats_list = [{"emoji": c["emoji"], "name": c["name"], "type": c["type"]} for c in custom_cats] if custom_cats else None

    # ─── 1. Send to AI ───
    try:
        data = await groq_service.parse_transaction(text, current_date, language, custom_cats_list)
    except Exception as e:
        await message.answer("⚠️ Tizimda xatolik yuz berdi. Iltimos keyinroq urinib ko'ring.")
        return

    # ─── 2. Chat intent ───
    if data.get("intent") == "chat":
        reply_msg = data.get("reply", "Menga moliyaviy ma'lumot kiriting.")
        # User ismini qo'shish (agar bor bo'lsa)
        name = user.get("full_name", "")
        if name and "{name}" not in reply_msg:
            pass  # AI allaqachon ism bilan javob qaytarishi kerak
        await message.answer(reply_msg)
        return

    # ─── 3. Unclear ───
    if data.get("unclear"):
        reason = data.get("unclear_reason", "")
        unclear_msg = (
            "Tushunmadim 🤔\n\n"
        )
        if reason:
            unclear_msg += f"Sabab: {reason}\n\n"
        unclear_msg += (
            "Aniqroq yozing:\n"
            "💸 Chiqim: «Taksiga 15,000 so'm»\n"
            "💰 Kirim: «Oylik 4 million tushdi»\n"
            "🤝 Qarz: «Jasurga 100 ming berdim»"
        )
        await message.answer(unclear_msg)
        return

    # ─── 4. Process transactions ───
    transactions = data.get("transactions", [])
    if not transactions:
        await message.answer("Hech qanday tranzaksiya topilmadi. Aniqroq yozing.")
        return

    for t in transactions:
        t_type = t.get("type")
        amount = float(t.get("amount", 0))
        currency = t.get("currency", "UZS").upper()
        date_str = t.get("date", current_date)
        display_date = parse_display_date(date_str)
        category = t.get("category", "📋 Boshqa")
        description = t.get("description", "")

        await ensure_balance_exists(user_id, currency)

        # ════════════════════════════
        #  KIRIM
        # ════════════════════════════
        if t_type == "kirim":
            await insert_transaction({
                "telegram_id": user_id,
                "type": "kirim",
                "amount": amount,
                "currency": currency,
                "date": date_str,
                "description": description,
                "category": category,
                "affects_balance": True,
            })

            new_balance = await update_user_balance(user_id, currency, amount, is_income=True)

            msg = (
                f"Hisobotga qo'shildi ✅\n\n"
                f"💰 Kirim:\n"
                f"📅 Sana: {display_date}\n"
                f"💵 Summa: {format_number(amount)} {currency}\n"
                f"🏷 Kategoriya: {category}\n"
                f"📝 Izoh: {description}\n\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"💵 {currency} balansi: {format_number(new_balance)} {currency}"
            )
            await message.answer(msg)

        # ════════════════════════════
        #  CHIQIM
        # ════════════════════════════
        elif t_type == "chiqim":
            await insert_transaction({
                "telegram_id": user_id,
                "type": "chiqim",
                "amount": amount,
                "currency": currency,
                "date": date_str,
                "description": description,
                "category": category,
                "affects_balance": True,
            })

            new_balance = await update_user_balance(user_id, currency, amount, is_income=False)

            # Limit check
            monthly_total = await get_monthly_expense(user_id, currency)
            limit_warning = await check_limit_warning(user_id, currency, monthly_total)

            msg = (
                f"Hisobotga qo'shildi ✅\n\n"
                f"💸 Chiqim:\n"
                f"📅 Sana: {display_date}\n"
                f"💵 Summa: {format_number(amount)} {currency}\n"
                f"🏷 Kategoriya: {category}\n"
                f"📝 Izoh: {description}\n\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"💵 {currency} balansi: {format_number(new_balance)} {currency}"
                f"{limit_warning}"
            )
            await message.answer(msg)

        # ════════════════════════════
        #  QARZ
        # ════════════════════════════
        elif t_type == "qarz":
            direction = t.get("direction", "bergan")
            person = t.get("person", "Noma'lum")
            due_date = t.get("due_date", "nomalum")

            # Save to Debt collection (primary)
            debt_id = await insert_debt({
                "telegram_id": user_id,
                "person": person,
                "amount": amount,
                "currency": currency,
                "direction": direction,
                "date": date_str,
                "due_date": due_date,
                "status": "active",
            })

            # Save to Transaction collection (history only)
            await insert_transaction({
                "telegram_id": user_id,
                "type": "qarz",
                "amount": amount,
                "currency": currency,
                "date": date_str,
                "description": f"Qarz — {person}",
                "category": "🤝 Qarz",
                "affects_balance": False,
            })

            # Balance does NOT change
            current_balance = await get_user_balance(user_id, currency)

            # Direction display
            if direction == "bergan":
                tur_text = "Sen berding (u senga qarzdir)"
                tur_tab = "Olishim kerak"
            else:
                tur_text = "Sen olding (sen unga qarzsan)"
                tur_tab = "Berishim kerak"

            # Due date display
            if due_date and due_date != "nomalum":
                due_display = parse_display_date(due_date)
            else:
                due_display = "Belgilanmagan"

            msg = (
                f"Qarzlar ro'yxatiga qo'shildi ✅\n\n"
                f"🤝 Qarz:\n"
                f"📅 Sana: {display_date}\n"
                f"👤 Kim: {person}\n"
                f"💵 Miqdor: {format_number(amount)} {currency}\n"
                f"📌 Tur: {tur_text}\n"
                f"📂 Tab: {tur_tab}\n"
                f"⏰ Muddat: {due_display}\n\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"💵 {currency} balansi: {format_number(current_balance)} {currency}\n"
                f"(Qarz balansga ta'sir qilmadi)"
            )

            keyboard = build_debt_keyboard(debt_id)
            await message.answer(msg, reply_markup=keyboard)

        # ════════════════════════════
        #  ESLATMA (reminder) O'RNATISH
        # ════════════════════════════
        reminder_date = t.get("reminder_date")
        reminder_time = t.get("reminder_time")
        if reminder_date and reminder_date != "null" and reminder_date != "nomalum":
            try:
                r_time = reminder_time if reminder_time else datetime.now().strftime("%H:%M")
                remind_dt = datetime.strptime(f"{reminder_date} {r_time}", "%Y-%m-%d %H:%M")
                if remind_dt > datetime.now():
                    remind_text = f"⏰ Eslatma!\n{description or category}\n💵 {format_number(amount)} {currency}"
                    if t_type == "qarz":
                        person_name = t.get("person", "")
                        if direction == "bergan":
                            remind_text = f"⏰ Eslatma!\n{person_name}ga {format_number(amount)} {currency} berish vaqti keldi!"
                        else:
                            remind_text = f"⏰ Eslatma!\n{person_name}dan {format_number(amount)} {currency} olish vaqtingiz keldi!"
                    schedule_one_time_reminder(user_id, remind_dt, remind_text)
            except Exception:
                pass
