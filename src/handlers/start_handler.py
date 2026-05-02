"""
Start, Language & Help handler.

Flow:
1. /start → If new user: language selection → welcome → channels → registration
2. /start → If existing user: welcome back message
3. /language → Change language anytime
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

    # Agar eski user bo'lsa va ro'yxatdan o'tgan bo'lsa
    if user.get("registration_complete"):
        from src.handlers.menu_handler import get_main_keyboard
        kbd = await get_main_keyboard()
        lang = user.get("language", "uz")
        name = user.get("full_name", "")
        text = t(lang, "welcome_back", name=name)
        text += "\n\n" + t(lang, "commands")
        await message.answer(text, reply_markup=kbd)
        
        # Admin uchun to'liq buyruqlar paneli
        if await is_admin(user_id):
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

    # Yangi user — til tanlash
    lang = user.get("language", "uz")
    await message.answer(
        t(lang, "choose_lang"),
        reply_markup=get_language_keyboard()
    )


# ═══════════════════════════════════════
# /language
# ═══════════════════════════════════════
@router.message(Command("language"))
async def language_command(message: Message):
    user = await get_user(message.from_user.id)
    lang = user.get("language", "uz")
    await message.answer(
        t(lang, "choose_lang"),
        reply_markup=get_language_keyboard()
    )


# ═══════════════════════════════════════
# Til tanlash callback
# ═══════════════════════════════════════
@router.callback_query(lambda c: c.data and c.data.startswith("lang_"))
async def process_language_selection(callback_query: CallbackQuery, state: FSMContext):
    lang_code = callback_query.data.split("_")[1]  # uz, en, ru
    user_id = callback_query.from_user.id
    user = await get_user(user_id)

    await update_user_language(user_id, lang_code)
    await callback_query.message.delete()

    # Agar allaqachon ro'yxatdan o'tgan user til o'zgartirsa
    if user.get("registration_complete"):
        from src.handlers.menu_handler import get_main_keyboard
        kbd = await get_main_keyboard()
        lang_msg = t(lang_code, "lang_changed")
        await callback_query.message.answer(lang_msg, reply_markup=kbd)
        await callback_query.answer()
        return

    # Yangi user — xush kelibsiz xabarini yuborish
    await callback_query.message.answer(
        t(lang_code, "welcome_new"),
        parse_mode="HTML"
    )

    # Keyin kanallarni tekshirish uchun oddiy xabar yuboramiz
    # (Middleware bu xabarni ushlab, kanal obunasini tekshiradi)
    # Agar kanal yo'q bo'lsa → to'g'ridan-to'g'ri ism so'rashga o'tadi
    from src.database import get_all_channels
    channels = await get_all_channels()

    if not channels:
        # Kanallar yo'q — to'g'ridan-to'g'ri ism so'rash
        await state.set_state(RegistrationStates.waiting_for_name)
        await callback_query.message.answer(t(lang_code, "ask_name"))
    else:
        # Kanallar bor — middleware ularni ko'rsatadi
        # Shu paytga qadar state'ni saqlab qo'yamiz
        await state.update_data(needs_registration=True)

    await callback_query.answer()



