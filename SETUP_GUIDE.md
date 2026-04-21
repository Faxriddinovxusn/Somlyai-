🎯 SOMLY AI - 1-BOSQICH SETUP GUIDE
════════════════════════════════════════════════════

✅ TAYYORLANGAN:
- Loyiha struktura (src/ papka + barcha modullar)
- MongoDB schemas (User, Transaction, Debt)
- Telegram Bot integration (telegraf)
- Groq API servisi
- Config va .env setup
- Logger va validators

════════════════════════════════════════════════════

📋 KO'RSATMALAR - 5 TA BOSQICH

BOSQICH 1: NPM INSTALL
─────────────────────
1. PowerShell/Terminal ochang:
   cd "Somly ai"

2. Setup skriptini ishga tushuring:
   Windows: .\setup.bat
   Linux/Mac: bash setup.sh

   YOKI qo'lda:
   npm install

✅ Bu barcha dependensiyalarni o'natadi:
   • telegraf - Telegram Bot
   • mongoose - MongoDB
   • groq-sdk - AI Service
   • dotenv - Environment variables
   • node-cron - Scheduler
   • nodemon - Development

════════════════════════════════════════════════════

BOSQICH 2: .ENV FAYLINI TO'LDIRISH
──────────────────────────────────
.env.example fayl allaqachon tayyorlangan!

📝 Quyidagilarni qilish kerak:

A) .env FAYLINI YARATISH:
   1. .env.example ni .env ga nusxa qiling
   2. .env faylini text editori bilan oching

B) QIYMATLARNI TO'LDIRISH:

   🔴 KERAKLI QIYMATLAR (Majburiy):
   
   ► BOT_TOKEN
   Olish: @BotFather da /newbot buyrug'i
   Link: https://t.me/BotFather
   Format: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
   
   ► ADMIN_ID
   Olish: @userinfobot da /start buyrug'i
   Link: https://t.me/userinfobot
   Format: 123456789 (faqat raqam)
   
   ► MONGO_URI
   Olish: MongoDB Atlas (bepul tier)
   Link: https://www.mongodb.com/cloud/atlas
   Format: mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
   
   Steps:
   1. MongoDB Atlas da ro'yxatdan o'ting
   2. Create Project
   3. Build Database (Shared - bepul)
   4. Create cluster
   5. IP Whitelist qo'shing (0.0.0.0/0 - development uchun)
   6. Database User yarating
   7. Connection String qo'chiring
   
   ► GROQ_API_KEY
   Olish: Groq Console
   Link: https://console.groq.com/keys
   Format: gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   
   Steps:
   1. https://console.groq.com ga kiring
   2. API Keys qo'shimni oching
   3. "+ Create API Key" bosing
   4. Key nusxa qo'chiring
   5. .env ga yozing

   🟡 IXTIYORIY QIYMATLAR:
   
   ► CHANNEL_1, CHANNEL_2, CHANNEL_3
   Telegram kanallaringizning nomlari
   Format: @channel_name (bo'sh qoldirish mumkin)
   
   ► WEBAPP_URL
   Local: http://localhost:3000
   Production: https://yourdomain.com
   Bo'sh qoldirish mumkin

════════════════════════════════════════════════════

BOSQICH 3: MONGO_URI OQISH (DETAIL)
────────────────────────────────────
Agar MongoDB Atlas da yangi bo'lsangiz:

1. https://account.mongodb.com/account/login ga kiring
2. Create Free Account
3. Create Organization
4. Create Project
5. Build Database → Shared (Bepul) → Create

6. Network Access:
   - "Network Access" → "Add IP Address"
   - "Allow Access from Anywhere" (0.0.0.0/0) - FAQAT DEVELOPMENT
   - Confirm

7. Database Access:
   - "Database Access" → "+ Add New Database User"
   - Username: somly_user (yoki boshqa)
   - Password: kuchli parol yarating
   - "Add User"

8. Connection String:
   - "Databases" → "Cluster" → "Connect"
   - "Connect your application"
   - Node.js 4.1 or later tanlang
   - Connection string nusxa qo'chiring
   - String ichidagi <password> o'riniga password yozing
   - .env ga yozing

EXAMPLE MONGO_URI:
mongodb+srv://somly_user:MyPassword123@cluster0.abc123.mongodb.net/?retryWrites=true&w=majority

════════════════════════════════════════════════════

BOSQICH 4: BOT TOKENNI OLISH
────────────────────────────
1. https://t.me/BotFather ga kiring
2. /start → /newbot buyrug'ini kiriting
3. Bot nomi kiriting (misol: Somly AI Bot)
4. Username kiriting (misol: somly_ai_bot)
5. Token oling va .env ga yozing

EXAMPLE BOT_TOKEN:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890

════════════════════════════════════════════════════

BOSQICH 5: GROQ API KEY OLISH
──────────────────────────────
1. https://console.groq.com/keys ga kiring
2. (Groq accountga ro'yxatdan o'ting yoki kiring)
3. "+ Create API Key" bosing
4. Key nusxa qo'chiring
5. .env ga yozing

EXAMPLE GROQ_API_KEY:
gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

════════════════════════════════════════════════════

⚠️ XATOLAR VA YECHIMLAR
────────────────────────

❌ "BOT_TOKEN missing"
   → .env faylni .gitignore ga qo'shilganini tekshiring
   → BOT_TOKEN qiymati bo'shmi? Tekshiring

❌ "MongoDB ulanish xatosi"
   → MONGO_URI o'g'ri kiritilganmi?
   → IP Whitelist qo'shilganmi?
   → Database User yaratilganmi?
   → Password to'g'rimi?

❌ "Groq parsing xatosi"
   → GROQ_API_KEY mavjudmi?
   → API Key faol emasmi?
   → Internet ulanishi bormi?

════════════════════════════════════════════════════

🚀 BOSHLASH
────────────
Hammasi to'liq qo'shilgandan keyin:

npm start        # Production mode
npm run dev      # Development mode (nodemon)

Bot Telegram chat ga /start yuboring
✅ Bot javob bersa, muvaffaq!

════════════════════════════════════════════════════

📚 QUYIDAGI BOSQICHLAR:

2️⃣ ONBOARDING - /start, telefon, ism qabul qilish
3️⃣ AI PARSING - Groq bilan tranzaksiya parsing
4️⃣ TRANZAKSIYA SAQLASH - MongoDB ga saqlash
5️⃣ BALANS TIZIMI - Hisob-kitob
6️⃣ QARZ TRACKING - Qarz monitoring
7️⃣ MINI APP DASHBOARD - Web UI
8️⃣ STATISTIKA - Grafiklar va analitika
9️⃣ ESLATMALAR - Scheduler
🔟 KANAL OBUNA - Obuna taklifi

════════════════════════════════════════════════════
