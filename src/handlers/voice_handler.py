"""
Voice handler.
Routes voice messages:
- If in registration (waiting_for_name) → handled by registration_handler
- If in registration (waiting_for_contact) → handled by registration_handler
- Otherwise → transcribe and pass to transaction pipeline
"""

import os
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.services.groq_service import groq_service
from src.handlers.message_handler import handle_transaction_text
from src.states import RegistrationStates

router = Router()


@router.message(F.voice)
async def process_voice_message(message: Message, bot: Bot, state: FSMContext):
    # ═══════════════════════════════════════
    # Registration state tekshiruvi
    # Agar ism kutayotgan bo'lsa → registration_handler o'zi ushlaydi
    # Bu yerga faqat oddiy (registration bo'lmagan) voice keladi
    # ═══════════════════════════════════════
    current_state = await state.get_state()
    if current_state in [
        RegistrationStates.waiting_for_name.state,
        RegistrationStates.waiting_for_contact.state,
    ]:
        # Bu holatlarda registration_handler.py o'zi ushlaydi
        # (chunki u avvalroq router'da turadi)
        return

    user_id = message.from_user.id

    status_msg = await message.answer("🎤 Ovoz tahlil qilinmoqda...")

    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path

    os.makedirs("temp", exist_ok=True)
    local_path = f"temp/{file_id}.ogg"

    try:
        await bot.download_file(file_path, local_path)

        # Whisper orqali matnga o'girish
        transcribed_text = await groq_service.transcribe_audio_with_retry(local_path)

        # Ovozni matnga o'girdik, darhol oraliq xabarni o'chiramiz
        await status_msg.delete()

        # Tranzaksiya pipeline'ga yuborish
        await handle_transaction_text(message, transcribed_text)

    except Exception as e:
        await status_msg.edit_text("❌ Ovozni tahlil qilishda xatolik. Iltimos qaytadan urinib ko'ring.")
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)
