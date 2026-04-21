"""
Scheduler — background tasks.
"""

import logging
from datetime import datetime, timedelta
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.database import (
    users_collection, debts_collection, transactions_collection,
    get_monthly_expense, get_monthly_income, get_user_balance
)

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

# Bot reference uchun (dinamik eslatmalar uchun)
_bot_ref = None


def format_number(num: float) -> str:
    if num < 0:
        return "-" + f"{int(abs(num)):,}".replace(",", " ")
    return f"{int(num):,}".replace(",", " ")


# ═══════════════════════════════════════
# ERTALABGI ESLATMA (08:00)
# ═══════════════════════════════════════
async def check_morning_reminders(bot: Bot):
    today = datetime.utcnow()
    yesterday = today - timedelta(days=1)
    yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)

    cursor = users_collection.find({"settings.morning_reminder": True})
    users = await cursor.to_list(length=10000)

    for user in users:
        telegram_id = user["telegram_id"]
        # Fariq uchun UZS balansi olinadi (asosiysi)
        currency = "UZS"
        
        # Kecha sarflagan:
        tx_cursor = transactions_collection.find({
            "telegram_id": telegram_id,
            "type": "chiqim",
            "currency": currency,
            "affects_balance": True,
            "created_at": {"$gte": yesterday_start, "$lte": yesterday_end}
        })
        yesterday_txs = await tx_cursor.to_list(length=100)
        yesterday_expense = sum(tx["amount"] for tx in yesterday_txs)

        # Bu oy sarflagan:
        month_expense = await get_monthly_expense(telegram_id, currency)
        
        # Balans:
        balance = await get_user_balance(telegram_id, currency)

        msg = (
            f"☀️ Xayrli tong!\n\n"
            f"📉 Kecha sarflagan: {format_number(yesterday_expense)} {currency}\n"
            f"📊 Bu oy sarflagan: {format_number(month_expense)} {currency}\n"
            f"💰 Balans: {format_number(balance)} {currency}\n\n"
            f"💡 Bugungi xarajatlarni yozishni unutmang!"
        )
        try:
            await bot.send_message(chat_id=telegram_id, text=msg)
        except Exception as e:
            logger.error(f"Morning reminder error for {telegram_id}: {e}")


# ═══════════════════════════════════════
# KUNDUZGI ESLATMA (21:00)
# ═══════════════════════════════════════
async def check_evening_reminders(bot: Bot):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    cursor = users_collection.find({"settings.evening_reminder": True})
    users = await cursor.to_list(length=10000)

    for user in users:
        telegram_id = user["telegram_id"]
        currency = "UZS"
        
        tx_cursor = transactions_collection.find({
            "telegram_id": telegram_id,
            "currency": currency,
            "affects_balance": True,
            "created_at": {"$gte": today_start}
        })
        today_txs = await tx_cursor.to_list(length=100)
        
        kirim = sum(tx["amount"] for tx in today_txs if tx["type"] == "kirim")
        chiqim = sum(tx["amount"] for tx in today_txs if tx["type"] == "chiqim")

        msg = (
            f"🌙 Xayrli kech!\n\n"
            f"Bugun:\n"
            f"💰 Kirim: {format_number(kirim)} {currency}\n"
            f"💸 Chiqim: {format_number(chiqim)} {currency}\n\n"
            f"Bugungi xarajatlaringizni to'liq kirdingizmi? ✅"
        )
        try:
            await bot.send_message(chat_id=telegram_id, text=msg)
        except Exception as e:
            logger.error(f"Evening reminder error for {telegram_id}: {e}")


# ═══════════════════════════════════════
# OYLIK XULOSA (Har oy 1-kuni)
# ═══════════════════════════════════════
async def check_monthly_summary(bot: Bot):
    # Bu funksiya 1-kun chaqiriladi, shuning uchun "o'tgan oy" ni olamiz
    today = datetime.utcnow()
    last_month = today.replace(day=1) - timedelta(days=1)
    start_of_last_month = last_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_last_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(seconds=1)

    months_uz = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun", "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"]
    month_name = months_uz[last_month.month - 1]

    cursor = users_collection.find({})
    users = await cursor.to_list(length=10000)

    for user in users:
        telegram_id = user["telegram_id"]
        currency = "UZS"

        pipeline = [
            {"$match": {
                "telegram_id": telegram_id,
                "currency": currency,
                "affects_balance": True,
                "created_at": {"$gte": start_of_last_month, "$lte": end_of_last_month}
            }},
            {"$group": {
                "_id": "$type",
                "total": {"$sum": "$amount"}
            }}
        ]
        
        res = await transactions_collection.aggregate(pipeline).to_list(length=2)
        totals = {r["_id"]: r["total"] for r in res}
        kirim = totals.get("kirim", 0)
        chiqim = totals.get("chiqim", 0)
        tejaldi = kirim - chiqim

        # Eng ko'p sarflagan kategoriya
        cat_pipeline = [
            {"$match": {
                "telegram_id": telegram_id,
                "type": "chiqim",
                "currency": currency,
                "created_at": {"$gte": start_of_last_month, "$lte": end_of_last_month}
            }},
            {"$group": {
                "_id": "$category",
                "total": {"$sum": "$amount"}
            }},
            {"$sort": {"total": -1}},
            {"$limit": 1}
        ]
        top_cat_res = await transactions_collection.aggregate(cat_pipeline).to_list(length=1)
        
        top_cat_str = ""
        if top_cat_res and chiqim > 0:
            cat_name = top_cat_res[0]["_id"]
            cat_total = top_cat_res[0]["total"]
            pct = int((cat_total / chiqim) * 100)
            top_cat_str = f"🏆 Eng ko'p sarflagan: {cat_name}\n   {format_number(cat_total)} {currency} ({pct}%)"

        msg = (
            f"📊 {month_name} oyining xulosasi:\n\n"
            f"💰 Jami kirim: {format_number(kirim)} {currency}\n"
            f"💸 Jami chiqim: {format_number(chiqim)} {currency}\n"
            f"✅ Tejaldi: {format_number(tejaldi)} {currency}\n\n"
            f"{top_cat_str}\n\n"
            f"Yangi oyda omad! 💪"
        )
        try:
            await bot.send_message(chat_id=telegram_id, text=msg)
        except Exception as e:
            pass


# ═══════════════════════════════════════
# QARZ ESLATMALARI (09:00)
# ═══════════════════════════════════════
async def check_debt_reminders(bot: Bot):
    today = datetime.utcnow().date()

    cursor = debts_collection.find({
        "status": {"$in": ["active", "partial"]},
    })
    debts = await cursor.to_list(length=1000)

    for debt in debts:
        due_date_str = debt.get("due_date")
        if not due_date_str or due_date_str == "nomalum":
            continue

        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue

        telegram_id = debt["telegram_id"]
        person = debt["person"]
        amount = debt["amount"] - debt.get("paid_amount", 0)
        currency = debt.get("currency", "UZS")
        direction = debt.get("direction", "bergan")
        debt_id = str(debt["_id"])

        if amount <= 0:
            continue

        delta = (due_date - today).days

        msg = None
        keyboard = None

        if direction == "bergan":
            # Ular senga qarzdir (Olishim kerak)
            if delta == 3:
                msg = (
                    f"⏰ Eslatma!\n"
                    f"{person} sizga {format_number(amount)} {currency} qaytarishi "
                    f"endi 3 kun qoldi (📅 {due_date.strftime('%d.%m.%Y')})"
                )
            elif delta == 0:
                msg = (
                    f"🔔 Bugun!\n"
                    f"{person} {format_number(amount)} {currency} qaytarishi kerak edi.\n"
                    f"Qaytardimi?"
                )
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="✅ Ha, qaytardi", callback_data=f"debt_paid:{debt_id}"),
                        InlineKeyboardButton(text="❌ Yo'q, hali", callback_data=f"debt_not_paid:{debt_id}")
                    ]
                ])
            elif delta < 0 and abs(delta) % 3 == 0:
                # Har 3 kunda bir
                msg = (
                    f"❗ Muddati o'tdi!\n"
                    f"{person} {format_number(amount)} {currency} qaytarmadi.\n"
                    f"{abs(delta)} kun kechikdi."
                )
        else:
            # Sen ularga qarzsan (Berishim kerak)
            if delta == 3:
                msg = (
                    f"⏰ Eslatma!\n"
                    f"{person}ga {format_number(amount)} {currency} qaytarishingiz "
                    f"endi 3 kun qoldi (📅 {due_date.strftime('%d.%m.%Y')})"
                )
            elif delta == 0:
                msg = (
                    f"🔔 Bugun!\n"
                    f"{person}ga {format_number(amount)} {currency} qaytarishingiz kerak edi.\n"
                    f"Qaytardingizmi?"
                )
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="✅ Ha, qaytardim", callback_data=f"debt_paid:{debt_id}"),
                        InlineKeyboardButton(text="❌ Yo'q, hali", callback_data=f"debt_not_paid:{debt_id}")
                    ]
                ])
            elif delta < 0 and abs(delta) % 3 == 0:
                msg = (
                    f"❗ Muddati o'tdi!\n"
                    f"{person}ga {format_number(amount)} {currency} qaytarishingiz kerak edi.\n"
                    f"{abs(delta)} kun kechikdi."
                )

        if msg:
            try:
                if keyboard:
                    await bot.send_message(chat_id=telegram_id, text=msg, reply_markup=keyboard)
                else:
                    await bot.send_message(chat_id=telegram_id, text=msg)
            except Exception as e:
                pass


def setup_scheduler(bot: Bot):
    global _bot_ref
    _bot_ref = bot

    # Ertalab 08:00
    scheduler.add_job(check_morning_reminders, trigger="cron", hour=8, minute=0, args=[bot], id="morning_reminders", replace_existing=True)
    
    # Kechqurun 21:00
    scheduler.add_job(check_evening_reminders, trigger="cron", hour=21, minute=0, args=[bot], id="evening_reminders", replace_existing=True)
    
    # Har oy 1-kuni 10:00 da
    scheduler.add_job(check_monthly_summary, trigger="cron", day=1, hour=10, minute=0, args=[bot], id="monthly_summary", replace_existing=True)
    
    # Qarzlar 09:00 da
    scheduler.add_job(check_debt_reminders, trigger="cron", hour=9, minute=0, args=[bot], id="debt_reminders", replace_existing=True)
    
    scheduler.start()
    logger.info("Scheduler started — Cron jobs loaded.")


# ═══════════════════════════════════════
# DINAMIK ESLATMA (bir martalik)
# ═══════════════════════════════════════
async def send_one_time_reminder(telegram_id: int, text: str):
    """Bir martalik eslatma yuborish."""
    global _bot_ref
    if not _bot_ref:
        return
    try:
        await _bot_ref.send_message(chat_id=telegram_id, text=text)
        logger.info(f"One-time reminder sent to {telegram_id}")
    except Exception as e:
        logger.error(f"Failed to send one-time reminder to {telegram_id}: {e}")


def schedule_one_time_reminder(telegram_id: int, run_date: datetime, text: str):
    """Berilgan sanada bir marta ishlaydigan eslatma o'rnatadi."""
    job_id = f"reminder_{telegram_id}_{run_date.strftime('%Y%m%d%H%M')}"
    scheduler.add_job(
        send_one_time_reminder,
        trigger="date",
        run_date=run_date,
        args=[telegram_id, text],
        id=job_id,
        replace_existing=True,
    )
    logger.info(f"Scheduled one-time reminder for {telegram_id} at {run_date}")
