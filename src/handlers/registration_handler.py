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
from src.database import get_user, update_user_name, update_user_phone, update_user_demographics
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

    username = message.from_user.username
    await update_user_name(user_id, name, username=username)
    await state.set_state(RegistrationStates.waiting_for_age)

    # Yosh so'rash
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="18 - 25"), KeyboardButton(text="25 - 30")],
            [KeyboardButton(text="30 - 35"), KeyboardButton(text="35 - 45")],
            [KeyboardButton(text="45+")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        t(lang, "ask_age"),
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

        username = message.from_user.username
        await update_user_name(user_id, name, username=username)
        await state.set_state(RegistrationStates.waiting_for_age)
        await status_msg.delete()

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="18 - 25"), KeyboardButton(text="25 - 30")],
                [KeyboardButton(text="30 - 35"), KeyboardButton(text="35 - 45")],
                [KeyboardButton(text="45+")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await message.answer(
            t(lang, "ask_age"),
            reply_markup=keyboard,
        )

    except Exception:
        await status_msg.edit_text("❌ Ovozni tahlil qilib bo'lmadi. Iltimos, ismingizni matn sifatida yozing.")
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)


# ═══════════════════════════════════════
# YOSH QABUL QILISH
# ═══════════════════════════════════════
@router.message(RegistrationStates.waiting_for_age, F.text)
async def process_age(message: Message, state: FSMContext):
    age = message.text.strip()
    if age.startswith("/"): return
    
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user.get("language", "uz")
    
    await update_user_demographics(user_id, age=age)
    await state.set_state(RegistrationStates.waiting_for_location)
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "btn_uzb")), KeyboardButton(text=t(lang, "btn_other_country"))]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(t(lang, "ask_location"), reply_markup=keyboard)


# ═══════════════════════════════════════
# JOYLASHUV QABUL QILISH
# ═══════════════════════════════════════
@router.message(RegistrationStates.waiting_for_location, F.text)
async def process_location(message: Message, state: FSMContext):
    loc = message.text.strip()
    if loc.startswith("/"): return
    
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user.get("language", "uz")
    
    if loc == t(lang, "btn_uzb"):
        await update_user_demographics(user_id, location="O'zbekiston")
        await state.set_state(RegistrationStates.waiting_for_region)
        
        regions = ["Toshkent shahri", "Toshkent viloyati", "Andijon", "Buxoro", "Farg'ona", "Jizzax", "Xorazm", "Namangan", "Navoiy", "Qashqadaryo", "Qoraqalpog'iston", "Samarqand", "Sirdaryo", "Surxondaryo"]
        kb_buttons = []
        for i in range(0, len(regions), 2):
            row = [KeyboardButton(text=regions[i])]
            if i+1 < len(regions): row.append(KeyboardButton(text=regions[i+1]))
            kb_buttons.append(row)
            
        keyboard = ReplyKeyboardMarkup(keyboard=kb_buttons, resize_keyboard=True, one_time_keyboard=True)
        await message.answer(t(lang, "ask_region"), reply_markup=keyboard)
    else:
        await state.set_state(RegistrationStates.waiting_for_country)
        await message.answer(t(lang, "ask_country_name"), reply_markup=ReplyKeyboardRemove())


# ═══════════════════════════════════════
# VILOYAT QABUL QILISH (UZB)
# ═══════════════════════════════════════
@router.message(RegistrationStates.waiting_for_region, F.text)
async def process_region(message: Message, state: FSMContext):
    region = message.text.strip()
    if region.startswith("/"): return
    
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user.get("language", "uz")
    name = user.get("full_name", "")
    
    await update_user_demographics(user_id, region=region)
    await state.set_state(RegistrationStates.waiting_for_contact)
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "share_contact_btn"), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(t(lang, "ask_contact", name=name), reply_markup=keyboard)


# ═══════════════════════════════════════
# DAVLAT QABUL QILISH (BOSHQA DAVLAT)
# ═══════════════════════════════════════
@router.message(RegistrationStates.waiting_for_country, F.text)
async def process_country(message: Message, state: FSMContext):
    country = message.text.strip()
    if country.startswith("/"): return
    
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user.get("language", "uz")
    name = user.get("full_name", "")
    
    await update_user_demographics(user_id, location=country, region="N/A")
    await state.set_state(RegistrationStates.waiting_for_contact)
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "share_contact_btn"), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(t(lang, "ask_contact", name=name), reply_markup=keyboard)


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
    
    # Referral tracking
    data = await state.get_data()
    referrer_id = data.get("referrer_id")
    if referrer_id:
        from src.database import track_referral, referrals_collection
        success = await track_referral(referrer_id, user_id)
        if success:
            try:
                from src.bot import bot
                stats = await referrals_collection.count_documents({"referrer_id": referrer_id})
                await bot.send_message(
                    chat_id=referrer_id,
                    text=f"🎉 Do'stingiz Somly AI ga qo'shildi!\nEndi siz {stats} kishini taklif qildingiz 👍"
                )
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Failed to notify referrer {referrer_id}: {e}")

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
