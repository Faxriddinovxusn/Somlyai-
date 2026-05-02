# Somly AI Excel Hisobot Tizimi

## 📊 Xulosa

Somly AI endi amaliy va turli shaklida moliyaviy hisobotlarni yaratish qobiliyatiga ega. Hisobot Excel formatida bo'lib, unda uchta varaq mavjud:
1. **Xulosa** - Umumiy ko'rsatkichlar va kategoriya analizi
2. **Tranzaksiyalar** - Kunlik guruhlashtirilgan barcha tranzaksiyalar
3. **Qarzlar** - Berishim kerak va olishim kerak bo'lgan qarzlar

---

## 🎯 Xususiyatlar

### 1. **Xulosa Varaqasi**
- Foydalanuvchi nomi va davr
- Jami kirim (yashil, katta raqam)
- Jami chiqim (qizil, katta raqam)
- Sof qoldiq (ko'k, katta raqam)
- Kategoriyalar bo'yicha chiqim jadvali (eng ko'p sarflangandan kamiga)
- Qarzlar haqida umumiy ma'lumot

### 2. **Tranzaksiyalar Varaqasi**
```
№ | Sana | Kun | Tur | Summa | Valyuta | Kategoriya | Izoh | Balans (keyin) | Shaxs
```
- Kunlik guruhlashtirilgan
- Kun boshiga qoldiq (och ko'k fon)
- Kirim qatorlari och yashil fonla
- Chiqim qatorlari och qizil fonla
- Qarz qatorlari och sariq fonla
- Kun yakuni xulosasi (kulganlashgan, italic)

### 3. **Qarzlar Varaqasi**
**BERISHIM KERAK (Men qarzman)** - Qizil sarlavha
- Ism | Summa | Valyuta | Sana | Muddat | Holat

**OLISHIM KERAK (U qarzdir)** - Yashil sarlavha
- Ism | Summa | Valyuta | Sana | Muddat | Holat

**Holatlar:** Aktiv / To'landi / Qisman / Bekor

---

## 💻 Foydalanish

### Botda Foydalanish

#### 1. `/excel` Buyrug'i
```
/excel
```
Bot sizga davr tanlash klaviaturasini ko'rsatadi:
- **Bu oy** - Joriy oyning 1-kunidan bugungi kunga qadar
- **O'tgan oy** - O'tgan oyning to'liq davri
- **Oxirgi 3 oy** - Sodir bo'lgan oxirgi 90 kunlik davr
- **Hammasi** - Barcha vaqtdagi tranzaksiyalar

#### 2. Davr Tanlash
Kerakli tugmani bosing. Bot:
1. Hisobot tayyorlanmoqda degen xabarni ko'rsatadi
2. Excel faylni yaratadi
3. Fayl bilan xabar yuboradi

### Excel Faylining Nomi
```
Somly_[Ism]_[Oy]-[Yil].xlsx
Masalan: Somly_Husniddin_Aprel-2026.xlsx
```

### Xabar Shabloni
```
📊 Hisobotingiz tayyor!

📅 Davr: [Tanlangan davr]
💰 Kirim: [Raqam] UZS
💸 Chiqim: [Raqam] UZS
✅ Qoldiq: [Raqam] UZS

📎 Somly_[Ism]_[Oy]-[Yil].xlsx
```

---

## 🎨 Dizayn Standartlari

### Ranglar
- **Sarlavhalar**: To'q ko'k fon (#1E40AF), oq matn
- **Kirim qatorlari**: Och yashil fon (#D1FAE5)
- **Chiqim qatorlari**: Och qizil fon (#FECACA)
- **Qarz qatorlari**: Och sariq fon (#FEF3C7)
- **Bir vaqtning o'zida qatorlar**: Kulrang fon (#F3F4F6)
- **Kun boshiga qoldiq**: Och ko'k fon (#DBEAFE)

### Tekislash
- **Raqamlar**: O'ngdan tekislangan
- **Matnlar**: Chapdan tekislangan
- **Sarlavhalar**: Markazga tekislangan

### Formatlash
- **Raqamlar**: #,##0 (1 000 000 ko'rinishi)
- **Foizlar**: 0.0% (10.5% ko'rinishi)
- **Birinchi qator**: Muzlatilgan (scroll qilganda ham ko'rinib turadi)
- **Filtrlar**: Sarlavha qatorida yoqilgan

---

## 🔧 Texnik Ma'lumotlar

### Fayllar
- **Excel Service**: `src/services/excel_service.py`
- **Export Handler**: `src/handlers/export_handler.py`
- **Database Queries**: `src/database.py`

### Tez'korlash
```python
# Excel faylni tashlab qo'yish
from src.services.excel_service import generate_excel_report

filepath = await generate_excel_report(
    telegram_id=12345,
    date_from=datetime(2026, 4, 1),
    date_to=datetime(2026, 4, 30),
    language="uz"
)
```

### Ma'lumot Manbalar
- **Tranzaksiyalar**: `transactions` koleksiyasi
  - Filtrlash: `date` maydoni (YYYY-MM-DD)
- **Qarzlar**: `debts` koleksiyasi
  - Filtrlash: `telegram_id` va `status`
- **Foydalanuvchi**: `users` koleksiyasi
  - Nomi va tilni olish

### API Endpointi (Future)
Mini App-da "📥 Hisobotni yuklab olish" tugmasi qo'shiladi.

---

## 📝 Misol

### Yanvar 2026 uchun Husniddin Aprel 2026 hisoboti:

**Fayl nomi**: `Somly_Husniddin_Aprel-2026.xlsx`

**Xulosa Varaqasi**:
```
Somly AI — Moliyaviy Hisobot
Foydalanuvchi: Husniddin
Davr: 01 Aprel 2026 — 24 Aprel 2026
Yaratildi: 25.04.2026 14:32

Jami kirim:  8,767,000 UZS
Jami chiqim: 70,000 UZS
Sof qoldiq:  8,697,000 UZS
```

**Kategoriyalar**:
| Kategoriya | Kirim | Chiqim | Foiz |
|-----------|-------|--------|------|
| Bozor | 0 | 45,000 | 64.3% |
| Transport | 0 | 25,000 | 35.7% |

---

## 🐛 Muammo Yechim

### Xatolik: "Hisobot yaratishda xato"
- MongoDB ulanishi tekshirilsin
- `temp/` papkasi mavjud ekanligini tekshirilsin

### Xatolik: "Fayl yuklanmadi"
- Fayl o'lchami 50 MB dan oshmasligi kerak
- Telegram API vaqtini tekshirilsin

### Xatolik: "Qarz qatorlari ko'rinmasdi"
- Minimal bitta qarz mavjud ekanligini tekshirilsin
- Qarz holatining "Aktiv" ekanligini tekshirilsin

---

## 🚀 Keldagi Rejalar

- [ ] Mini App-da "📥 Hisobotni yuklab olish" tugmasi
- [ ] CSV va PDF formatlarida export
- [ ] Avtomatik oylik hisobot yuborish
- [ ] Hisobot shablonlarini o'zlashtirish
- [ ] Turli valyuta uchun alohida hisobotlar

---

## 📧 Qo'llaniladigan Mamlakatlashlar

**Uzbek (uz)**:
- Davr: Yanvar, Fevral, Mart, Aprel, May, Iyun, Iyul, Avgust, Sentyabr, Oktyabr, Noyabr, Dekabr
- Kunlar: Dushanba, Seshanba, Chorshanba, Payshanba, Juma, Shanba, Yakshanba
- Holatlar: Aktiv, To'landi, Qisman, Bekor

---

**Ishlab chiqaruvchi**: Somly AI  
**Versiya**: 1.0  
**Oxirgi yangilanish**: 25.04.2026
