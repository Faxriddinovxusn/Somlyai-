"""
Somly AI Bot — main entry point.

Wires together:
- start_handler       (/start, /help, /language + lang_ callbacks)
- registration_handler (FSM: name + contact collection)
- admin_handler       (/stats, /admin, /add_channel, /send)
- export_handler      (/excel)
- balance_handler     (/balance, /newbalance, /setlimit, /cancel + FSM)
- debt_handler        (/debts + callback queries + FSM)
- voice_handler       (voice messages → Whisper → text pipeline)
- message_handler     (text messages → AI → transaction pipeline) ← LAST (catch-all)
- scheduler           (daily/monthly reminders + dynamic one-time reminders)
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from src.config import BOT_TOKEN
from src.handlers import (
    start_handler,
    registration_handler,
    limit_handler,
    menu_handler,
    voice_handler,
    message_handler,
    admin_handler,
    export_handler,
)
from src.middlewares.subscription import SubscriptionMiddleware
from src.services.scheduler import setup_scheduler
from src.api import start_api_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # ── Register middleware ──
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())

    # ── Register routers ──
    # Order matters! Command routers first, then FSM routers,
    # then voice, then text (catch-all) last.
    dp.include_router(admin_handler.router)         # /stats, /admin, /add_channel, /send
    dp.include_router(start_handler.router)         # /start, /help, /language + lang_ callbacks
    dp.include_router(registration_handler.router)  # FSM: name + contact
    dp.include_router(export_handler.router)        # /excel
    dp.include_router(limit_handler.router)         # /setlimit
    dp.include_router(menu_handler.router)          # main reply keyboard menus
    dp.include_router(voice_handler.router)         # voice messages
    dp.include_router(message_handler.router)       # text messages (catch-all — MUST be last)

    # ── Start scheduler ──
    setup_scheduler(bot)

    # ── Start API Server ──
    await start_api_server()

    # ── Start polling ──
    logger.info("🚀 Somly AI Bot ishga tushdi!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
