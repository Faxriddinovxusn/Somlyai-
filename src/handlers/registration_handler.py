"""
Registration handler — Name + Phone collection.

Handles:
- Text name input
- Voice name input (transcribed → AI extracts name)
- Contact sharing via ReplyKeyboard
"""

import os
from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from src.states import RegistrationStates
from src.database import get_user, update_user_name, update_user_phone
from src.services.groq_service import groq_service
from src.handlers.start_handler import t

router = Router()


# ═══════════════════════════════════════
# ISM QABUL QILISH (matn)
# ═══════════════════════════════════════
@router.message(RegistrationStates.waiting_for_name, F.text)
async def process_name_text(message: Message, state: FSMContext):
    name = message.text.strip()

    # Agar buyruq yuborsa — e'tiborsiz qoldiramiz
    if name.startswith("/"):
        return

    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user.get("language", "uz")

    await update_user_name(user_id, name)
    await state.set_state(RegistrationStates.waiting_for_contact)

    # Contact so'rash
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "share_contact_btn"), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        t(lang, "ask_contact", name=name),
        reply_markup=keyboard,
    )


# ═══════════════════════════════════════
# ISM QABUL QILISH (ovozli)
# ═══════════════════════════════════════
@router.message(RegistrationStates.waiting_for_name, F.voice)
async def process_name_voice(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user.get("language", "uz")

    status_msg = await message.answer("🎤 ...")

    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path

    os.makedirs("temp", exist_ok=True)
    local_path = f"temp/{file_id}.ogg"

    try:
        await bot.download_file(file_path, local_path)
        transcribed = await groq_service.transcribe_audio_with_retry(local_path)
        # AI orqali faqat ismni ajratib olish
        name = await groq_service.extract_name(transcribed)

        if not name or len(name) < 2:
            name = transcribed.strip()

        await update_user_name(user_id, name)
        await state.set_state(RegistrationStates.waiting_for_contact)
        await status_msg.delete()

        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=t(lang, "share_contact_btn"), request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await message.answer(
            t(lang, "ask_contact", name=name),
            reply_markup=keyboard,
        )

    except Exception:
        await status_msg.edit_text("❌ Ovozni tahlil qilib bo'lmadi. Iltimos, ismingizni matn sifatida yozing.")
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)


# ═══════════════════════════════════════
# CONTACT QABUL QILISH
# ═══════════════════════════════════════
@router.message(RegistrationStates.waiting_for_contact, F.contact)
async def process_contact(message: Message, state: FSMContext):
    user_id = message.from_user.id
    phone = message.contact.phone_number
    user = await get_user(user_id)
    lang = user.get("language", "uz")
    name = user.get("full_name", "")

    await update_user_phone(user_id, phone)
    await state.clear()
    
    from src.database import get_all_channels
    channels = await get_all_channels()
    
    if channels:
        # Show channels right away
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        buttons = []
        for ch in channels:
            buttons.append([InlineKeyboardButton(text=f"📢 {ch['name']}", url=ch['link'])])
            
        check_texts = {
            "uz": "✅ Davom etish",
            "en": "✅ Continue",
            "ru": "✅ Продолжить",
        }
        buttons.append([InlineKeyboardButton(
            text=check_texts.get(lang, check_texts["uz"]),
            callback_data="check_sub"
        )])
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        header_texts = {
            "uz": "📢 Foydali kanallarimiz:\n",
            "en": "📢 Our useful channels:\n",
            "ru": "📢 Наши полезные каналы:\n",
        }
        text = header_texts.get(lang, header_texts["uz"])
        for i, ch in enumerate(channels, 1):
            text += f"{i}️⃣ {ch['name']}\n"
            
        await message.answer("✅ Ro'yxatdan o'tdingiz!", reply_markup=ReplyKeyboardRemove())
        await message.answer(text, reply_markup=keyboard)
    else:
        from src.handlers.menu_handler import get_main_keyboard
        kbd = await get_main_keyboard()
        await message.answer(
            t(lang, "registration_done", name=name),
            reply_markup=kbd,
        )


# ═══════════════════════════════════════
# CONTACT BERMAGAN — MATN YOZGAN
# ═══════════════════════════════════════
@router.message(RegistrationStates.waiting_for_contact, F.text)
async def process_contact_text_fallback(message: Message):
    if message.text.startswith("/"):
        return
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user.get("language", "uz")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "share_contact_btn"), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(t(lang, "contact_required"), reply_markup=keyboard)


# ═══════════════════════════════════════
# CONTACT BERMAGAN — OVOZ YUBORGAN
# ═══════════════════════════════════════
@router.message(RegistrationStates.waiting_for_contact, F.voice)
async def process_contact_voice_fallback(message: Message):
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user.get("language", "uz")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "share_contact_btn"), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(t(lang, "contact_required"), reply_markup=keyboard)
