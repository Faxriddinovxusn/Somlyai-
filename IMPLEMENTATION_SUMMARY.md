# Somly AI Excel Hisobot Tizimi - Ishlanma Xulosa

## ✅ Bajarilgan Ishlar

### 1. **Excel Service Module** (`src/services/excel_service.py`)
Yaratilgan bo'lib, quyidagi xususiyatlarni o'z ichiga oladi:

#### Varaqalar
- **Xulosa Varaqasi**: Umumiy ko'rsatkichlar, kategoriya analizi, qarz haqida ma'lumot
- **Tranzaksiyalar Varaqasi**: Kunlik guruhlashtirilgan, balans tracking
- **Qarzlar Varaqasi**: Berishim kerak / Olishim kerak bo'lgan qarzlar

#### Dizayn Xususiyatlari
- Professional rang kodlami (kirim-yashil, chiqim-qizil, qarz-sariq)
- Avtomatik formatla (raqamlar #,##0, foizlar 0.0%)
- Muzlatilgan sarlavhalar (scroll qilganda ko'rinib turadi)
- Filtr tugmalari sarlavha qatorida
- Ojon ketishdirilgan qatorlar alternativ ranglar bilan

#### Funktsiyalar
```python
async def generate_excel_report(
    telegram_id: int,
    date_from: datetime,
    date_to: datetime,
    language: str = "uz"
) -> str
```

### 2. **Export Handler** (`src/handlers/export_handler.py`)
Bot komandasini boshqaradi:

#### `/excel` Buyrug'i
- Davr tanlash interfeysi
- Avtomatik Excel tuzatiladi
- Telegram orqali fayl yuboriladi

#### Davr Variantlari
- Bu oy (oy 1-kunidan bugunga)
- O'tgan oy (to'liq oyning davri)
- Oxirgi 3 oy (90 kunlik davr)
- Hammasi (barcha ma'lumotlar)

#### Fayl Nomi
```
Somly_[Ism]_[Oy]-[Yil].xlsx
Masalan: Somly_Husniddin_Aprel-2026.xlsx
```

#### Xabar Shabloni
```
📊 Hisobotingiz tayyor!

📅 Davr: [Davr]
💰 Kirim: X,XXX,XXX UZS
💸 Chiqim: X,XXX,XXX UZS
✅ Qoldiq: X,XXX,XXX UZS

📎 Fayl nomi
```

### 3. **Bot Integratsiyasi**
- Handler `src/bot.py`-da ro'yxatga olingan
- `/excel` buyrug'i ishlaydi
- Keyboard tugmalari qo'shildi

### 4. **Ma'lumot Bazasi Integratsiyasi**
Ishlatiladigan funktsiyalar:
- `get_user()` - Foydalanuvchi ma'lumotlari
- `get_transactions_paginated()` - Tranzaksiyalar
- `get_user_all_balances()` - Balanslar
- `debts_collection` - Qarzlar

### 5. **Hujjatlar**
Yaratilgan dokumentlar:
- `EXCEL_GUIDE.md` - Foydalanish yo'riqnomasi
- `MINIAPP_EXPORT_INTEGRATION.md` - Mini App integratsiyasi
- Bu fayl

---

## 📁 Fayllar Tuzilmasi

```
Somly ai/
├── src/
│   ├── services/
│   │   └── excel_service.py          ✅ (yangi)
│   ├── handlers/
│   │   └── export_handler.py         ✅ (yangilangan)
│   └── bot.py                        ✅ (o'zgarishsiz, allaqachon ro'yxatga olingan)
├── temp/                              ✅ (yangi papka)
├── webapp/
│   └── src/pages/
│       └── Profile.jsx               ⚠️ (integratsiya kerak)
├── EXCEL_GUIDE.md                    ✅ (yangi)
├── MINIAPP_EXPORT_INTEGRATION.md     ✅ (yangi)
└── requirements.txt                  ✅ (openpyxl allaqachon mavjud)
```

---

## 🚀 Foydalanish

### Botdan
```
1. /excel buyrug'ini yozing
2. Davr tanlang (Bu oy / O'tgan oy / 3 oy / Hammasi)
3. ⏳ Kuting (hisobot tayyorlanmoqda)
4. 📊 Excel faylni qabul qiling
```

### Mini App dan (tugatish kerak)
```
1. Profile → "Hisobotni yuklab olish"
2. Davr tanlash modali
3. Davr tanlang
4. Bot bilan o'zaro ta'sirni tugatish
```

---

## 🔧 Texnik Detallar

### Varaqalar Tuzilmasi

#### 1. Xulosa (Summary)
- Sarlavha: "Somly AI — Moliyaviy Hisobot"
- Foydalanuvchi nomi va davr
- Katta raqamlar: Kirim (yashil), Chiqim (qizil), Qoldiq (ko'k)
- Kategoriyalar jadvali (eng ko'p sarflangandan kamiga)
- Qarz haqida umumiy ma'lumot

#### 2. Tranzaksiyalar
Ustunlar:
```
№ | Sana | Kun | Tur | Summa | Valyuta | Kategoriya | Izoh | Balans | Shaxs
```
Kunlik guruhlashtirilgan:
- Kun boshiga qoldiq (och ko'k fon)
- Kirim qatorlari (och yashil fon)
- Chiqim qatorlari (och qizil fon)
- Qarz qatorlari (och sariq fon)
- Kun yakuni xulosasi (kulganlashgan, italic)

#### 3. Qarzlar
Ikkita bo'lim:
- **BERISHIM KERAK** (Men qarzman) - Qizil sarlavha
- **OLISHIM KERAK** (U qarzdir) - Yashil sarlavha

Ustunlar:
```
Ism | Summa | Valyuta | Sana | Muddat | Holat
```

Holatlar: Aktiv, To'landi, Qisman, Bekor

### Rang Sxemasi
```python
Sarlavhalar:        #1E40AF (to'q ko'k)
Kirim fon:          #D1FAE5 (och yashil)
Chiqim fon:         #FECACA (och qizil)
Qarz fon:           #FEF3C7 (och sariq)
Alternativ qator:   #F3F4F6 (kulrang)
Kun boshiga qoldiq: #DBEAFE (och ko'k)
Matn oq:            #FFFFFF
```

### Formatlar
```
Raqamlar:           #,##0
Foizlar:            0.0%
Sana:               YYYY-MM-DD
Kun:                Dushanba, Seshanba, ...
Oy:                 Yanvar, Fevral, ...
```

---

## 💾 Ma'lumot Alqashlash

### Tranzaksiyalar Qayta Olish
```python
txs, _ = await get_transactions_paginated(
    telegram_id=user_id,
    page=1,
    per_page=10000,
    date_from="2026-04-01",
    date_to="2026-04-30"
)
```

Tranzaksiya ob'yekti:
```python
{
    "_id": ObjectId(...),
    "telegram_id": 123456,
    "type": "kirim" | "chiqim",
    "amount": 1000000,
    "currency": "UZS",
    "date": "2026-04-20",
    "description": "Oylik",
    "category": "Kirim",
    "affects_balance": True,
    "created_at": datetime
}
```

### Qarzlar Qayta Olish
```python
debts = await debts_collection.find({
    "telegram_id": user_id,
    "status": "active"
}).to_list(None)
```

Qarz ob'yekti:
```python
{
    "_id": ObjectId(...),
    "telegram_id": 123456,
    "person": "Jasur",
    "amount": 1000000,
    "paid_amount": 0,
    "currency": "UZS",
    "direction": "bergan" | "olgan",
    "date": "2026-04-20",
    "due_date": "2026-05-20" | None,
    "status": "active" | "paid" | "partial" | "cancelled",
    "created_at": datetime
}
```

---

## 🐛 Debugging

### Excel fayl yaratilmayotgan bo'lsa
1. MongoDB ulanishini tekshiring
2. `temp/` papkasining mavjudligini tekshiring
3. Openpyxl nomidir ekanligini tekshiring: `pip list | grep openpyxl`

### Tranzaksiyalar ko'rinmasayotgan bo'lsa
1. Davr rangini tekshiring (date vs created_at)
2. Telefon raqamini tekshiring (telegram_id)
3. Lokal soatni tekshiring (UTC vs local)

### Qarz qatorlari ko'rinmasayotgan bo'lsa
1. Minimal bitta qarz yaratilganligini tekshiring
2. Qarz holatining "active" ekanligini tekshiring
3. Direction maydonining "bergan" yoki "olgan" ekanligini tekshiring

---

## 📊 Misol Output

### Xulosa Varaqasi
```
Somly AI — Moliyaviy Hisobot
Foydalanuvchi: Husniddin
Davr: 01 Aprel 2026 — 24 Aprel 2026
Yaratildi: 25.04.2026 14:32

Jami kirim:  8,767,000 UZS  (YASHIL, KATTA)
Jami chiqim: 70,000 UZS     (QIZIL, KATTA)
Sof qoldiq:  8,697,000 UZS  (KO'K, KATTA)

KATEGORIYALAR:
│ Kategoriya │ Kirim    │ Chiqim  │ Foiz   │
├────────────┼──────────┼─────────┼────────┤
│ Bozor      │ 0        │ 45,000  │ 64.3%  │
│ Transport  │ 0        │ 25,000  │ 35.7%  │

QARZLAR:
Berishim kerak: 50,000 UZS
Olishim kerak: 100,000 UZS
```

---

## ✨ Oziqlik Versiyada O'zgarishlar

### Qo'shilganlar
- Excel service module
- Export handler
- Hujjatlar (3 ta)
- temp papkasi

### O'zgartirilganlar
- export_handler.py (yangilangan logika)
- repo memory (yangilanma qo'shildi)

### Saqlanganlar
- bot.py (ro'yxat allaqachon o'rnatilgan edi)
- requirements.txt (openpyxl allaqachon mavjud edi)
- Barcha boshqa fayllar o'zgarishsiz qoldi

---

## 🎯 Keyingi Qadamlar

### 1. Mini App Integratsiyasi
- [ ] Profile.jsx da export modal yangilash
- [ ] Telegram WebApp API bilan bog'lanish
- [ ] Button funksionalligini sinov qilish

### 2. Qo'shimcha Formatlar
- [ ] PDF export
- [ ] CSV export
- [ ] JSON export

### 3. Avtomatsyon
- [ ] Oylik hisobot avtomatik yuborish
- [ ] Remind eslatmalar
- [ ] Shaxsiy shablonlar

### 4. Takomallash
- [ ] Barcha valyutalar uchun alohida hisobotlar
- [ ] Turli diapazonlar
- [ ] Turli tillar

---

## 📞 Qo'llab Quvvatlash

Agar muammoning yuzaga kelsa:
1. EXCEL_GUIDE.md - foydalanish yo'riqnomasi
2. MINIAPP_EXPORT_INTEGRATION.md - Mini App integratsiyasi
3. src/services/excel_service.py - kod izahlari
4. src/handlers/export_handler.py - handler izahlari

---

**Ishchi: GitHub Copilot**  
**Sana: 25.04.2026**  
**Versiya: 1.0**  
**Holat: ✅ Tayyor Ishlanish va Sinovlash Uchun**
