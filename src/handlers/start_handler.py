"""
Start, Language & Help handler.

Flow:
1. /start → If new user: language selection → welcome → channels → registration
2. /start → If existing user: welcome back message
3. /language → Change language anytime
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from src.database import get_user, is_admin, update_user_language
from src.states import RegistrationStates

router = Router()

# ═══════════════════════════════════════
# TRANSLATIONS
# ═══════════════════════════════════════
TEXTS = {
    "uz": {
        "welcome_new": (
            "✨ Assalomu aleykum!\n\n"
            "Men <b>Somly AI</b> man — sizning shaxsiy moliya yordamchingiz 💰\n\n"
            "Meni ishlatish pullik bo'lishi mumkin edi, lekin @XusniddinWR tomonidan "
            "men <b>bepul</b> qilindim! 🎉\n\n"
            "🔒 Sizning ma'lumotlaringiz bizda saqlanmaydi!\n\n"
            "Sizdan shunchaki bot talab qiladigan kanallarga obuna bo'lish talab etiladi.\n\n"
            "Ishlaringizga omad! 💪"
        ),
        "welcome_back": "👋 Qaytganingiz bilan, {name}! Bugun nimalarga xarajat qildingiz?",
        "ask_name": "🤝 Keling tanishib olamiz!\n\nIsmingizni kiriting (matn yoki ovozli):",
        "ask_contact": (
            "{name}, keling ro'yxatdan o'tib olamiz! 📱\n\n"
            "Raqamingizni pastdagi tugma orqali yuboring 👇"
        ),
        "contact_required": "📱 Ro'yxatdan o'tish uchun raqamingizni pastdagi tugma orqali yuboring!",
        "share_contact_btn": "📱 Raqamni yuborish",
        "registration_done": (
            "✅ Ajoyib, {name}! Ro'yxatdan o'tdingiz!\n\n"
            "Endi quyidagi xarajatni audio yoki matn ko'rinishida yuboring:\n\n"
            "Masalan: \"Fastfoodga 15,000 so'm xarajat qildim\" 💸"
        ),
        "commands": (
            "📌 Buyruqlar:\n"
            "/setlimit — Oylik limit\n"
            "/excel — Hisobot yuklash\n"
            "/language — Tilni o'zgartirish\n"
            "/help — Yordam"
        ),
    },
    "en": {
        "welcome_new": (
            "✨ Hello!\n\n"
            "I am <b>Somly AI</b> — your personal finance assistant 💰\n\n"
            "Using me could have been paid, but @XusniddinWR made me "
            "<b>free</b>! 🎉\n\n"
            "🔒 Your data is not stored with us!\n\n"
            "You just need to subscribe to the required channels.\n\n"
            "Good luck! 💪"
        ),
        "welcome_back": "👋 Welcome back, {name}! What did you spend today?",
        "ask_name": "🤝 Let's get to know each other!\n\nPlease enter your name (text or voice):",
        "ask_contact": (
            "{name}, let's complete registration! 📱\n\n"
            "Share your phone number using the button below 👇"
        ),
        "contact_required": "📱 To register, please share your phone number using the button below!",
        "share_contact_btn": "📱 Share phone number",
        "registration_done": (
            "✅ Great, {name}! You're registered!\n\n"
            "Now send your expense as text or audio:\n\n"
            "Example: \"Spent 15,000 on fast food\" 💸"
        ),
        "commands": (
            "📌 Commands:\n"
            "/setlimit — Monthly limit\n"
            "/excel — Download report\n"
            "/language — Change language\n"
            "/help — Help"
        ),
    },
    "ru": {
        "welcome_new": (
            "✨ Здравствуйте!\n\n"
            "Я <b>Somly AI</b> — ваш личный финансовый помощник 💰\n\n"
            "Мое использование могло быть платным, но @XusniddinWR сделал меня "
            "<b>бесплатным</b>! 🎉\n\n"
            "🔒 Ваши данные у нас не хранятся!\n\n"
            "От вас требуется лишь подписка на каналы бота.\n\n"
            "Удачи! 💪"
        ),
        "welcome_back": "👋 С возвращением, {name}! На что вы сегодня потратились?",
        "ask_name": "🤝 Давайте познакомимся!\n\nВведите ваше имя (текст или голосовое):",
        "ask_contact": (
            "{name}, давайте завершим регистрацию! 📱\n\n"
            "Отправьте свой номер телефона кнопкой ниже 👇"
        ),
        "contact_required": "📱 Для регистрации отправьте номер телефона кнопкой ниже!",
        "share_contact_btn": "📱 Отправить номер",
        "registration_done": (
            "✅ Отлично, {name}! Вы зарегистрированы!\n\n"
            "Теперь отправьте расход текстом или голосом:\n\n"
            "Например: \"Потратил 15 000 на фастфуд\" 💸"
        ),
        "commands": (
            "📌 Команды:\n"
            "/setlimit — Ежемесячный лимит\n"
            "/excel — Скачать отчет\n"
            "/language — Изменить язык\n"
            "/help — Помощь"
        ),
    },
}

def t(lang: str, key: str, **kwargs) -> str:
    text = TEXTS.get(lang, TEXTS["uz"]).get(key, TEXTS["uz"][key])
    if kwargs:
        text = text.format(**kwargs)
    return text


def get_language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")]
    ])


# ═══════════════════════════════════════
# /start
# ═══════════════════════════════════════
@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_user(user_id)

    # Agar eski user bo'lsa va ro'yxatdan o'tgan bo'lsa
    if user.get("registration_complete"):
        from src.handlers.menu_handler import get_main_keyboard
        kbd = await get_main_keyboard()
        lang = user.get("language", "uz")
        name = user.get("full_name", "")
        text = t(lang, "welcome_back", name=name)
        text += "\n\n" + t(lang, "commands")
        if await is_admin(user_id):
            text += "\n\n🛠 ADMIN: /stats, /add_channel, /remove_channel, /admin, /remove_admin, /send, /setwebapp"
        await message.answer(text, reply_markup=kbd)
        return

    # Yangi user — til tanlash
    await message.answer(
        "🌍 Iltimos, tilni tanlang:\n"
        "Please select your language:\n"
        "Пожалуйста, выберите язык:",
        reply_markup=get_language_keyboard()
    )


# ═══════════════════════════════════════
# /language
# ═══════════════════════════════════════
@router.message(Command("language"))
async def language_command(message: Message):
    await message.answer(
        "🌍 Tilni tanlang / Select language / Выберите язык:",
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
        lang_msg = {
            "uz": "✅ Til o'zgartirildi",
            "en": "✅ Language changed",
            "ru": "✅ Язык изменен"
        }
        await callback_query.message.answer(lang_msg.get(lang_code, "✅ Til o'zgartirildi"), reply_markup=kbd)
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


# ═══════════════════════════════════════
# /help
# ═══════════════════════════════════════
@router.message(Command("help"))
async def help_command(message: Message):
    user_id = message.from_user.id
    user = await get_user(user_id)
    lang = user.get("language", "uz")

    if lang == "en":
        help_text = (
            "📚 Somly AI Help\n\n"
            "━━━━━━━━━━━━━━━━\n"
            "💬 SEND A MESSAGE:\n"
            "Write any financial message — AI analyzes it automatically.\n\n"
            "Examples:\n"
            "  💸 «Spent 45k on food»\n"
            "  💰 «Received 4M salary»\n"
            "  🤝 «Lent 100k to Jasur»\n"
            "  🎤 You can also send voice messages\n\n"
            + t(lang, "commands")
        )
    elif lang == "ru":
        help_text = (
            "📚 Помощь Somly AI\n\n"
            "━━━━━━━━━━━━━━━━\n"
            "💬 ОТПРАВЬТЕ СООБЩЕНИЕ:\n"
            "Напишите любое финансовое сообщение — ИИ проанализирует автоматически.\n\n"
            "Примеры:\n"
            "  💸 «Потратил 45 тысяч на еду»\n"
            "  💰 «Получил зарплату 4 млн»\n"
            "  🤝 «Дал в долг 100 тысяч Жасуру»\n"
            "  🎤 Можно отправить голосовое сообщение\n\n"
            + t(lang, "commands")
        )
    else:
        help_text = (
            "📚 Somly AI Yordam\n\n"
            "━━━━━━━━━━━━━━━━\n"
            "💬 XABAR YUBORING:\n"
            "Istalgan moliyaviy xabar yozing — AI uni tahlil qiladi.\n\n"
            "Misollar:\n"
            "  💸 «Ovqatga 45 ming berdim»\n"
            "  💰 «Oylik 4 mln tushdi»\n"
            "  🤝 «Jasurga 100 ming qarz berdim»\n"
            "  🎤 Ovozli xabar yuborishingiz mumkin\n\n"
            + t(lang, "commands")
        )

    if await is_admin(user_id):
        help_text += "\n\n🛠 ADMIN: /stats, /add_channel, /remove_channel, /admin, /remove_admin, /send, /setwebapp"

    await message.answer(help_text)
