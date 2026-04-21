"""
Groq AI Service with API key rotation.

Features:
- Multiple API keys rotation on 429 / quota / connection errors
- 30s cooldown when all keys exhausted
- Transaction parsing with enhanced 7-step analysis
- Whisper audio transcription
- Name extraction from voice
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from groq import AsyncGroq, APIStatusError, APITimeoutError, APIConnectionError
from src.config import GROQ_API_KEYS, GROQ_MODEL
from src.categories import get_all_category_names_for_ai

logger = logging.getLogger(__name__)


class GroqService:
    def __init__(self):
        self.keys = GROQ_API_KEYS
        self.current_key_index = 0
        self.clients = [AsyncGroq(api_key=key) for key in self.keys]

    def get_client(self):
        return self.clients[self.current_key_index]

    def next_key(self):
        self.current_key_index = (self.current_key_index + 1) % len(self.keys)
        logger.warning(f"Switched to Groq API Key {self.current_key_index + 1}/{len(self.keys)}")

    async def chat_completion_with_retry(self, messages: List[Dict], max_retries: int = None, **kwargs) -> str:
        if max_retries is None:
            max_retries = len(self.keys) * 2

        attempts = 0
        while attempts < max_retries:
            client = self.get_client()
            try:
                response = await client.chat.completions.create(
                    messages=messages,
                    model=GROQ_MODEL,
                    **kwargs
                )
                return response.choices[0].message.content
            except (APIStatusError, APITimeoutError, APIConnectionError) as e:
                error_str = str(e)
                logger.error(f"Groq API Error (key {self.current_key_index+1}): {error_str}")
                if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower() or "connection" in error_str.lower() or "403" in error_str:
                    self.next_key()
                    attempts += 1
                    if attempts % len(self.keys) == 0:
                        logger.warning("All keys exhausted. Waiting 30s before retry.")
                        await asyncio.sleep(30)
                else:
                    raise e
        raise Exception("Max retries reached for Groq API")

    async def transcribe_audio_with_retry(self, file_path: str, max_retries: int = None) -> str:
        if max_retries is None:
            max_retries = len(self.keys) * 2

        attempts = 0
        while attempts < max_retries:
            client = self.get_client()
            try:
                with open(file_path, "rb") as file:
                    transcription = await client.audio.transcriptions.create(
                        file=(file_path, file.read()),
                        model="whisper-large-v3-turbo",
                        response_format="json",
                        language="uz"
                    )
                return transcription.text
            except (APIStatusError, APITimeoutError, APIConnectionError) as e:
                error_str = str(e)
                logger.error(f"Groq Audio Error (key {self.current_key_index+1}): {error_str}")
                if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower() or "connection" in error_str.lower() or "403" in error_str:
                    self.next_key()
                    attempts += 1
                    if attempts % len(self.keys) == 0:
                        await asyncio.sleep(30)
                else:
                    raise e
        raise Exception("Max retries reached for Groq Audio API")

    # ═══════════════════════════════════════
    # ISMNI AJRATIB OLISH (ovozdan)
    # ═══════════════════════════════════════
    async def extract_name(self, transcribed_text: str) -> str:
        """Ovozdan kelgan matndan faqat ismni ajratib oladi."""
        messages = [
            {"role": "system", "content": (
                "Foydalanuvchi o'z ismini aytdi. Matndan FAQAT ismni ajratib ber. "
                "Agar 'Mening ismim Xusniddin' desa → 'Xusniddin' deb qaytar. "
                "Agar faqat 'Sardor' desa → 'Sardor' deb qaytar. "
                "Hech qanday qo'shimcha so'z, izoh yoki belgi qo'shma. "
                "Faqat ism yozilsin, boshqa hech narsa bo'lmasin."
            )},
            {"role": "user", "content": transcribed_text}
        ]
        try:
            result = await self.chat_completion_with_retry(
                messages, temperature=0.0, max_tokens=50
            )
            # Clean up
            return result.strip().strip('"').strip("'").strip(".")
        except Exception:
            return transcribed_text.strip()

    # ═══════════════════════════════════════
    # ASOSIY TRANZAKSIYA TAHLILI
    # ═══════════════════════════════════════
    async def parse_transaction(self, text: str, current_date_str: str, language: str = "uz", custom_categories: list = None) -> Dict[str, Any]:
        # Kechagi va ertangi sanani hisoblash
        today = datetime.strptime(current_date_str, "%Y-%m-%d")
        yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")
        tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M")

        # Til bo'yicha yo'riqnoma
        lang_map = {"uz": "O'zbek", "en": "English", "ru": "Русский"}
        lang_name = lang_map.get(language, "O'zbek")

        # Kategoriyalar ro'yxatini tayyorlash
        categories_text = get_all_category_names_for_ai(custom_categories)

        system_prompt = f"""Siz moliya botining AI tahlilchisisiz.
BUGUNGI SANA: {current_date_str}
KECHAGI SANA: {yesterday}
ERTANGI SANA: {tomorrow}
HOZIRGI VAQT: {current_time}

JAVOB TILI: {lang_name} — Barcha javoblaringiz FAQAT {lang_name} tilida bo'lishi SHART!

═══ 1. INTENT (niyat) ═══
Foydalanuvchining niyatini ANIQ aniqlang:
- Agar moliyaviy ma'lumot yoki tranzaksiya bo'lsa → intent="finance"
- Agar oddiy suhbat, savol, salomlashish, taklif yoki boshqa narsa bo'lsa → intent="chat"
- MUHIM: "Bu bot pullikmi?", "Nima qila olasan?", "Salom", "Rahmat" — bular hammasi intent="chat"
- MUHIM: "taksiga 15 ming", "oylik tushdi", "Jasurga qarz berdim" — bular intent="finance"

═══ 2. TRANZAKSIYA TURLARI ═══
KIRIM: "tushdi", "oldim" (ish kontekstida), "ishladim", "sotdim", "kirim", "maosh", "oylik"
CHIQIM: "xarjladim", "ketdi", "to'ladim", "sarfladim", "sotib oldim", "berdim" (xizmat/mahsulot uchun), "ishlatdim"

QARZ — direction ni to'g'ri aniqla:
- "Jasurga 100 ming berdim" → direction: "bergan" (Jasur qaytarishi kerak)
- "Jasurdan 100 ming oldim" → direction: "olgan" (Men qaytarishim kerak)
- "Jasur menga 100 ming berishi kerak" → direction: "bergan"
- "Men Jasurga 100 ming beraman" → direction: "olgan"
MUHIM: Qarz HECH QACHON balansni o'zgartirmaydi!

═══ 3. MIQDOR ═══
"ming" → ×1000, "mln"/"million" → ×1000000
"yarim million" → 500000, "bir yarim million" → 1500000

═══ 4. VALYUTA ═══
"so'm"/"sum"/"UZS" → UZS, "dollar"/"$"/"USD" → USD
"rubl"/"₽"/"RUB" → RUB, "tenge"/"₸"/"KZT" → KZT
Aytilmagan → "UZS"

═══ 5. KO'P TRANZAKSIYA ═══
Bitta xabarda bir nechta bo'lsa — BARCHASINI alohida ajrat.

═══ 6. SANA — BU JUDA MUHIM! ═══
"bugun" → {current_date_str}
"kecha" → {yesterday} (ANIQ kechagi sana!)
"ertaga" → {tomorrow} (ANIQ ertangi sana!)
"o'tgan haftada" → tegishli sana
"10-may" → 2026-05-10
Aytilmagan → {current_date_str}
Har doim YYYY-MM-DD formatida.

═══ 7. ESLATMA VAQTI (reminder) ═══
Agar foydalanuvchi "ertaga", "2 kundan keyin" yoki aniq sana aytsa VA bu qarz yoki kelajakdagi harakat bo'lsa:
- "reminder_date" maydonini qo'shing (YYYY-MM-DD formatida)
- "reminder_time" maydonini qo'shing (HH:MM formatida, 24 soatlik)
- Agar soat aytilmagan bo'lsa → "{current_time}" ni qo'ying (hozirgi vaqt)
- Agar soat aytilgan bo'lsa (masalan "kechki 6 da") → "18:00" qo'ying

Misol: "ertaga Sardorga 20 ming berishim kerak soat 6 da" → 
  reminder_date: "{tomorrow}", reminder_time: "18:00"
Misol: "ertaga Sardorga 20 ming berishim kerak" → 
  reminder_date: "{tomorrow}", reminder_time: "{current_time}"

═══ 8. KATEGORIYALAR ═══
Kategoriyanlarni tanlashda quyidagi tartibga amal qiling:
1. AVVAL shaxsiy (foydalanuvchi) kategoriyalarini tekshiring
2. Keyin tizim kategoriyalaridan tanlang
3. Hech biri mos kelmasa "📦 Boshqa xarajat" yoki "💸 Boshqa daromad" bering

{categories_text}

Kategoriya formati: "emoji nom" (masalan: "🚕 Taksi")

═══ JAVOB FORMATI ═══

Agar "chat":
Foydalanuvchiga {lang_name} tilida QISQA, ANIQ va LO'NDA javob bering.
MUHIM: Foydalanuvchining muomalasiga, kayfiyatiga va so'zlashuv uslubiga to'liq moslashing (segmentatsiyaga e'tibor bering). Agar u rasmiy yozsa, siz ham rasmiy javob bering. Agar samimiy, do'stona yoki emotsional yozsa, xuddi shunday do'stona va emotsional javob bering. AI o'zini o'zi tarbiyalashi va har bir foydalanuvchiga individual yondashishi shart.
Ba'zan (har doim emas!) foydalanuvchi uslubiga mos kichik moliyaviy motivatsiya qo'shing.
{{
  "intent": "chat",
  "reply": "..."
}}

Agar "finance":
{{
  "intent": "finance",
  "unclear": false,
  "unclear_reason": "",
  "transactions": [
    {{
      "type": "kirim|chiqim|qarz",
      "amount": 15000,
      "currency": "UZS",
      "date": "{current_date_str}",
      "description": "Taksiga",
      "category": "🚕 Transport",
      "direction": "bergan",
      "person": "Jasur",
      "due_date": "nomalum",
      "reminder_date": null,
      "reminder_time": null
    }}
  ]
}}

MUHIM: Faqat JSON, boshqa hech narsa yozma."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]

        response = await self.chat_completion_with_retry(
            messages,
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=1500,
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error(f"Groq did not return valid JSON: {response}")
            return {"intent": "chat", "reply": "Kechirasiz, tushunmadim. Qaytadan yozing."}


groq_service = GroqService()
