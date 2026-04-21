"""
Somly AI — 58 ta tizim kategoriyalari + shaxsiy kategoriya tizimi.

Tizim kategoriyalari o'zgartirib bo'lmaydi.
Shaxsiy kategoriyalarni foydalanuvchi yaratadi/o'zgartiradi/o'chiradi.
"""

# ═══════════════════════════════════════
# TIZIM KATEGORIYALARI (58 ta)
# ═══════════════════════════════════════

SYSTEM_CATEGORIES = [
    # ── KIRIM (10 ta) ──
    {"emoji": "💼", "name": "Maosh", "type": "kirim"},
    {"emoji": "💪", "name": "Mehnat daromadi", "type": "kirim"},
    {"emoji": "🏢", "name": "Biznes daromadi", "type": "kirim"},
    {"emoji": "🏠", "name": "Ijara daromadi", "type": "kirim"},
    {"emoji": "🛒", "name": "Savdo daromadi", "type": "kirim"},
    {"emoji": "💰", "name": "Investitsiya daromadi", "type": "kirim"},
    {"emoji": "🎁", "name": "Sovg'a (kirim)", "type": "kirim"},
    {"emoji": "💵", "name": "Qo'shimcha daromad", "type": "kirim"},
    {"emoji": "🏦", "name": "Bank foizi", "type": "kirim"},
    {"emoji": "💸", "name": "Boshqa daromad", "type": "kirim"},

    # ── CHIQIM: Oziq-ovqat va ichimlik (5 ta) ──
    {"emoji": "🍔", "name": "Oziq-ovqat", "type": "chiqim"},
    {"emoji": "🍽", "name": "Restoran va kafelar", "type": "chiqim"},
    {"emoji": "☕", "name": "Choy va qahva", "type": "chiqim"},
    {"emoji": "🍕", "name": "Fastfood", "type": "chiqim"},
    {"emoji": "🥤", "name": "Ichimliklar", "type": "chiqim"},

    # ── CHIQIM: Transport (5 ta) ──
    {"emoji": "🚕", "name": "Taksi", "type": "chiqim"},
    {"emoji": "🚌", "name": "Jamoat transporti", "type": "chiqim"},
    {"emoji": "🚗", "name": "Mashina xarajati", "type": "chiqim"},
    {"emoji": "⛽", "name": "Yoqilg'i va Gaz", "type": "chiqim"},
    {"emoji": "🅿️", "name": "Avtoturargoh", "type": "chiqim"},

    # ── CHIQIM: Uy-joy (5 ta) ──
    {"emoji": "🏠", "name": "Uy-joy xarajati", "type": "chiqim"},
    {"emoji": "💡", "name": "Kommunal to'lovlar", "type": "chiqim"},
    {"emoji": "🔧", "name": "Uy ta'mirlash", "type": "chiqim"},
    {"emoji": "🛋", "name": "Mebel va jihozlar", "type": "chiqim"},
    {"emoji": "🧹", "name": "Uy-ro'zg'or", "type": "chiqim"},

    # ── CHIQIM: Shaxsiy (5 ta) ──
    {"emoji": "👗", "name": "Kiyim-kechak", "type": "chiqim"},
    {"emoji": "💇", "name": "Go'zallik va sartaroshxona", "type": "chiqim"},
    {"emoji": "👤", "name": "Shaxsiy xarajat", "type": "chiqim"},
    {"emoji": "🧴", "name": "Gigiena va kosmetika", "type": "chiqim"},
    {"emoji": "👟", "name": "Poyabzal", "type": "chiqim"},

    # ── CHIQIM: Sog'liq (4 ta) ──
    {"emoji": "💊", "name": "Dori-darmon", "type": "chiqim"},
    {"emoji": "🏥", "name": "Kasalxona va klinika", "type": "chiqim"},
    {"emoji": "🦷", "name": "Tish doktori", "type": "chiqim"},
    {"emoji": "👓", "name": "Optika va ko'zoynak", "type": "chiqim"},

    # ── CHIQIM: Ta'lim va rivojlanish (4 ta) ──
    {"emoji": "📚", "name": "O'qish va kurslar", "type": "chiqim"},
    {"emoji": "🎓", "name": "Ta'lim to'lovi", "type": "chiqim"},
    {"emoji": "📖", "name": "Kitoblar", "type": "chiqim"},
    {"emoji": "💻", "name": "Onlayn kurslar", "type": "chiqim"},

    # ── CHIQIM: Texnologiya (3 ta) ──
    {"emoji": "📱", "name": "Telefon va aloqa", "type": "chiqim"},
    {"emoji": "🖥", "name": "Kompyuter va texnika", "type": "chiqim"},
    {"emoji": "🔌", "name": "Aksessuarlar", "type": "chiqim"},

    # ── CHIQIM: Ko'ngilochar (5 ta) ──
    {"emoji": "🎮", "name": "O'yin-kulgi", "type": "chiqim"},
    {"emoji": "🎬", "name": "Kino va teatr", "type": "chiqim"},
    {"emoji": "🎵", "name": "Musiqa va obuna", "type": "chiqim"},
    {"emoji": "✈️", "name": "Sayohat", "type": "chiqim"},
    {"emoji": "🏖", "name": "Dam olish", "type": "chiqim"},

    # ── CHIQIM: Sport va salomatlik (3 ta) ──
    {"emoji": "🏋️", "name": "Sport va fitnes", "type": "chiqim"},
    {"emoji": "🏊", "name": "Basseyn", "type": "chiqim"},
    {"emoji": "🧘", "name": "Yoga va meditatsiya", "type": "chiqim"},

    # ── CHIQIM: Boshqalar (5 ta) ──
    {"emoji": "🛍", "name": "Xaridlar", "type": "chiqim"},
    {"emoji": "🎁", "name": "Sovg'alar va ehsonlar", "type": "chiqim"},
    {"emoji": "🐶", "name": "Uy hayvonlari", "type": "chiqim"},
    {"emoji": "📦", "name": "Boshqa xarajat", "type": "chiqim"},

    # ── HAR IKKALASI (4 ta) ──
    {"emoji": "🤝", "name": "Qarz", "type": "both"},
    {"emoji": "💳", "name": "To'lov", "type": "both"},
    {"emoji": "🔄", "name": "O'tkazma", "type": "both"},
    {"emoji": "📋", "name": "Boshqa", "type": "both"},
]


def get_system_categories_by_type(cat_type: str = None) -> list:
    """Tizim kategoriyalarini tur bo'yicha filtrlash."""
    if not cat_type or cat_type == "all":
        return SYSTEM_CATEGORIES
    if cat_type == "both":
        return [c for c in SYSTEM_CATEGORIES if c["type"] in ["both"]]
    return [c for c in SYSTEM_CATEGORIES if c["type"] in [cat_type, "both"]]


def get_category_display(emoji: str, name: str) -> str:
    """'🍔 Oziq-ovqat' formatida qaytaradi."""
    return f"{emoji} {name}"


def find_system_category(query: str) -> dict | None:
    """Tizim kategoriyasini nomidan qidirish."""
    query_lower = query.lower()
    for cat in SYSTEM_CATEGORIES:
        if cat["name"].lower() == query_lower or cat["emoji"] in query:
            return cat
    # Partial match
    for cat in SYSTEM_CATEGORIES:
        if query_lower in cat["name"].lower():
            return cat
    return None


def get_all_category_names_for_ai(custom_categories: list = None) -> str:
    """AI prompti uchun barcha kategoriyalar ro'yxatini matn sifatida qaytaradi."""
    lines = []

    if custom_categories:
        lines.append("SHAXSIY KATEGORIYALAR (birinchi navbatda shulardan tanlang!):")
        for c in custom_categories:
            lines.append(f"  {c['emoji']} {c['name']} ({c['type']})")
        lines.append("")

    lines.append("TIZIM KATEGORIYALARI:")
    lines.append("KIRIM:")
    for c in SYSTEM_CATEGORIES:
        if c["type"] == "kirim":
            lines.append(f"  {c['emoji']} {c['name']}")

    lines.append("CHIQIM:")
    for c in SYSTEM_CATEGORIES:
        if c["type"] == "chiqim":
            lines.append(f"  {c['emoji']} {c['name']}")

    lines.append("HAR IKKALASI:")
    for c in SYSTEM_CATEGORIES:
        if c["type"] == "both":
            lines.append(f"  {c['emoji']} {c['name']}")

    return "\n".join(lines)
