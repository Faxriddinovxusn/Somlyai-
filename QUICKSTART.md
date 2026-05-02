# 🚀 Somly AI Excel Hisobot - Tez Boshlash

## 📋 Chek-List (Tayyorlik)

- [x] Excel service module (`src/services/excel_service.py`) - ✅ Tayyor
- [x] Export handler (`src/handlers/export_handler.py`) - ✅ Yangilangan
- [x] Bot integratsiyasi - ✅ O'rnatilgan
- [x] temp/ papkasi - ✅ Yaratilgan
- [x] Hujjatlar - ✅ Tayyorlangan
- [ ] Mini App integratsiyasi - ⏳ Qo'shimcha

---

## 🎯 1-Qadamlar

### 1. Botni Sinov Qilish

```bash
# Bot ishlatilmaqda ekanligini tekshiring
python run.py
```

### 2. `/excel` Buyrug'iga Sinov Qilish

Telegram botda `/excel` yazib, buyruq ishlamasligini tekshiring:
```
/excel
```

Ko'ring bo'lishi kerak:
- Davr tanlash klaviaturasi
- 4 ta tugma: "Bu oy", "O'tgan oy", "Oxirgi 3 oy", "Hammasi"

### 3. Davr Tanlash

Tugmalardan bittasini bosing, masalan "Bu oy"

Ko'ring bo'lishi kerak:
- ⏳ "Hisobot tayyorlanmoqda, kuting..." xabari
- 📊 Excel fayl bilan xabar

### 4. Excel Faylni Ochish

Yuklangan faylni ochib, barcha varaqalarni tekshiring:
- ✅ Xulosa - umumiy ko'rsatkichlar
- ✅ Tranzaksiyalar - kunlik guruhlashtirilgan
- ✅ Qarzlar - berishim kerak / olishim kerak

---

## 🔍 Muammo Yechim

### Xatolik: "❌ Xato..."

**Sabab 1: MongoDB ulanmadi**
```bash
# Tekshirilsin .env fayli
# MONGO_URI=mongodb://localhost:27017
# DB_NAME=somly_ai
```

**Sabab 2: temp/ papkasi yo'q**
```bash
# Papka yaratilsin
mkdir temp
```

**Sabab 3: openpyxl o'rnatilmadi**
```bash
pip install openpyxl
```

### Xatolik: Faylda ma'lumot yo'q

**Sabab**: Tanlangan davarda tranzaksiya yo'q

**Yechim**: Avval tranzaksiya qo'shing, keyin qayta sinov qiling

### Xatolik: Qarz qatorlari ko'rinmasdi

**Sabab**: Qarz yaratilmagan

**Yechim**: Bot orqali qarz qo'shing, keyin qayta sinov qiling

---

## 📁 Fayl Strukturasi

```
Somly ai/
├── src/
│   ├── services/
│   │   ├── excel_service.py          ← Excel tuzatish
│   │   └── groq_service.py
│   ├── handlers/
│   │   ├── export_handler.py         ← Bot komandasini boshqarish
│   │   └── ...
│   └── bot.py                        ← Handler ro'yxat
├── temp/                              ← Excel fayllar saqlanadi
├── EXCEL_GUIDE.md                    ← Batafsil yo'riqnoma
├── MINIAPP_EXPORT_INTEGRATION.md     ← Mini App ulanish
├── IMPLEMENTATION_SUMMARY.md         ← Ishlanma xulosa
└── requirements.txt                  ← Kutubxonalar (openpyxl mavjud)
```

---

## 🎨 Varaqalar Xulosa

### 1️⃣ Xulosa Varaqasi
```
Somly AI — Moliyaviy Hisobot
Foydalanuvchi: [Ism]
Davr: 01 Aprel 2026 — 24 Aprel 2026
Yaratildi: 25.04.2026 14:32

Jami kirim:  8,767,000 UZS  (yashil)
Jami chiqim: 70,000 UZS     (qizil)
Sof qoldiq:  8,697,000 UZS  (ko'k)

Kategoriyalar bo'yicha chiqim tabli
```

### 2️⃣ Tranzaksiyalar Varaqasi
```
Kunlik guruhlashtirilgan:
- Kun boshiga qoldiq
- Kirim qatorlari (och yashil)
- Chiqim qatorlari (och qizil)
- Kun yakuni xulosasi
```

### 3️⃣ Qarzlar Varaqasi
```
BERISHIM KERAK (Men qarzman) - qizil
OLISHIM KERAK (U qarzdir) - yashil
```

---

## 📊 Davr Variantlari

| Tugma | Davr |
|-------|------|
| Bu oy | Oy 1-kunidan bugungi kunga qadar |
| O'tgan oy | O'tgan oyning to'liq davri |
| Oxirgi 3 oy | Sodir bo'lgan oxirgi 90 kun |
| Hammasi | Barcha ma'lumotlar |

---

## 💾 Fayl Nomi

```
Somly_[Ism]_[Oy]-[Yil].xlsx

Masallar:
- Somly_Husniddin_Aprel-2026.xlsx
- Somly_Alla_May-2026.xlsx
- Somly_Sardor_Mart-2026.xlsx
```

---

## 🔗 Mini App Integratsiyasi (Keyingi Bosqich)

Mini App da "📥 Hisobotni yuklab olish" tugmasi mavjud, lekin bot bilan bog'lanishi kerak.

Qarang: `MINIAPP_EXPORT_INTEGRATION.md`

---

## 📱 Telegram Formatlar

### Yuborilayotgan Xabar

```
📊 Hisobotingiz tayyor!

📅 Davr: Bu oy
💰 Kirim: 8,767,000 UZS
💸 Chiqim: 70,000 UZS
✅ Qoldiq: 8,697,000 UZS

📎 Somly_Husniddin_Aprel-2026.xlsx
```

### Excel Fayl Shaxslari

- **Fayl nomi**: Oziq-turli nomli
- **Varaqalar**: 3 ta (Xulosa, Tranzaksiyalar, Qarzlar)
- **Rang Sxemasi**: Professional va oson o'qish
- **Formatlar**: Raqamlar, foizlar, sana - to'g'ri formatda
- **Muzlatilgan Sarlavhalar**: Scroll qilganda ham ko'rinib turadi

---

## ⚡ Tezlik Kodi

### Bot orqali export
```python
# Handler allaqachon ishlaydi
/excel → davr tanlash → Excel generation → file yuborish
```

### Ma'lumot manbalar
```python
# Tranzaksiyalar
telegram_id + date (YYYY-MM-DD) = filter

# Qarzlar  
telegram_id + status = filter

# Balanslar
telegram_id = get user balances
```

---

## ✅ Sinov HolatI

- ✅ Excel service - Kodda xato yo'q
- ✅ Export handler - Kodda xato yo'q
- ✅ Bot integratsiyasi - O'rnatilgan
- ✅ Hujjatlar - Tayyorlangan
- ⏳ Mini App - Integratsiya kerak (variant)
- ⏳ End-to-End sinov - Hozir bajarish kerak

---

## 🎓 Qo'shimcha O'rganish

1. **EXCEL_GUIDE.md** - Batafsil foydalanish yo'riqnomasi
2. **MINIAPP_EXPORT_INTEGRATION.md** - Mini App ulanish
3. **IMPLEMENTATION_SUMMARY.md** - Texnik detallar
4. **src/services/excel_service.py** - Kod izahlari
5. **src/handlers/export_handler.py** - Handler kod

---

## 🚀 Keyingi Qadamlar

1. End-to-End sinov qilish
2. Production nasirga yuklash
3. Mini App integratsiyasi (ixtiyoriy)
4. Qo'shimcha formatlar (PDF, CSV)
5. Avtomatsyon (oylik hisobot)

---

**Tayyor bo'ldi! Sinov qilishni boshlayingiz! 🎉**

For detailed information, see: EXCEL_GUIDE.md
