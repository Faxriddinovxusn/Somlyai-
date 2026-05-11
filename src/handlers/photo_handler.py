"""
Photo handler — processes images sent to the bot.
Scans for QR codes (fiscal receipts) and creates expense transactions.
"""

import logging
import os
import tempfile
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from src.database import (
    get_user, insert_transaction, update_user_balance,
    ensure_balance_exists, get_user_all_balance_names,
    save_qr_scan
)
from src.services.qr_service import decode_qr_from_bytes, is_fiscal_url, fetch_fiscal_receipt, format_receipt_message
from src.services.i18n import t
from src.services.error_handler import log_error, ErrorType

logger = logging.getLogger(__name__)
router = Router()

# Temp storage for pending QR receipts (user_id -> receipt_data)
_pending_receipts = {}

# Kategoriyalar
QR_CATEGORIES = [
    ("🍔 Oziq-ovqat", "Oziq-ovqat"),
    ("🛍 Xaridlar", "Xaridlar"),
    ("🏠 Uy-joy", "Uy-joy"),
    ("📦 Boshqa", "Boshqa xarajatlar"),
]


@router.message(F.photo)
async def process_photo_message(message: Message, bot: Bot):
    """Rasm kelganda QR kod qidiramiz."""
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user.get("language", "uz") if user else "uz"

    # Status xabar
    status_msg = await message.answer("🔍 QR kod qidirilmoqda...")

    try:
        # Rasmning eng katta versiyasini yuklab olish
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        
        # Temporary file ga saqlash
        file_bytes = b""
        tmp_path = os.path.join(tempfile.gettempdir(), f"somly_qr_{user_id}.jpg")
        await bot.download_file(file.file_path, tmp_path)
        
        with open(tmp_path, "rb") as f:
            file_bytes = f.read()
        
        # Tozalash
        try:
            os.remove(tmp_path)
        except:
            pass

        if not file_bytes:
            await status_msg.edit_text("❌ Rasmni yuklab bo'lmadi. Qayta yuboring.")
            return

        # QR kod qidirish
        qr_data = decode_qr_from_bytes(file_bytes)

        if not qr_data:
            await status_msg.edit_text(
                "🔍 Rasmda QR kod topilmadi.\n\n"
                "Chekni to'g'ridan-to'g'ri va yaxshiroq yoritilgan joyda suratga oling."
            )
            await save_qr_scan(user_id, "not_found", {})
            return

        # QR topildi — fiscal URL mi?
        if not is_fiscal_url(qr_data):
            # Fiscal emas — oddiy rasm sifatida qabul qilish
            # Caption ni matn sifatida AI ga yuborish mumkin
            await status_msg.edit_text(
                "📎 QR kod topildi, lekin bu fiskal chek emas.\n"
                "Agar xarajat kiritmoqchi bo'lsangiz, summasini matn sifatida yozing."
            )
            await save_qr_scan(user_id, "not_fiscal", {"url": qr_data})
            return

        # Fiscal URL — ma'lumotlarni olish
        await status_msg.edit_text("🧾 Chek ma'lumotlari olinmoqda...")

        receipt = await fetch_fiscal_receipt(qr_data)

        if not receipt["success"] or receipt["total"] == 0:
            await status_msg.edit_text(
                "⚠️ Chek ma'lumotlari hozir olinmayapti.\n"
                "Summani qo'lda kiriting yoki keyinroq qayta urinib ko'ring."
            )
            await save_qr_scan(user_id, "fetch_failed", {"url": qr_data, "error": receipt.get("error")})
            return

        # Muvaffaqiyatli! Natijani ko'rsatish
        receipt_text = format_receipt_message(receipt)

        # Balanslarni olish
        balance_names = await get_user_all_balance_names(user_id)
        default_balance = balance_names[0] if balance_names else "UZS"

        # Receiptni vaqtinchalik saqlash
        _pending_receipts[user_id] = {
            "receipt": receipt,
            "category": "Oziq-ovqat",
            "balance_name": default_balance,
        }

        # Inline tugmalar
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Saqlash", callback_data="qr_save"),
                InlineKeyboardButton(text="✏️ Kategoriya", callback_data="qr_edit_cat"),
                InlineKeyboardButton(text="❌ Bekor", callback_data="qr_cancel"),
            ]
        ])

        await status_msg.edit_text(receipt_text, reply_markup=keyboard, parse_mode="HTML")
        await save_qr_scan(user_id, "success", {
            "url": qr_data,
            "total": receipt["total"],
            "shop": receipt.get("shop_name"),
            "items_count": len(receipt.get("items", []))
        })

    except Exception as e:
        logger.error(f"Photo handler error: {e}", exc_info=True)
        log_error(ErrorType.UNKNOWN, f"Photo QR scan error: {e}", user_id, e)
        await status_msg.edit_text(
            "❌ Rasmni qayta ishlashda xatolik yuz berdi.\n"
            "Qayta urinib ko'ring yoki summani qo'lda kiriting."
        )


@router.callback_query(lambda c: c.data == "qr_save")
async def qr_save_callback(callback: CallbackQuery):
    """QR chekni xarajat sifatida saqlash."""
    user_id = callback.from_user.id
    pending = _pending_receipts.get(user_id)

    if not pending:
        await callback.answer("⏳ Ma'lumotlar topilmadi. Qayta skanerlang.", show_alert=True)
        return

    receipt = pending["receipt"]
    category = pending["category"]
    balance_name = pending["balance_name"]

    try:
        from datetime import datetime

        # Balansni tekshirish
        await ensure_balance_exists(user_id, balance_name, "UZS")

        # Izoh tayyorlash
        items_count = len(receipt.get("items", []))
        shop = receipt.get("shop_name", "Do'kon")
        description = f"{shop} — {items_count} ta mahsulot" if items_count else shop

        # Tranzaksiya yaratish
        tx_data = {
            "telegram_id": user_id,
            "type": "chiqim",
            "amount": receipt["total"],
            "currency": "UZS",
            "category": category,
            "description": description,
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "source": "qr_scan",
            "receipt_items": receipt.get("items", []),
            "shop_name": shop,
            "affects_balance": True,
        }
        await insert_transaction(tx_data)

        # Balansni yangilash
        await update_user_balance(user_id, balance_name, -receipt["total"])

        # Tozalash
        _pending_receipts.pop(user_id, None)

        formatted_total = f"{receipt['total']:,}".replace(",", " ")
        await callback.message.edit_text(
            f"✅ <b>Saqlandi!</b>\n\n"
            f"🧾 {description}\n"
            f"💵 {formatted_total} UZS\n"
            f"📂 {category}\n"
            f"📅 {datetime.utcnow().strftime('%d.%m.%Y')}",
            parse_mode="HTML"
        )
        await callback.answer("✅ Xarajat saqlandi!")

    except Exception as e:
        logger.error(f"QR save error: {e}", exc_info=True)
        await callback.answer("❌ Saqlashda xatolik", show_alert=True)


@router.callback_query(lambda c: c.data == "qr_edit_cat")
async def qr_edit_category_callback(callback: CallbackQuery):
    """Kategoriya tanlash."""
    user_id = callback.from_user.id
    pending = _pending_receipts.get(user_id)

    if not pending:
        await callback.answer("⏳ Ma'lumotlar topilmadi.", show_alert=True)
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=label, callback_data=f"qr_cat_{value}")]
        for label, value in QR_CATEGORIES
    ] + [
        [InlineKeyboardButton(text="🔙 Ortga", callback_data="qr_back")]
    ])

    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("qr_cat_"))
async def qr_select_category_callback(callback: CallbackQuery):
    """Kategoriya tanlandi."""
    user_id = callback.from_user.id
    pending = _pending_receipts.get(user_id)

    if not pending:
        await callback.answer("⏳ Ma'lumotlar topilmadi.", show_alert=True)
        return

    category = callback.data.replace("qr_cat_", "")
    _pending_receipts[user_id]["category"] = category

    # Asosiy tugmalarni qaytarish
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Saqlash", callback_data="qr_save"),
            InlineKeyboardButton(text=f"📂 {category}", callback_data="qr_edit_cat"),
            InlineKeyboardButton(text="❌ Bekor", callback_data="qr_cancel"),
        ]
    ])

    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer(f"✅ Kategoriya: {category}")


@router.callback_query(lambda c: c.data == "qr_back")
async def qr_back_callback(callback: CallbackQuery):
    """Asosiy tugmalarga qaytish."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Saqlash", callback_data="qr_save"),
            InlineKeyboardButton(text="✏️ Kategoriya", callback_data="qr_edit_cat"),
            InlineKeyboardButton(text="❌ Bekor", callback_data="qr_cancel"),
        ]
    ])
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(lambda c: c.data == "qr_cancel")
async def qr_cancel_callback(callback: CallbackQuery):
    """Bekor qilish."""
    user_id = callback.from_user.id
    _pending_receipts.pop(user_id, None)

    await callback.message.edit_text("❌ Chek bekor qilindi.")
    await callback.answer()
