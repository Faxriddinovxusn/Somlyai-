"""
Anti-Spam & Rate Limiting Middleware.
Protects the bot from flood, limits messages per user, handles Blacklist,
and forces unregistered users to use /start.
"""

import time
import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.fsm.context import FSMContext

from src.database import get_user
from src.services.error_handler import handle_error, ErrorType

logger = logging.getLogger(__name__)

# Structure: 
# {
#   user_id: {
#       "msgs": [ts1, ts2, ...],
#       "voices": [ts1, ts2, ...],
#       "last_1m_warn": 0.0,
#       "last_1h_warn": 0.0,
#   }
# }
user_activity = {}

# Limits for messages
MSG_1S_LIMIT = 2
MSG_1M_LIMIT = 30
MSG_1H_LIMIT = 200

# Limits for voices
VOICE_1M_LIMIT = 10
VOICE_1H_LIMIT = 50


def clean_old_timestamps(ts_list, now, max_age=3600):
    """Remove timestamps older than max_age."""
    return [ts for ts in ts_list if now - ts <= max_age]


class AntiSpamMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        bot: Bot = data.get("bot")

        # Only check Message and CallbackQuery
        if isinstance(event, Message):
            user = event.from_user
            is_voice = bool(event.voice)
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            is_voice = False
        else:
            return await handler(event, data)

        if not user:
            return await handler(event, data)

        user_id = user.id
        now = time.time()

        # Initialize user activity tracker
        if user_id not in user_activity:
            user_activity[user_id] = {
                "msgs": [],
                "voices": [],
                "last_1m_warn": 0.0,
                "last_1h_warn": 0.0,
            }

        activity = user_activity[user_id]

        # Fetch user from DB
        db_user = await get_user(user_id)

        # ════════════════════════════════════════════
        # 1. BLACKLIST CHECK
        # ════════════════════════════════════════════
        if db_user and db_user.get("is_blacklisted"):
            logger.info(f"Blacklisted user {user_id} tried to send a message. Ignored.")
            return

        # ════════════════════════════════════════════
        # 2. NEW USER CHECK
        # ════════════════════════════════════════════
        is_registered = db_user and db_user.get("registration_complete")
        state: FSMContext = data.get("state")
        current_state = await state.get_state() if state else None

        # Allow /start always, allow callbacks if in registration, allow contact sending, allow language selection
        is_start_cmd = isinstance(event, Message) and event.text and event.text.startswith("/start")
        is_lang_callback = isinstance(event, CallbackQuery) and event.data and event.data.startswith("lang_")
        is_in_fsm = current_state is not None
        
        if not is_registered and not is_start_cmd and not is_in_fsm and not is_lang_callback:
            # Tell user to press /start
            if isinstance(event, Message):
                await event.answer("Davom etish uchun /start bosing.")
            elif isinstance(event, CallbackQuery):
                await event.answer("Davom etish uchun /start bosing.", show_alert=True)
            return

        # ════════════════════════════════════════════
        # 3. RATE LIMITING
        # ════════════════════════════════════════════
        # Clean old timestamps
        activity["msgs"] = clean_old_timestamps(activity["msgs"], now, 3600)
        activity["voices"] = clean_old_timestamps(activity["voices"], now, 3600)

        # Count occurrences
        msgs_1s = len([t for t in activity["msgs"] if now - t <= 1])
        msgs_1m = len([t for t in activity["msgs"] if now - t <= 60])
        msgs_1h = len(activity["msgs"])

        voices_1m = len([t for t in activity["voices"] if now - t <= 60])
        voices_1h = len(activity["voices"])

        # Record this event
        activity["msgs"].append(now)
        if is_voice:
            activity["voices"].append(now)

        # ----- 1 HOUR LIMIT -----
        if msgs_1h >= MSG_1H_LIMIT or (is_voice and voices_1h >= VOICE_1H_LIMIT):
            if now - activity["last_1h_warn"] > 3600:
                activity["last_1h_warn"] = now
                if isinstance(event, Message):
                    await event.answer("🚫 Bugungi limitga yetdingiz. Bir soatdan keyin davom eting.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("🚫 Bugungi limitga yetdingiz.", show_alert=True)
                
                # Alert Admin
                await handle_error(bot, ErrorType.TELEGRAM_GENERAL, f"User {user_id} hit the 1-hour spam limit ({msgs_1h} msgs, {voices_1h} voices).", user_id)
            return  # Block

        # ----- 1 MINUTE LIMIT -----
        if msgs_1m >= MSG_1M_LIMIT or (is_voice and voices_1m >= VOICE_1M_LIMIT):
            if now - activity["last_1m_warn"] > 60:
                activity["last_1m_warn"] = now
                if isinstance(event, Message):
                    await event.answer("⏳ Bir oz sekinroq! 30 soniyadan keyin davom eting.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("⏳ Bir oz sekinroq! 30 soniyadan keyin davom eting.", show_alert=True)
            return  # Block

        # ----- 1 SECOND LIMIT -----
        if msgs_1s >= MSG_1S_LIMIT:
            # Silent ignore
            logger.warning(f"User {user_id} hit 1s limit. Ignored.")
            return  # Block

        # Pass to the next middleware/handler
        return await handler(event, data)
