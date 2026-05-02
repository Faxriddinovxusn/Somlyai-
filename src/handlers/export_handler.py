"""
Export handler.
Generates an advanced Excel file with all user transactions and debts.
"""

import io
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from src.database import get_user, transactions_collection, get_active_debts
from src.services.excel_service import generate_excel_report

router = Router()

def get_export_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Bu oy", callback_data="export_this_month"),
            InlineKeyboardButton(text="O'tgan oy", callback_data="export_last_month")
        ],
        [
            InlineKeyboardButton(text="Oxirgi 3 oy", callback_data="export_last_3_months"),
            InlineKeyboardButton(text="Hammasi", callback_data="export_all_time")
        ]
    ])

@router.message(Command("excel"))
@router.message(F.text == "📥 Yuklab olish")
async def show_export_menu(message: Message, state: FSMContext):
    """Show export period selection."""
    await state.clear()
    await message.answer(
        "📥 <b>Hisobot yuklab olish</b>\n\nQaysi davr uchun hisobot kerakligini tanlang:",
        reply_markup=get_export_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("export_"))
async def process_export_period(callback: CallbackQuery):
    """Process period selection and generate report."""
    action = callback.data
    user_id = callback.from_user.id
    
    now = datetime.utcnow()
    start_date = None
    end_date = now
    period_text = ""
    
    if action == "export_this_month":
        start_date = datetime(now.year, now.month, 1)
        end_date = now
        month_name = _get_uzbek_month(now.month)
        period_text = f"{month_name} {now.year}"
    elif action == "export_last_month":
        # Get first day of this month
        first_day_this_month = datetime(now.year, now.month, 1)
        # Get last day of last month
        last_day_last_month = first_day_this_month - timedelta(days=1)
        # Get first day of last month
        start_date = datetime(last_day_last_month.year, last_day_last_month.month, 1)
        end_date = last_day_last_month.replace(hour=23, minute=59, second=59)
        month_name = _get_uzbek_month(start_date.month)
        period_text = f"{month_name} {start_date.year}"
    elif action == "export_last_3_months":
        start_date = now - timedelta(days=90)
        period_text = "Oxirgi 3 oy"
    elif action == "export_all_time":
        # No date filter, get all
        start_date = datetime(2020, 1, 1)
        period_text = "Barcha vaqt"
        
    await callback.message.delete()
    await generate_and_send_excel(callback.message, user_id, start_date, end_date, period_text)


async def generate_and_send_excel(message: Message, user_id: int, start_date: datetime, end_date: datetime, period_text: str):
    """Generate Excel report and send to user."""
    wait_msg = await message.answer("⏳ <i>Hisobot tayyorlanmoqda, kuting...</i>", parse_mode="HTML")
    
    try:
        # Generate Excel file
        filepath = await generate_excel_report(user_id, start_date, end_date, language="uz")
        
        # Get user name for caption
        user = await get_user(user_id)
        full_name = user.get("full_name", "Foydalanuvchi")
        
        # Calculate totals for caption using date field (same as report)
        date_from_str = start_date.strftime("%Y-%m-%d")
        date_to_str = end_date.strftime("%Y-%m-%d")
        
        query = {
            "telegram_id": user_id,
            "date": {
                "$gte": date_from_str,
                "$lte": date_to_str
            }
        }
        
        transactions = await transactions_collection.find(query).to_list(None)
        total_income = sum(tx.get("amount", 0) for tx in transactions if tx.get("type") == "kirim")
        total_expense = sum(tx.get("amount", 0) for tx in transactions if tx.get("type") == "chiqim")
        net_balance = total_income - total_expense
        
        # Read file
        with open(filepath, 'rb') as f:
            file_data = f.read()
        
        # Get filename from filepath
        filename = filepath.split('/')[-1]
        
        # Create caption
        caption = (
            f"📊 <b>Hisobotingiz tayyor!</b>\n\n"
            f"📅 <b>Davr:</b> {period_text}\n"
            f"💰 <b>Kirim:</b> {total_income:,.0f} UZS\n"
            f"💸 <b>Chiqim:</b> {total_expense:,.0f} UZS\n"
            f"✅ <b>Qoldiq:</b> {net_balance:,.0f} UZS\n\n"
            f"📎 <code>{filename}</code>"
        )
        
        # Send file
        file = BufferedInputFile(file_data, filename=filename)
        await wait_msg.delete()
        await message.answer_document(
            document=file,
            caption=caption,
            parse_mode="HTML"
        )
        
    except Exception as e:
        await wait_msg.edit_text(f"❌ Xato: {str(e)}")


def _get_uzbek_month(month_num: int) -> str:
    """Convert month number to Uzbek month name."""
    months = {
        1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel", 5: "May", 6: "Iyun",
        7: "Iyul", 8: "Avgust", 9: "Sentyabr", 10: "Oktyabr", 11: "Noyabr", 12: "Dekabr"
    }
    return months.get(month_num, str(month_num))

