"""
Database layer for Somly AI.

Balance structure per user:
{
    "telegram_id": 12345,
    "balances": {
        "UZS": {"amount": 0, "title": "So'm", "color": "#3B82F6", "limit": null},
        "USD": {"amount": 0, "title": "Dollar", "color": "#10B981", "limit": null}
    },
    "is_active": true
}

Debt structure:
{
    "telegram_id": 12345,
    "person": "Jasur",
    "amount": 100000,
    "paid_amount": 0,
    "currency": "UZS",
    "direction": "bergan",   # bergan = u senga qarzdir | olgan = sen unga qarzsan
    "date": "2026-04-21",
    "due_date": "2026-05-01" or null,
    "status": "active",      # active | paid | partial | cancelled
    "created_at": datetime
}
"""

from datetime import datetime, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from src import config

client = AsyncIOMotorClient(config.MONGO_URI)
db = client[config.DB_NAME]

# Collections
users_collection = db["users"]
transactions_collection = db["transactions"]
debts_collection = db["debts"]
admins_collection = db["admins"]
channels_collection = db["channels"]
custom_categories_collection = db["custom_categories"]
config_collection = db["config"]

# ═══════════════════════════════════════
# USER & BALANCE OPERATIONS
# ═══════════════════════════════════════

DEFAULT_BALANCES = {
    "UZS": {"amount": 0, "title": "So'm",   "color": "#3B82F6", "limit": None},
    "USD": {"amount": 0, "title": "Dollar", "color": "#10B981", "limit": None},
}

async def get_user(telegram_id: int) -> dict:
    """Get or create user with default UZS + USD balances."""
    user = await users_collection.find_one({"telegram_id": telegram_id})
    if not user:
        user = {
            "telegram_id": telegram_id,
            "full_name": None,
            "phone_number": None,
            "registration_complete": False,
            "language": "uz",
            "balances": {k: dict(v) for k, v in DEFAULT_BALANCES.items()},
            "settings": {"morning_reminder": True, "evening_reminder": True},
            "channels_joined": False,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_active": datetime.utcnow(),
        }
        await users_collection.insert_one(user)
        user = await users_collection.find_one({"telegram_id": telegram_id})
    else:
        # Update last active
        await users_collection.update_one(
            {"telegram_id": telegram_id},
            {"$set": {"last_active": datetime.utcnow()}}
        )
    return user


async def ensure_balance_exists(telegram_id: int, currency: str):
    """If currency balance doesn't exist yet, create it with 0."""
    user = await get_user(telegram_id)
    balances = user.get("balances", {})
    if currency not in balances:
        await users_collection.update_one(
            {"telegram_id": telegram_id},
            {"$set": {f"balances.{currency}": {
                "amount": 0,
                "title": currency,
                "color": "#6B7280",
                "limit": None,
            }}}
        )




async def update_user_language(telegram_id: int, language: str):
    await users_collection.update_one(
        {"telegram_id": telegram_id},
        {"$set": {"language": language}}
    )

async def update_user_channels_joined(telegram_id: int, joined: bool):
    await users_collection.update_one(
        {"telegram_id": telegram_id},
        {"$set": {"channels_joined": joined}}
    )


async def update_user_name(telegram_id: int, name: str):
    await users_collection.update_one(
        {"telegram_id": telegram_id},
        {"$set": {"full_name": name}}
    )


async def update_user_phone(telegram_id: int, phone: str):
    await users_collection.update_one(
        {"telegram_id": telegram_id},
        {"$set": {"phone_number": phone, "registration_complete": True}}
    )

async def update_user_balance(telegram_id: int, currency: str, amount: float, is_income: bool) -> float:
    """
    Kirim → balance increases.
    Chiqim → balance decreases (can go negative).
    Returns new balance amount.
    """
    currency = currency.upper()
    await ensure_balance_exists(telegram_id, currency)
    user = await get_user(telegram_id)

    current = user["balances"][currency]["amount"]
    new_amount = current + amount if is_income else current - amount

    await users_collection.update_one(
        {"telegram_id": telegram_id},
        {"$set": {f"balances.{currency}.amount": new_amount}}
    )
    return new_amount


async def get_user_balance(telegram_id: int, currency: str) -> float:
    currency = currency.upper()
    await ensure_balance_exists(telegram_id, currency)
    user = await get_user(telegram_id)
    return user["balances"][currency]["amount"]


async def get_user_all_balances(telegram_id: int) -> dict:
    user = await get_user(telegram_id)
    return user.get("balances", {})


async def create_custom_balance(telegram_id: int, currency: str, title: str,
                                initial_amount: float, color: str, limit: float = None):
    """Foydalanuvchi yangi balans qo'shadi."""
    currency = currency.upper()
    await users_collection.update_one(
        {"telegram_id": telegram_id},
        {"$set": {f"balances.{currency}": {
            "amount": initial_amount,
            "title": title,
            "color": color,
            "limit": limit,
        }}}
    )


async def update_balance_limit(telegram_id: int, currency: str, limit: float):
    currency = currency.upper()
    await users_collection.update_one(
        {"telegram_id": telegram_id},
        {"$set": {f"balances.{currency}.limit": limit}}
    )


# ═══════════════════════════════════════
# TRANSACTION OPERATIONS
# ═══════════════════════════════════════

async def insert_transaction(data: dict) -> str:
    data["created_at"] = datetime.utcnow()
    result = await transactions_collection.insert_one(data)
    return str(result.inserted_id)


async def get_monthly_expense(telegram_id: int, currency: str) -> float:
    """Bu oyda qilingan jami chiqimlar summasi."""
    now = datetime.utcnow()
    first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    pipeline = [
        {"$match": {
            "telegram_id": telegram_id,
            "type": "chiqim",
            "currency": currency.upper(),
            "affects_balance": True,
            "created_at": {"$gte": first_day},
        }},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}},
    ]
    cursor = transactions_collection.aggregate(pipeline)
    result = await cursor.to_list(length=1)
    return result[0]["total"] if result else 0.0


async def get_monthly_income(telegram_id: int, currency: str) -> float:
    """Bu oyda qilingan jami kirimlar summasi."""
    now = datetime.utcnow()
    first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    pipeline = [
        {"$match": {
            "telegram_id": telegram_id,
            "type": "kirim",
            "currency": currency.upper(),
            "affects_balance": True,
            "created_at": {"$gte": first_day},
        }},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}},
    ]
    cursor = transactions_collection.aggregate(pipeline)
    result = await cursor.to_list(length=1)
    return result[0]["total"] if result else 0.0


async def get_transactions_paginated(
    telegram_id: int, page: int = 1, per_page: int = 10,
    type_filter: str = None, category_filter: str = None,
    currency_filter: str = None, search_query: str = None,
    date_from: str = None, date_to: str = None,
) -> tuple:
    """Returns (transactions_list, total_count) with filters and pagination."""
    query = {"telegram_id": telegram_id}

    if type_filter and type_filter != "all":
        query["type"] = type_filter
    if category_filter:
        query["category"] = {"$regex": category_filter, "$options": "i"}
    if currency_filter:
        query["currency"] = currency_filter.upper()
    if search_query:
        query["$or"] = [
            {"description": {"$regex": search_query, "$options": "i"}},
            {"category": {"$regex": search_query, "$options": "i"}},
        ]
    if date_from or date_to:
        date_q = {}
        if date_from:
            date_q["$gte"] = date_from
        if date_to:
            date_q["$lte"] = date_to
        query["date"] = date_q

    total = await transactions_collection.count_documents(query)
    skip = (page - 1) * per_page
    cursor = transactions_collection.find(query).sort("created_at", -1).skip(skip).limit(per_page)
    txs = await cursor.to_list(length=per_page)
    return txs, total


async def get_transaction_by_id(tx_id: str) -> dict | None:
    try:
        return await transactions_collection.find_one({"_id": ObjectId(tx_id)})
    except Exception:
        return None


async def update_transaction(tx_id: str, updates: dict):
    await transactions_collection.update_one(
        {"_id": ObjectId(tx_id)},
        {"$set": updates}
    )


async def delete_transaction(tx_id: str) -> dict | None:
    """Delete transaction and return it for balance recalculation."""
    tx = await get_transaction_by_id(tx_id)
    if tx:
        await transactions_collection.delete_one({"_id": ObjectId(tx_id)})
    return tx


async def get_user_categories(telegram_id: int) -> list:
    """Get unique categories used by this user."""
    pipeline = [
        {"$match": {"telegram_id": telegram_id}},
        {"$group": {"_id": "$category"}},
        {"$sort": {"_id": 1}},
    ]
    result = await transactions_collection.aggregate(pipeline).to_list(length=50)
    return [r["_id"] for r in result if r["_id"]]


# ═══════════════════════════════════════
# CUSTOM CATEGORIES OPERATIONS
# ═══════════════════════════════════════

async def get_custom_categories(telegram_id: int) -> list:
    cursor = custom_categories_collection.find({"telegram_id": telegram_id}).sort("name", 1)
    return await cursor.to_list(length=100)


async def add_custom_category(telegram_id: int, emoji: str, name: str, cat_type: str) -> str:
    result = await custom_categories_collection.insert_one({
        "telegram_id": telegram_id,
        "emoji": emoji,
        "name": name,
        "type": cat_type,
        "created_at": datetime.utcnow(),
    })
    return str(result.inserted_id)


async def update_custom_category(cat_id: str, updates: dict):
    await custom_categories_collection.update_one(
        {"_id": ObjectId(cat_id)},
        {"$set": updates}
    )


async def delete_custom_category(cat_id: str):
    await custom_categories_collection.delete_one({"_id": ObjectId(cat_id)})


async def get_custom_category_by_id(cat_id: str) -> dict | None:
    try:
        return await custom_categories_collection.find_one({"_id": ObjectId(cat_id)})
    except Exception:
        return None


# ═══════════════════════════════════════
# DEBT OPERATIONS
# ═══════════════════════════════════════

async def insert_debt(data: dict) -> str:
    data["created_at"] = datetime.utcnow()
    data.setdefault("paid_amount", 0)
    data.setdefault("status", "active")
    result = await debts_collection.insert_one(data)
    return str(result.inserted_id)


async def get_debt_by_id(debt_id: str) -> dict | None:
    try:
        return await debts_collection.find_one({"_id": ObjectId(debt_id)})
    except Exception:
        return None


async def get_active_debts(telegram_id: int, direction: str = None) -> list:
    """
    direction: 'bergan' or 'olgan' or None (all).
    Returns only active/partial debts.
    """
    query = {
        "telegram_id": telegram_id,
        "status": {"$in": ["active", "partial"]},
    }
    if direction:
        query["direction"] = direction
    cursor = debts_collection.find(query).sort("created_at", -1)
    return await cursor.to_list(length=100)


async def update_debt_status(debt_id: str, status: str, paid_amount: float = None):
    update = {"$set": {"status": status, "updated_at": datetime.utcnow()}}
    if paid_amount is not None:
        update["$set"]["paid_amount"] = paid_amount
    await debts_collection.update_one({"_id": ObjectId(debt_id)}, update)


async def update_debt_due_date(debt_id: str, new_due_date: str):
    await debts_collection.update_one(
        {"_id": ObjectId(debt_id)},
        {"$set": {"due_date": new_due_date, "updated_at": datetime.utcnow()}}
    )


async def delete_debt(debt_id: str):
    await debts_collection.update_one(
        {"_id": ObjectId(debt_id)},
        {"$set": {"status": "cancelled", "updated_at": datetime.utcnow()}}
    )


async def get_debts_due_soon(days_ahead: int = 3) -> list:
    """Muddati yaqinlashgan yoki o'tgan qarzlar."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    future = (datetime.utcnow() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    cursor = debts_collection.find({
        "status": {"$in": ["active", "partial"]},
        "due_date": {"$ne": "nomalum", "$ne": None},
    })
    debts = await cursor.to_list(length=500)

    result = []
    for d in debts:
        dd = d.get("due_date", "")
        if not dd or dd == "nomalum":
            continue
        result.append(d)
    return result


async def get_total_debt_by_direction(telegram_id: int, direction: str, currency: str = None) -> float:
    query = {
        "telegram_id": telegram_id,
        "direction": direction,
        "status": {"$in": ["active", "partial"]},
    }
    if currency:
        query["currency"] = currency.upper()

    pipeline = [
        {"$match": query},
        {"$group": {"_id": None, "total": {"$sum": {
            "$subtract": ["$amount", {"$ifNull": ["$paid_amount", 0]}]
        }}}},
    ]
    cursor = debts_collection.aggregate(pipeline)
    result = await cursor.to_list(length=1)
    return result[0]["total"] if result else 0.0


# ═══════════════════════════════════════
# ADMIN & CHANNELS OPERATIONS
# ═══════════════════════════════════════

async def is_admin(telegram_id: int) -> bool:
    if str(telegram_id) == str(config.ADMIN_ID):
        return True
    admin = await admins_collection.find_one({"telegram_id": telegram_id})
    return bool(admin)


async def add_admin(telegram_id: int) -> bool:
    if await is_admin(telegram_id):
        return False
    await admins_collection.insert_one({"telegram_id": telegram_id, "added_at": datetime.utcnow()})
    return True


async def remove_admin(telegram_id: int) -> bool:
    if str(telegram_id) == str(config.ADMIN_ID):
        return False # Cannot remove Super Admin
    result = await admins_collection.delete_one({"telegram_id": telegram_id})
    return result.deleted_count > 0


async def get_all_channels() -> list:
    cursor = channels_collection.find({})
    return await cursor.to_list(length=100)


async def add_channel(link: str, name: str) -> bool:
    exists = await channels_collection.find_one({"link": link})
    if exists:
        return False
    # If link is like https://t.me/kanalnomi, the chat_id checking is easier if we store username
    # We will just store the link and name for the button.
    await channels_collection.insert_one({"link": link, "name": name, "added_at": datetime.utcnow()})
    return True


async def remove_channel(link: str) -> bool:
    result = await channels_collection.delete_one({"link": link})
    return result.deleted_count > 0

async def update_channel_by_index(index: int, new_link: str, new_name: str) -> bool:
    """O'zgartirish index orqali, bu yerda index 0-based"""
    channels = await get_all_channels()
    if index < 0 or index >= len(channels):
        return False
    target_id = channels[index]["_id"]
    await channels_collection.update_one(
        {"_id": target_id},
        {"$set": {"link": new_link, "name": new_name, "updated_at": datetime.utcnow()}}
    )
    return True

async def set_webapp_url(url: str):
    await config_collection.update_one(
        {"_id": "webapp_url"},
        {"$set": {"url": url}},
        upsert=True
    )

async def get_webapp_url() -> str:
    doc = await config_collection.find_one({"_id": "webapp_url"})
    if doc:
        return doc.get("url", "https://google.com")
    return "https://google.com"


# ═══════════════════════════════════════
# STATISTICS OPERATIONS
# ═══════════════════════════════════════

async def get_bot_statistics() -> dict:
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    seven_days_ago = today - timedelta(days=7)

    total_users = await users_collection.count_documents({})
    today_users = await users_collection.count_documents({"created_at": {"$gte": today}})
    active_users = await users_collection.count_documents({"last_active": {"$gte": seven_days_ago}})
    today_messages = await transactions_collection.count_documents({"created_at": {"$gte": today}})
    
    total_txs = await transactions_collection.count_documents({})
    
    # Lang counts
    uz_count = await users_collection.count_documents({"language": "uz"})
    ru_count = await users_collection.count_documents({"language": "ru"})
    en_count = await users_collection.count_documents({"language": "en"})
    
    uz_p = int((uz_count / total_users * 100) if total_users > 0 else 0)
    ru_p = int((ru_count / total_users * 100) if total_users > 0 else 0)
    en_p = int((en_count / total_users * 100) if total_users > 0 else 0)

    return {
        "total_users": total_users,
        "today_users": today_users,
        "active_users": active_users,
        "today_messages": today_messages,
        "today_txs": today_messages,  # For simple mapping
        "total_txs": total_txs,
        "langs": f"UZ: {uz_p}% | RU: {ru_p}% | EN: {en_p}%"
    }

async def get_user_full_stats(telegram_id: int) -> dict:
    user = await users_collection.find_one({"telegram_id": telegram_id})
    if not user:
        return None
        
    tx_count = await transactions_collection.count_documents({"telegram_id": telegram_id})
    
    return {
        "full_name": user.get("full_name", "Noma'lum"),
        "phone": user.get("phone_number", "Noma'lum"),
        "created_at": user.get("created_at", datetime.utcnow()).strftime("%Y-%m-%d"),
        "balances": user.get("balances", {}),
        "tx_count": tx_count,
        "last_active": user.get("last_active", datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S")
    }

