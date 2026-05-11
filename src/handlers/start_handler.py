"""
Start, Language & Help handler.

Onboarding Flow (PROMPT 1):
1. /start → If new user: language selection
2. Language selected → welcome message
3. Ask name → detect gender via AI
4. Ask phone → save contact
5. Channel subscription check
6. First transaction prompt
7. /start → If existing user: "Xush kelibsiz qaytib!"
"""

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from src.database import get_user, is_admin, update_user_language
from src.states import RegistrationStates
from src.services.i18n import t

router = Router()


def get_language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
        ]
    ])


# ═══════════════════════════════════════
# /start
# ═══════════════════════════════════════
@router.message(Command("start"))
async def start_command(message: Message, command: CommandObject, state: FSMContext):
    user_id = message.from_user.id
    user = await get_user(user_id)
    
    # Referral code handling
    if command.args and command.args.startswith("ref_"):
        try:
            referrer_id = int(command.args.split("_")[1])
            if referrer_id != user_id:
                await state.update_data(referrer_id=referrer_id)
        except (ValueError, IndexError):
            pass

    # ════════════════════════════════════════════
    # ADMIN AUTO-REGISTER — Admin hech qachon oddiy user oqimiga tushmaydi
    # ════════════════════════════════════════════
    from src.config import ADMIN_ID
    if str(user_id) == str(ADMIN_ID):
        if not user or not user.get("registration_complete"):
            # Admin bazada yo'q yoki registration tugamagan — avtomatik yaratish
            from src.database import users_collection
            from datetime import datetime
            admin_data = {
                "telegram_id": user_id,
                "full_name": message.from_user.full_name or "Admin",
                "username": message.from_user.username or "",
                "language": "uz",
                "registration_complete": True,
                "is_admin": True,
                "is_active": True,
                "created_at": datetime.utcnow(),
            }
            await users_collection.update_one(
                {"telegram_id": user_id},
                {"$set": admin_data},
                upsert=True
            )
            user = await get_user(user_id)

        # Admin uchun to'g'ridan-to'g'ri admin panelni ko'rsatish
        lang = user.get("language", "uz")
        name = user.get("full_name", "Admin")

        try:
            from src.handlers.menu_handler import get_main_keyboard
            kbd = await get_main_keyboard(lang)
            await message.answer(
                f"👋 Xush kelibsiz, <b>{name}</b>!\n\n"
                f"🛡 Siz <b>Admin</b> sifatida tizimga kirdingiz.",
                reply_markup=kbd, parse_mode="HTML"
            )
        except Exception:
            # WebApp URL noto'g'ri — keyboard siz yuboramiz
            await message.answer(
                f"👋 Xush kelibsiz, <b>{name}</b>!\n\n"
                f"🛡 Siz <b>Admin</b> sifatida tizimga kirdingiz.\n\n"
                f"⚠️ Mini App URL o'rnatilmagan. <code>/setwebapp https://NGROK_URL</code> yuboring.",
                parse_mode="HTML"
            )

        admin_text = (
            "🛠 <b>ADMIN PANEL — Barcha buyruqlar:</b>\n\n"
            
            "📊 <b>Statistika va Monitoring:</b>\n"
            "├ /stats — Bot statistikasi (foydalanuvchilar, tranzaksiyalar)\n"
            "├ /user [id] — Foydalanuvchi ma'lumotlari\n"
            "└ /web — Admin veb-panel kirish ma'lumotlari\n\n"
            
            "👥 <b>Foydalanuvchi boshqaruvi:</b>\n"
            "├ /admin [id] — Yangi admin qo'shish\n"
            "├ /remove_admin [id] — Adminlikdan o'chirish\n"
            "├ /ban [id] — Qora ro'yxatga kiritish\n"
            "└ /unban [id] — Qora ro'yxatdan chiqarish\n\n"
            
            "📢 <b>Kanallar boshqaruvi:</b>\n"
            "├ /channels — Barcha kanallar ro'yxati\n"
            "├ /add_channel — Yangi kanal qo'shish\n"
            "├ /change_channel — Kanalni o'zgartirish\n"
            "├ /setchannel [#] [@link] — Tezkor o'zgartirish\n"
            "└ /remove_channel [link] — Kanalni o'chirish\n\n"
            
            "📣 <b>Xabar tarqatish:</b>\n"
            "└ /send — Barcha foydalanuvchilarga xabar yuborish\n\n"
            
            "🌐 <b>Web App:</b>\n"
            "└ /setwebapp [link] — Mini App URL o'rnatish\n\n"
            
            "🧠 <b>AI Bilimlar bazasi:</b>\n"
            "├ /teach [mavzu]: [matn] — Yangi bilim qo'shish\n"
            "├ /knowledge — Barcha bilimlar ro'yxati\n"
            "├ /editteach [mavzu]: [matn] — Bilimni tahrirlash\n"
            "└ /unteach [mavzu] — Bilimni o'chirish (arxivlash)\n\n"
            
            "🔧 <b>Tizim:</b>\n"
            "└ /language — Tilni o'zgartirish"
        )
        await message.answer(admin_text, parse_mode="HTML")
        return

    # ════════════════════════════════════════════
    # QAYTA /start — Allaqachon ro'yxatdan o'tgan user
    # ════════════════════════════════════════════
    if user and user.get("registration_complete"):
        lang = user.get("language", "uz")
        name = user.get("full_name", "")
        
        # "Siz allaqachon ro'yxatdansiz! Xush kelibsiz qaytib! 😊 [Ism]"
        text = t(lang, "welcome_back", name=name)
        
        try:
            from src.handlers.menu_handler import get_main_keyboard
            kbd = await get_main_keyboard(lang)
            await message.answer(text, reply_markup=kbd)
        except Exception:
            await message.answer(text)
        return

    # ════════════════════════════════════════════
    # YANGI USER — 1-QADAM: TIL TANLASH
    # "🌐 Tilni tanlang / Choose your language / Выберите язык"
    # ════════════════════════════════════════════
    await message.answer(
        t("uz", "choose_lang"),
        reply_markup=get_language_keyboard()
    )


# ═══════════════════════════════════════
# /language — Tilni o'zgartirish
# ═══════════════════════════════════════
@router.message(Command("language"))
async def language_command(message: Message):
    await message.answer(
        t("uz", "choose_lang"),
        reply_markup=get_language_keyboard()
    )


# ═══════════════════════════════════════
# TIL TANLASH CALLBACK
# 2-QADAM: XUSH KELIBSIZ XABARI → 3-QADAM: ISM SO'RASH
# ═══════════════════════════════════════
@router.callback_query(lambda c: c.data and c.data.startswith("lang_"))
async def process_language_selection(callback_query: CallbackQuery, state: FSMContext):
    lang_code = callback_query.data.split("_")[1]  # uz, en, ru
    user_id = callback_query.from_user.id
    user = await get_user(user_id)

    await update_user_language(user_id, lang_code)
    await callback_query.message.delete()

    # ════════════════════════════════════════════
    # Agar allaqachon ro'yxatdan o'tgan user til o'zgartirsa
    # ════════════════════════════════════════════
    if user.get("registration_complete"):
        from src.handlers.menu_handler import get_main_keyboard
        kbd = await get_main_keyboard(lang_code)
        lang_msg = t(lang_code, "lang_changed")
        await callback_query.message.answer(lang_msg, reply_markup=kbd)
        await callback_query.answer()
        return

    # ════════════════════════════════════════════
    # 2-QADAM: XUSH KELIBSIZ XABARI
    # ════════════════════════════════════════════
    await callback_query.message.answer(t(lang_code, "welcome_new"))

    # ════════════════════════════════════════════
    # 3-QADAM: ISM SO'RASH
    # ════════════════════════════════════════════
    await state.set_state(RegistrationStates.waiting_for_name)
    await callback_query.message.answer(t(lang_code, "ask_name"))

    await callback_query.answer()


