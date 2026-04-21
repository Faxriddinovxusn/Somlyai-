from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from src.database import get_webapp_url

router = Router()

async def get_main_keyboard() -> ReplyKeyboardMarkup:
    url = await get_webapp_url()
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📊 Mening hisobim", web_app=WebAppInfo(url=url)),
                KeyboardButton(text="➕ Qo'shish")
            ]
        ],
        resize_keyboard=True,
        persistent=True
    )
    return keyboard

@router.message(F.text == "➕ Qo'shish")
async def process_add_button(message: Message):
    text = (
        "Xarajat, daromad yoki qarzni yozing yoki ovoz yuboring:\n\n"
        "💸 'Taksiga 15,000 so'm'\n"
        "💰 'Oylik 4 million tushdi'\n"
        "🤝 'Jasurga 100 ming berdim'\n"
        "🎤 Mikrofon orqali ham ayta olasiz"
    )
    # Re-send the keyboard just in case they lost it
    kbd = await get_main_keyboard()
    await message.answer(text, reply_markup=kbd)

@router.message(F.text == "📊 Mening hisobim")
async def process_my_account_button(message: Message):
    # This might only trigger on old clients or desktop clients that don't support web_app buttons
    # or if the web_app property wasn't set correctly.
    url = await get_webapp_url()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kbd = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ochish", web_app=WebAppInfo(url=url))]
    ])
    await message.answer("Mini Appni ochish uchun pastdagi tugmani bosing:", reply_markup=kbd)
