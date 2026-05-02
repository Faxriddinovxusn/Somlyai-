import asyncio
from datetime import datetime
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.database import reminders_collection, update_reminder_status
from src.bot import bot
from src.handlers.start_handler import t
from src.database import get_user

logger = logging.getLogger(__name__)

async def check_and_send_reminders():
    """
    Checks the reminders collection for pending reminders whose remind_at <= now.
    Sends them to the user and updates their status to 'sent'.
    """
    now = datetime.utcnow()
    try:
        # Find pending reminders that are due
        cursor = reminders_collection.find({
            "status": "pending",
            "remind_at": {"$lte": now}
        })
        reminders = await cursor.to_list(length=50)
        
        for rem in reminders:
            user_id = rem.get("user_id")
            message = rem.get("message", "Eslatma!")
            reminder_id = str(rem["_id"])
            
            user = await get_user(user_id)
            lang = user.get("language", "uz") if user else "uz"
            
            text = f"⏰ <b>Eslatma:</b>\n\n{message}"
            
            # Send message to user
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=text,
                    parse_mode="HTML"
                )
                # Mark as sent
                await update_reminder_status(reminder_id, "sent")
                logger.info(f"Sent reminder {reminder_id} to user {user_id}")
            except Exception as e:
                logger.error(f"Failed to send reminder {reminder_id} to user {user_id}: {e}")
                
    except Exception as e:
        logger.error(f"Error in check_and_send_reminders: {e}")

# Initialize scheduler
scheduler = AsyncIOScheduler()

def setup_scheduler():
    """Adds jobs and starts the scheduler."""
    scheduler.add_job(check_and_send_reminders, 'interval', minutes=1)
    scheduler.start()
    logger.info("Background scheduler started.")
