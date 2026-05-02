"""
Mandatory Channel Subscription Middleware.
Intercepts all messages/callbacks and checks subscription.
After subscription is verified, redirects to registration if not complete.
"""

import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, CallbackQuery, TelegramObject, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from src.database import get_all_channels, get_user
from src.states import RegistrationStates

logger = logging.getLogger(__name__)


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        bot: Bot = data.get("bot")

        # Get user info
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        else:
            return await handler(event, data)

        if not user:
            return await handler(event, data)

        user_id = user.id

        # ════════════════════════════════════════════
        # BYPASS — hech qachon tekshirmaslik kerak bo'lgan holatlar
        # ════════════════════════════════════════════
        if isinstance(event, Message):
            # /start, /language buyruqlari
            if event.text and (event.text.startswith("/start") or event.text.startswith("/language")):
                return await handler(event, data)
            # Contact (registration davomida)
            if event.contact:
                return await handler(event, data)
        elif isinstance(event, CallbackQuery):
            # Til tanlash callback'lari
            if event.data and event.data.startswith("lang_"):
                return await handler(event, data)

        # ════════════════════════════════════════════
        # FSM state tekshiruvi — agar registration davomida bo'lsa, o'tkazib yuborish
        # ════════════════════════════════════════════
        state: FSMContext = data.get("state")
        if state:
            current_state = await state.get_state()
            if current_state and current_state in [
                RegistrationStates.waiting_for_name.state,
                RegistrationStates.waiting_for_contact.state,
            ]:
                return await handler(event, data)

        # ════════════════════════════════════════════
        # USER TILINI OLISH
        # ════════════════════════════════════════════
        db_user = await get_user(user_id)
        lang = db_user.get("language", "uz") if db_user else "uz"

        # ════════════════════════════════════════════
        # KANAL OBUNASI TEKSHIRUVI
        # ════════════════════════════════════════════
        if db_user and db_user.get("channels_joined"):
            # Registration tekshiruvi (kanal obunasidan keyin)
            if not db_user.get("registration_complete"):
                return await self._redirect_to_registration(event, data, lang, state)
            return await handler(event, data)

        channels = await get_all_channels()
        if not channels:
            # Kanallar yo'q — registration tekshiruvi
            if db_user and not db_user.get("registration_complete"):
                return await self._redirect_to_registration(event, data, lang, state)
            return await handler(event, data)

        not_subscribed = []
        for ch in channels:
            link = ch["link"]
            chat_identifier = link
            if "t.me/" in link and "+" not in link:
                username = link.split("t.me/")[1].split("/")[0]
                chat_identifier = f"@{username}"

            try:
                member = await bot.get_chat_member(chat_id=chat_identifier, user_id=user_id)
                if member.status in ["left", "kicked", "restricted"]:
                    not_subscribed.append(ch)
            except Exception as e:
                logger.warning(f"Sub check failed for {chat_identifier}: {e}")
                # Agar tekshirib bo'lmasa, skip qilamiz (bot admin emas bo'lishi mumkin)
                pass

        if not_subscribed:
            return await self._show_subscription_required(event, not_subscribed, lang)

        # ════════════════════════════════════════════
        # OBUNA TEKSHIRUVI MUVAFFAQIYATLI — check_sub callback
        # ════════════════════════════════════════════
        if isinstance(event, CallbackQuery) and event.data == "check_sub":
            await event.message.delete()
            
            # DB da saqlash
            from src.database import update_user_channels_joined
            await update_user_channels_joined(user_id, True)

            # Registration tekshiruvi
            if db_user and not db_user.get("registration_complete"):
                return await self._redirect_to_registration(event, data, lang, state)

            from src.handlers.menu_handler import get_main_keyboard
            kbd = await get_main_keyboard()
            succ = {
                "uz": "Rahmat! 🎉 Botdan to'liq foydalanishingiz mumkin!",
                "en": "Thank you! 🎉 You can now use the bot!",
                "ru": "Спасибо! 🎉 Теперь вы можете использовать бота!",
            }
            await event.message.answer(succ.get(lang, succ["uz"]), reply_markup=kbd)
            await event.answer()
            return

        # ════════════════════════════════════════════
        # REGISTRATION TEKSHIRUVI (kanal obunasidan keyin)
        # ════════════════════════════════════════════
        if db_user and not db_user.get("registration_complete"):
            return await self._redirect_to_registration(event, data, lang, state)

        return await handler(event, data)

    async def _show_subscription_required(self, event, not_subscribed, lang):
        """Obuna bo'lmagan kanallarga tugma chiqarish."""
        buttons = []
        for ch in not_subscribed:
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
        for i, ch in enumerate(not_subscribed, 1):
            text += f"{i}️⃣ {ch['name']}\n"

        if isinstance(event, Message):
            await event.answer(text, reply_markup=keyboard)
        elif isinstance(event, CallbackQuery):
            if event.data == "check_sub":
                await event.message.answer(text, reply_markup=keyboard)
                alert = {
                    "uz": "Hali to'liq obuna bo'lmadingiz!",
                    "en": "You haven't subscribed to all channels!",
                    "ru": "Вы ещё не подписались на все каналы!",
                }
                await event.answer(alert.get(lang, alert["uz"]), show_alert=True)
            else:
                await event.answer("⚠️", show_alert=False)

    async def _redirect_to_registration(self, event, data, lang, state):
        """Ro'yxatdan o'tishga yo'naltirish."""
        ask_name = {
            "uz": "🤝 Keling tanishib olamiz!\n\nTo'liq ismingizni kiriting (matn yoki ovozli):",
            "en": "🤝 Let's get to know each other!\n\nPlease enter your full name (text or voice):",
            "ru": "🤝 Давайте познакомимся!\n\nВведите ваше полное имя (текст или голосовое):",
        }
        if state:
            await state.set_state(RegistrationStates.waiting_for_name)

        if isinstance(event, Message):
            await event.answer(ask_name.get(lang, ask_name["uz"]))
        elif isinstance(event, CallbackQuery):
            await event.message.answer(ask_name.get(lang, ask_name["uz"]))
            await event.answer()
