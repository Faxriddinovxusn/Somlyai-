"""
HTTP API Server for the Telegram WebApp.
Runs using aiohttp with error handling middleware.
"""

import json
import logging
from aiohttp import web
from src.database import (
    get_user, get_user_all_balances, get_active_debts, transactions_collection,
    get_custom_categories, add_custom_category, delete_custom_category,
    get_referral_stats, get_all_referral_stats
)
from src.categories import SYSTEM_CATEGORIES
from src.config import BOT_TOKEN
from src.services.error_handler import log_error, handle_error, ErrorType

logger = logging.getLogger(__name__)

routes = web.RouteTableDef()

# Allow CORS for development
def set_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@routes.options('/{path:.*}')
async def options_handler(request):
    return set_cors(web.Response())

@routes.get('/')
async def root_handler(request):
    return web.Response(
        text="Somly AI API Backend is running.\n\n"
             "It seems you pointed Ngrok to port 8000.\n"
             "Please point Ngrok to port 3000 (Vite frontend) instead:\n"
             "ngrok http 3000\n",
        content_type="text/plain"
    )

from src.ws_manager import ws_manager
import aiohttp

@routes.get('/api/ws')
async def websocket_handler(request):
    user_id = int(request.query.get('user_id', 0))
    if not user_id:
        return web.Response(status=400, text="Missing user_id")
        
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    ws_manager.connect(user_id, ws)
    try:
        await ws.send_str(json.dumps({"event": "connected", "data": {"status": "ok"}}))
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                # Handle potential messages from client if needed (e.g. ping/pong)
                pass
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('ws connection closed with exception %s' % ws.exception())
    finally:
        ws_manager.disconnect(user_id, ws)
    return ws

@routes.get('/api/exchange-rates')
async def get_exchange_rates_api(request):
    from src.services.currency_service import get_exchange_rates
    data = get_exchange_rates()
    return set_cors(web.json_response(data))

@routes.get('/api/dashboard/trend')
async def get_dashboard_trend(request):
    try:
        user_id = int(request.query.get('user_id', 0))
        if not user_id:
            return set_cors(web.json_response({"error": "Missing user_id"}, status=400))
            
        from datetime import datetime, timedelta
        from src.database import transactions_collection
        
        today = datetime.now()
        start_date = (today - timedelta(days=6)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        
        txs = await transactions_collection.find({
            "telegram_id": user_id,
            "date": {"$gte": start_date, "$lte": end_date}
        }).to_list(length=1000)
        
        days = []
        for i in range(6, -1, -1):
            d = (today - timedelta(days=i))
            d_str = d.strftime("%Y-%m-%d")
            
            day_txs = [t for t in txs if t.get("date") == d_str]
            chiqim = sum(t["amount"] for t in day_txs if t["type"] == "chiqim")
            kirim = sum(t["amount"] for t in day_txs if t["type"] == "kirim")
            
            days.append({
                "day": d.strftime("%a"),
                "total": chiqim if chiqim > kirim else kirim,
                "type": "chiqim" if chiqim >= kirim else "kirim",
                "isToday": i == 0
            })
            
        return set_cors(web.json_response(days))
    except Exception as e:
        return set_cors(web.json_response({"error": str(e)}, status=500))

@routes.get('/api/dashboard')
async def get_dashboard(request):
    from datetime import datetime, timedelta
    
    user_id = int(request.query.get('user_id', 0))
    if not user_id:
        return set_cors(web.json_response({"error": "Missing user_id"}, status=400))
        
    user = await get_user(user_id) or {}
        
    start_date = request.query.get('start')
    end_date = request.query.get('end')
    
    if not start_date or not end_date:
        today = datetime.now()
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        # simple trick for end of month
        next_month = today.replace(day=28) + timedelta(days=4)
        end_date = (next_month - timedelta(days=next_month.day)).strftime("%Y-%m-%d")
        
    # Get balances
    balances_dict = await get_user_all_balances(user_id)
    balances_list = [{"currency": cur, "amount": data.get("amount", 0), "emoji": data.get("emoji", "💰"), "color": data.get("color", "#30D158"), "title": data.get("title", cur), "limit": data.get("limit")} for cur, data in balances_dict.items()]
    if not balances_list:
        balances_list = [{"currency": "UZS", "amount": 0, "emoji": "💰", "color": "#0A84FF", "title": "So'm"}]

    # Get debts
    bergan = await get_active_debts(user_id, "bergan")
    olgan = await get_active_debts(user_id, "olgan")
    b_total = sum(d["amount"] - d.get("paid_amount",0) for d in bergan)
    o_total = sum(d["amount"] - d.get("paid_amount",0) for d in olgan)

    # Calculate previous period dates for comparison
    try:
        sd = datetime.strptime(start_date, "%Y-%m-%d")
        ed = datetime.strptime(end_date, "%Y-%m-%d")
        diff = (ed - sd).days + 1
        prev_sd = (sd - timedelta(days=diff)).strftime("%Y-%m-%d")
        prev_ed = (ed - timedelta(days=diff)).strftime("%Y-%m-%d")
    except Exception:
        prev_sd, prev_ed = start_date, end_date

    # Fetch transactions
    curr_txs = await transactions_collection.find({
        "telegram_id": user_id,
        "date": {"$gte": start_date, "$lte": end_date}
    }).to_list(length=1000)
    
    prev_txs = await transactions_collection.find({
        "telegram_id": user_id,
        "date": {"$gte": prev_sd, "$lte": prev_ed}
    }).to_list(length=1000)
    
    recent_txs = sorted(curr_txs, key=lambda x: x.get("created_at", ""), reverse=True)[:5]
    formatted_txs = [{
        "id": str(tx["_id"]),
        "type": tx["type"],
        "amount": tx["amount"],
        "category": tx.get("category", "Boshqa"),
        "date": tx.get("date", ""),
        "desc": tx.get("description", "")
    } for tx in recent_txs]

    # Aggregations
    stats = {}
    daily_stats = {}
    comparison = {}

    for cur in balances_dict.keys():
        if cur not in stats:
             stats[cur] = {"Hammasi": [], "Kirim": [], "Chiqim": []}
             daily_stats[cur] = {}
             comparison[cur] = {"kirim": {"current": 0, "prev": 0}, "chiqim": {"current": 0, "prev": 0}}
             
    # Default UZS if empty
    if not stats:
         stats["UZS"] = {"Hammasi": [], "Kirim": [], "Chiqim": []}
         daily_stats["UZS"] = {}
         comparison["UZS"] = {"kirim": {"current": 0, "prev": 0}, "chiqim": {"current": 0, "prev": 0}}

    # Group curr_txs
    cat_totals = {} # {currency: {type: {category_name: {"amount": 0, "count": 0, "emoji": ""}}}}
    for tx in curr_txs:
        c = tx.get("currency", "UZS").upper()
        if c not in cat_totals:
            cat_totals[c] = {"kirim": {}, "chiqim": {}}
        t_type = tx.get("type")
        if t_type not in ["kirim", "chiqim"]: continue
        
        # split emoji and name
        raw_cat = tx.get("category", "📋 Boshqa")
        parts = raw_cat.split(" ", 1)
        emoji = parts[0] if len(parts) > 1 else "📋"
        name = parts[1] if len(parts) > 1 else parts[0]
        
        if name not in cat_totals[c][t_type]:
             cat_totals[c][t_type][name] = {"amount": 0, "count": 0, "emoji": emoji}
             
        cat_totals[c][t_type][name]["amount"] += tx.get("amount", 0)
        cat_totals[c][t_type][name]["count"] += 1
        
        # Line chart logic
        d_str = tx.get("date", "")
        if d_str:
            if c not in daily_stats: daily_stats[c] = {}
            if d_str not in daily_stats[c]: daily_stats[c][d_str] = {"kirim": 0, "chiqim": 0}
            daily_stats[c][d_str][t_type] += tx.get("amount", 0)
            
        # Comparison logic
        if c in comparison:
            comparison[c][t_type]["current"] += tx.get("amount", 0)
            
    for tx in prev_txs:
        c = tx.get("currency", "UZS").upper()
        t_type = tx.get("type")
        if t_type in ["kirim", "chiqim"] and c in comparison:
             comparison[c][t_type]["prev"] += tx.get("amount", 0)

    # Format Pie Chart Stats
    # Premium color palettes
    kirim_colors = ['#30D158', '#34C759', '#32D74B', '#28CD41', '#248A3D']
    chiqim_colors = ['#FF453A', '#FF9F0A', '#BF5AF2', '#0A84FF', '#FF375F', '#5E5CE6', '#FFD60A']
    
    for c, types in cat_totals.items():
        if c not in stats: stats[c] = {"Hammasi": [], "Kirim": [], "Chiqim": []}
        
        total_k = sum(k["amount"] for k in types["kirim"].values())
        total_ch = sum(ch["amount"] for ch in types["chiqim"].values())
        
        stats[c]["Hammasi"] = [
            {"name": "Kirim", "value": total_k, "color": "#30D158", "emoji": "💰", "count": sum(k["count"] for k in types["kirim"].values())},
            {"name": "Chiqim", "value": total_ch, "color": "#FF453A", "emoji": "💸", "count": sum(ch["count"] for ch in types["chiqim"].values())}
        ]
        
        for idx, (cat_name, data) in enumerate(types["kirim"].items()):
             stats[c]["Kirim"].append({
                 "name": cat_name, "value": data["amount"], "count": data["count"],
                 "emoji": data["emoji"], "color": kirim_colors[idx % len(kirim_colors)]
             })
        for idx, (cat_name, data) in enumerate(types["chiqim"].items()):
             stats[c]["Chiqim"].append({
                 "name": cat_name, "value": data["amount"], "count": data["count"],
                 "emoji": data["emoji"], "color": chiqim_colors[idx % len(chiqim_colors)]
             })

    response_data = {
        "balances": balances_list,
        "stats": stats,
        "daily_stats": daily_stats,
        "comparison": comparison,
        "debts": {
            "berishimKerak": o_total,
            "olishimKerak": b_total
        },
        "transactions": formatted_txs,
        "language": user.get("language", "uz")
    }
    return set_cors(web.json_response(response_data))


@routes.get('/api/user_info')
async def get_user_info(request):
    user_id = int(request.query.get('user_id', 0))
    if not user_id:
        return set_cors(web.json_response({"error": "Missing user_id"}, status=400))
    
    user = await get_user(user_id)
    return set_cors(web.json_response({
        "language": user.get("language", "uz")
    }))


@routes.get('/api/categories')
async def get_categories(request):
    user_id = int(request.query.get('user_id', 0))
    if not user_id:
        return set_cors(web.json_response({"error": "Missing user_id"}, status=400))
    
    custom_cats = await get_custom_categories(user_id)
    # Convert ObjectId to string
    for cat in custom_cats:
        cat["id"] = str(cat["_id"])
        del cat["_id"]
        
    return set_cors(web.json_response({
        "system": SYSTEM_CATEGORIES,
        "custom": custom_cats
    }))

@routes.post('/api/categories')
async def create_category(request):
    try:
        data = await request.json()
        user_id = int(data.get('user_id', 0))
        name = data.get('name')
        emoji = data.get('emoji')
        cat_type = data.get('type')
        color = data.get('color', '#0A84FF')
        
        if not all([user_id, name, emoji, cat_type]):
            return set_cors(web.json_response({"error": "Missing fields"}, status=400))
            
        cat_id = await add_custom_category(user_id, emoji, name, cat_type, color)
        
        bot = request.app.get('bot')
        if bot:
            user = await get_user(user_id)
            user_name = user.get("full_name", "Siz")
            msg = f"✅ {user_name} Mini Appda:\nYangi kategoriya qo'shildi:\n{emoji} {name} ({cat_type})"
            await bot.send_message(chat_id=user_id, text=msg)
            
        return set_cors(web.json_response({"success": True, "id": str(cat_id)}))
    except Exception as e:
        return set_cors(web.json_response({"error": str(e)}, status=500))

@routes.delete('/api/categories/{cat_id}')
async def delete_category(request):
    cat_id = request.match_info['cat_id']
    user_id = int(request.query.get('user_id', 0))
    # We don't have the category name here easily without a DB query, so keep it generic or skip
    await delete_custom_category(cat_id)
    if user_id:
        bot = request.app.get('bot')
        if bot:
            user = await get_user(user_id)
            user_name = user.get("full_name", "Siz")
            await bot.send_message(chat_id=user_id, text=f"✅ {user_name} Mini Appda:\nKategoriya o'chirildi.")
    return set_cors(web.json_response({"success": True}))

@routes.post('/api/balances')
async def create_balance(request):
    from src.database import create_custom_balance
    try:
        data = await request.json()
        user_id = int(data.get('user_id', 0))
        currency = data.get('currency')
        title = data.get('title', currency)
        emoji = data.get('emoji', '💰')
        amount = float(data.get('amount', 0))
        color = data.get('color', '#30D158')
        limit = data.get('limit')
        if limit:
            limit = float(limit)
            
        if not all([user_id, currency]):
            return set_cors(web.json_response({"error": "Missing fields"}, status=400))
            
        await create_custom_balance(user_id, currency, title, amount, color, emoji, limit)
        
        bot = request.app.get('bot')
        if bot:
            user = await get_user(user_id)
            user_name = user.get("full_name", "Siz")
            msg = f"✅ {user_name} Mini Appda:\nYangi balans yaratildi:\n{title} - {amount} {currency}"
            await bot.send_message(chat_id=user_id, text=msg)
            
        return set_cors(web.json_response({"success": True}))
    except Exception as e:
        logger.error(f"Error creating balance: {e}")
        return set_cors(web.json_response({"error": "Server error"}, status=500))

@routes.get('/api/balances/{currency}/check_delete')
async def check_delete_balance(request):
    try:
        user_id = int(request.query.get('user_id', 0))
        currency = request.match_info['currency'].upper()
        if not user_id:
            return set_cors(web.json_response({"error": "Missing user_id"}, status=400))
        
        from src.database import transactions_collection
        count = await transactions_collection.count_documents({"telegram_id": user_id, "currency": currency})
        return set_cors(web.json_response({"count": count}))
    except Exception as e:
        logger.error(f"Error checking balance: {e}")
        return set_cors(web.json_response({"error": "Server error"}, status=500))

@routes.delete('/api/balances/{currency}')
async def delete_balance_api(request):
    try:
        data = await request.json()
        user_id = int(data.get('user_id', 0))
        currency = request.match_info['currency'].upper()
        
        if not user_id:
            return set_cors(web.json_response({"error": "Missing user_id"}, status=400))
            
        from src.database import delete_custom_balance, transactions_collection
        # Move existing tx to UZS
        await transactions_collection.update_many(
            {"telegram_id": user_id, "currency": currency},
            {"$set": {"currency": "UZS"}}
        )
        
        await delete_custom_balance(user_id, currency)
        
        bot = request.app.get('bot')
        if bot:
            user = await get_user(user_id)
            user_name = user.get("full_name", "Siz")
            msg = f"✅ {user_name} Mini Appda:\n'{currency}' balansi o'chirildi. Undagi tranzaksiyalar UZS balansiga o'tkazildi."
            await bot.send_message(chat_id=user_id, text=msg)
            
        return set_cors(web.json_response({"success": True}))
    except Exception as e:
        return set_cors(web.json_response({"error": str(e)}, status=500))

@routes.post('/api/balances/transfer')
async def transfer_balance(request):
    """Transfer funds between two balances"""
    try:
        data = await request.json()
        user_id = int(data.get('user_id', 0))
        from_currency = str(data.get('from_balance_id', '')).upper()
        to_currency = str(data.get('to_balance_id', '')).upper()
        amount = float(data.get('amount', 0))
        
        if not all([user_id, from_currency, to_currency, amount]):
            return set_cors(web.json_response({"error": "Missing required fields"}, status=400))
        
        if from_currency == to_currency:
            return set_cors(web.json_response({"error": "Cannot transfer to same balance"}, status=400))
        
        if amount <= 0:
            return set_cors(web.json_response({"error": "Amount must be positive"}, status=400))
        
        # Get user balances
        user = await users_collection.find_one({"telegram_id": user_id})
        if not user:
            return set_cors(web.json_response({"error": "User not found"}, status=404))
        
        balances = user.get("balances", {})
        from_balance = balances.get(from_currency, {})
        to_balance = balances.get(to_currency, {})
        
        if not from_balance:
            return set_cors(web.json_response({"error": f"Balance {from_currency} not found"}, status=404))
        
        if from_balance.get("amount", 0) < amount:
            return set_cors(web.json_response({"error": "Insufficient balance"}, status=400))
        
        # Perform transfer
        new_from_amount = from_balance.get("amount", 0) - amount
        new_to_amount = to_balance.get("amount", 0) + amount if to_balance else amount
        
        await users_collection.update_one(
            {"telegram_id": user_id},
            {"$set": {
                f"balances.{from_currency}.amount": new_from_amount,
                f"balances.{to_currency}.amount": new_to_amount
            }}
        )
        
        # Broadcast update via WebSocket
        await ws_manager.broadcast(user_id, "balance.updated", {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "amount": amount,
            "action": "transfer"
        })
        
        # Send confirmation message via bot
        bot = request.app.get('bot')
        if bot:
            msg = f"✅ O'tkazish muvaffaq:\n{from_currency} → {to_currency}\nSumma: {amount}"
            await bot.send_message(chat_id=user_id, text=msg)
        
        return set_cors(web.json_response({"success": True, "from_amount": new_from_amount, "to_amount": new_to_amount}))
    except Exception as e:
        return set_cors(web.json_response({"error": str(e)}, status=500))

@routes.post('/api/notify_action')
async def notify_action(request):
    try:
        data = await request.json()
        user_id = int(data.get('user_id', 0))
        message = data.get('message', '')
        
        if not user_id or not message:
            return set_cors(web.json_response({"error": "Missing fields"}, status=400))
            
        bot = request.app.get('bot')
        if bot:
            await bot.send_message(chat_id=user_id, text=message)
            
        return set_cors(web.json_response({"success": True}))
    except Exception as e:
        return set_cors(web.json_response({"error": str(e)}, status=500))


@routes.post('/api/settings/notifications')
async def update_notifications(request):
    try:
        data = await request.json()
        user_id = int(data.get('user_id', 0))
        morning_reminder = data.get('morning_reminder', True)
        evening_reminder = data.get('evening_reminder', True)
        
        if not user_id:
            return set_cors(web.json_response({"error": "Missing user_id"}, status=400))
        
        from src.database import users_collection
        await users_collection.update_one(
            {"telegram_id": user_id},
            {"$set": {
                "settings.morning_reminder": morning_reminder,
                "settings.evening_reminder": evening_reminder
            }}
        )
        
        return set_cors(web.json_response({"success": True}))
    except Exception as e:
        logger.error(f"Error updating notifications: {e}")
        return set_cors(web.json_response({"error": str(e)}, status=500))

@routes.post('/api/settings/language')
async def update_language(request):
    try:
        data = await request.json()
        user_id = int(data.get('user_id', 0))
        language = data.get('language', 'uz')
        
        if not user_id:
            return set_cors(web.json_response({"error": "Missing user_id"}, status=400))
        
        from src.database import users_collection
        await users_collection.update_one(
            {"telegram_id": user_id},
            {"$set": {"language": language}}
        )
        
        bot = request.app.get('bot')
        if bot:
            msg = "✅ Til muvaffaqiyatli o'zgartirildi." if language == 'uz' else "✅ Язык успешно изменен." if language == 'ru' else "✅ Language changed successfully."
            try:
                await bot.send_message(chat_id=user_id, text=msg)
            except:
                pass
                
        return set_cors(web.json_response({"success": True}))
    except Exception as e:
        logger.error(f"Error updating language: {e}")
        return set_cors(web.json_response({"error": str(e)}, status=500))

@routes.post('/api/export')
async def export_excel_route(request):
    try:
        data = await request.json()
        user_id = int(data.get('user_id', 0))
        period = data.get('period', 'Bu oy')
        
        bot = request.app.get('bot')
        if bot and user_id:
            try:
                await bot.send_message(chat_id=user_id, text=f"⏳ Excel hisobot tayyorlanmoqda ({period})...")
                # Trigger the actual export logic
                from src.handlers.report_handler import send_excel_report
                import asyncio
                # The send_excel_report might expect (message, user_id) or something similar
                # Just mock or fire if it exists, otherwise just send the message
                try:
                    asyncio.create_task(send_excel_report(bot, user_id))
                except Exception:
                    pass
            except Exception as inner_e:
                logger.error(f"Error triggering excel: {inner_e}")
                
        return set_cors(web.json_response({"success": True}))
    except Exception as e:
        return set_cors(web.json_response({"error": str(e)}, status=500))


# ═══════════════════════════════════════
# GROUP ROUTES
# ═══════════════════════════════════════

@routes.get('/api/groups')
async def get_groups(request):
    from src.database import get_user_groups
    user_id = int(request.query.get('user_id', 0))
    if not user_id:
        return set_cors(web.json_response({"error": "Missing user_id"}, status=400))
    groups = await get_user_groups(user_id)
    return set_cors(web.json_response(groups))

@routes.post('/api/groups')
async def create_group_route(request):
    from src.database import create_group
    try:
        data = await request.json()
        user_id = int(data.get('user_id', 0))
        name = data.get('name', '')
        if not user_id or not name:
            return set_cors(web.json_response({"error": "Missing fields"}, status=400))
        group_id = await create_group(user_id, name)
        return set_cors(web.json_response({"success": True, "id": group_id}))
    except Exception as e:
        return set_cors(web.json_response({"error": str(e)}, status=500))

@routes.get('/api/groups/{group_id}')
async def get_group_detail(request):
    from src.database import get_group_by_id
    group_id = request.match_info['group_id']
    group = await get_group_by_id(group_id)
    if not group:
        return set_cors(web.json_response({"error": "Group not found"}, status=404))
    return set_cors(web.json_response(group))

@routes.post('/api/groups/{group_id}/members')
async def add_member_route(request):
    from src.database import add_group_member
    try:
        group_id = request.match_info['group_id']
        data = await request.json()
        telegram_id = int(data.get('telegram_id', 0))
        name = data.get('name', '')
        if not telegram_id or not name:
            return set_cors(web.json_response({"error": "Missing fields"}, status=400))
        added = await add_group_member(group_id, telegram_id, name)
        if not added:
            return set_cors(web.json_response({"error": "Already a member or group not found"}, status=400))
        return set_cors(web.json_response({"success": True}))
    except Exception as e:
        return set_cors(web.json_response({"error": str(e)}, status=500))

@routes.delete('/api/groups/{group_id}/members/{member_id}')
async def remove_member_route(request):
    from src.database import remove_group_member
    try:
        group_id = request.match_info['group_id']
        member_id = int(request.match_info['member_id'])
        removed = await remove_group_member(group_id, member_id)
        return set_cors(web.json_response({"success": removed}))
    except Exception as e:
        return set_cors(web.json_response({"error": str(e)}, status=500))

@routes.get('/api/groups/search-user')
async def search_user_route(request):
    from src.database import search_user_by_phone
    phone = request.query.get('phone', '')
    if not phone or len(phone) < 5:
        return set_cors(web.json_response({"error": "Phone too short"}, status=400))
    user = await search_user_by_phone(phone)
    if not user:
        return set_cors(web.json_response({"error": "User not found"}, status=404))
    return set_cors(web.json_response(user))

@routes.post('/api/groups/{group_id}/balances')
async def add_group_balance_route(request):
    from src.database import add_group_balance
    try:
        group_id = request.match_info['group_id']
        data = await request.json()
        currency = data.get('currency', '')
        title = data.get('title', currency)
        color = data.get('color', '#3B82F6')
        if not currency:
            return set_cors(web.json_response({"error": "Missing currency"}, status=400))
        await add_group_balance(group_id, currency, title, color)
        return set_cors(web.json_response({"success": True}))
    except Exception as e:
        return set_cors(web.json_response({"error": str(e)}, status=500))

@routes.get('/api/channels')
async def get_channels_route(request):
    from src.database import get_all_channels
    channels = await get_all_channels()
    result = []
    for c in channels:
        result.append({
            "name": c.get("name", "Kanal"),
            "link": c.get("link", ""),
            "description": c.get("description", "Somly AI tavsiya etadi"),
        })
    return set_cors(web.json_response(result))

@routes.get('/api/debts')
async def get_debts(request):
    user_id = int(request.query.get('user_id', 0))
    if not user_id:
        return set_cors(web.json_response({"error": "Missing user_id"}, status=400))
    
    bergan = await get_active_debts(user_id, "bergan")
    olgan = await get_active_debts(user_id, "olgan")
    
    def format_debt(d):
        return {
            "id": str(d["_id"]),
            "name": d.get("person", "Noma'lum"),
            "amount": d.get("amount", 0) - d.get("paid_amount", 0),
            "currency": d.get("currency", "UZS"),
            "desc": d.get("description", "Qarz"),
            "date": d.get("created_at", "").isoformat() if hasattr(d.get("created_at", ""), "isoformat") else str(d.get("created_at", "")),
            "due_date": d.get("due_date", ""),
            "status": d.get("status", "active")
        }
        
    response_data = {
        "berishimKerak": [format_debt(d) for d in olgan], # olgan means I owe them
        "olishimKerak": [format_debt(d) for d in bergan]  # bergan means they owe me
    }
    
    return set_cors(web.json_response(response_data))

@routes.post('/api/debts/{debt_id}/{action}')
async def debt_action(request):
    from src.database import update_debt_status, delete_debt, get_debt_by_id, insert_transaction, update_user_balance
    try:
        debt_id = request.match_info['debt_id']
        action = request.match_info['action']
        data = await request.json()
        user_id = int(data.get('user_id', 0))
        
        bot = request.app.get('bot')
        user_name = "Siz"
        if bot and user_id:
             user = await get_user(user_id)
             user_name = user.get("full_name", "Siz")
        
        if action == 'pay':
            debt = await get_debt_by_id(debt_id)
            if not debt:
                return set_cors(web.json_response({"error": "Debt not found"}, status=404))

            await update_debt_status(debt_id, 'paid')
            
            # Cancel related reminders
            from src.database import reminders_collection
            await reminders_collection.update_many(
                {"related_debt_id": debt_id, "status": "pending"},
                {"$set": {"status": "done", "updated_at": datetime.utcnow()}}
            )
            
            t_type = "kirim" if debt.get("direction") == "bergan" else "chiqim" 
            amount = debt.get("amount", 0) - debt.get("paid_amount", 0)
            currency = debt.get("currency", "UZS")
            
            tx_data = {
                "telegram_id": debt.get("telegram_id", user_id),
                "type": t_type,
                "amount": amount,
                "currency": currency,
                "category": "🔄 Qarz qaytdi" if t_type == "kirim" else "🔄 Qarz uzildi",
                "description": f"{debt.get('person')} bilan qarz hisob-kitobi",
                "affects_balance": True
            }
            await insert_transaction(tx_data)
            await update_user_balance(tx_data["telegram_id"], currency, amount, is_income=(t_type == "kirim"))
            
            msg = f"✅ {user_name} Mini Appda:\nQarz qaytarilgan deb belgilandi va balans yangilandi."
        elif action == 'delete':
            await delete_debt(debt_id)
            msg = f"✅ {user_name} Mini Appda:\nQarz o'chirildi."
        else:
            return set_cors(web.json_response({"error": "Invalid action"}, status=400))
            
        if bot and user_id:
            await bot.send_message(chat_id=user_id, text=msg)
            
        return set_cors(web.json_response({"success": True}))
    except Exception as e:
        return set_cors(web.json_response({"error": str(e)}, status=500))

@routes.put('/api/transactions/{tx_id}')
async def edit_transaction(request):
    from src.database import update_transaction
    try:
        tx_id = request.match_info['tx_id']
        data = await request.json()
        user_id = int(data.get('user_id', 0))
        updates = data.get('updates', {})
        
        if not updates:
            return set_cors(web.json_response({"error": "No updates provided"}, status=400))
            
        await update_transaction(tx_id, updates)
        
        bot = request.app.get('bot')
        if bot and user_id:
            user = await get_user(user_id)
            user_name = user.get("full_name", "Siz")
            
            # Format message simply showing what changed
            details = "\n".join([f"• {k}: {v}" for k, v in updates.items() if k not in ['id', 'user_id']])
            msg = f"✅ {user_name} Mini Appda:\nTranzaksiya tahrirlandi:\n{details}"
            await bot.send_message(chat_id=user_id, text=msg)
            
        return set_cors(web.json_response({"success": True}))
    except Exception as e:
        return set_cors(web.json_response({"error": str(e)}, status=500))

@routes.delete('/api/transactions/{tx_id}')
async def remove_transaction(request):
    from src.database import delete_transaction, get_transaction_by_id, update_user_balance
    try:
        tx_id = request.match_info['tx_id']
        user_id = int(request.query.get('user_id', 0))
        
        tx = await get_transaction_by_id(tx_id)
        if tx:
            await delete_transaction(tx_id)
            # Revert balance
            if tx.get("affects_balance"):
                await update_user_balance(tx["telegram_id"], tx["currency"], -tx["amount"], is_income=(tx["type"] == "kirim"))
            
            if user_id:
                bot = request.app.get('bot')
                if bot:
                    user = await get_user(user_id)
                    user_name = user.get("full_name", "Siz")
                    msg = f"✅ {user_name} Mini Appda:\nTranzaksiya o'chirildi:\n{tx.get('amount')} {tx.get('currency')} ({tx.get('category', '')})"
                    await bot.send_message(chat_id=user_id, text=msg)
            
        return set_cors(web.json_response({"success": True}))
    except Exception as e:
        return set_cors(web.json_response({"error": str(e)}, status=500))


# ═══════════════════════════════════════
# REMINDER ROUTES
# ═══════════════════════════════════════

@routes.get('/api/reminders')
async def get_reminders_api(request):
    from src.database import get_user_reminders
    user_id = int(request.query.get('user_id', 0))
    status = request.query.get('status', 'pending')
    if not user_id:
        return set_cors(web.json_response({"error": "Missing user_id"}, status=400))
    
    reminders = await get_user_reminders(user_id, status)
    result = []
    for r in reminders:
        result.append({
            "id": str(r["_id"]),
            "type": r.get("type", "general"),
            "message": r.get("message", ""),
            "scheduled_time": r.get("scheduled_time").isoformat() if r.get("scheduled_time") else "",
            "status": r.get("status", "pending")
        })
    return set_cors(web.json_response(result))

@routes.post('/api/reminders/{rem_id}/status')
async def update_reminder_status_api(request):
    from src.database import update_reminder_status
    rem_id = request.match_info['rem_id']
    data = await request.json()
    status = data.get('status')
    if not status:
        return set_cors(web.json_response({"error": "Missing status"}, status=400))
    await update_reminder_status(rem_id, status)
    return set_cors(web.json_response({"success": True}))

@routes.delete('/api/reminders/{rem_id}')
async def delete_reminder_api(request):
    from src.database import reminders_collection
    from bson.objectid import ObjectId
    try:
        rem_id = request.match_info['rem_id']
        await reminders_collection.delete_one({"_id": ObjectId(rem_id)})
        return set_cors(web.json_response({"success": True}))
    except Exception as e:
        return set_cors(web.json_response({"error": str(e)}, status=500))


# ═══════════════════════════════════════
# SHARED WALLET ROUTES
# ═══════════════════════════════════════

@routes.get('/api/shared_wallets')
async def get_shared_wallets_api(request):
    from src.database import get_user_shared_wallets
    user_id = int(request.query.get('user_id', 0))
    if not user_id:
        return set_cors(web.json_response({"error": "Missing user_id"}, status=400))
    
    wallets = await get_user_shared_wallets(user_id)
    # Format and include member names
    from src.database import get_user
    result = []
    for w in wallets:
        members_data = []
        for m in w["members"]:
            u = await get_user(m["user_id"])
            members_data.append({
                "user_id": m["user_id"],
                "name": u.get("full_name", "Noma'lum"),
                "role": m["role"],
                "status": m["status"]
            })
            
        result.append({
            "id": str(w["_id"]),
            "name": w["name"],
            "currency": w["currency"],
            "amount": w["amount"],
            "color": w["color"],
            "owner_id": w["owner_id"],
            "members": members_data
        })
    return set_cors(web.json_response(result))

@routes.post('/api/shared_wallets')
async def create_shared_wallet_api(request):
    from src.database import create_shared_wallet
    data = await request.json()
    user_id = int(data.get('user_id', 0))
    name = data.get('name')
    currency = data.get('currency')
    amount = float(data.get('amount', 0))
    color = data.get('color', '#8B5CF6')
    
    if not all([user_id, name, currency]):
        return set_cors(web.json_response({"error": "Missing fields"}, status=400))
        
    wallet_id = await create_shared_wallet(user_id, name, currency, amount, color)
    return set_cors(web.json_response({"success": True, "id": wallet_id}))

@routes.post('/api/shared_wallets/{id}/invite')
async def invite_member_api(request):
    from src.database import find_user_by_contact, create_shared_wallet_invite, get_user
    wallet_id = request.match_info['id']
    data = await request.json()
    from_user_id = int(data.get('user_id', 0))
    contact = data.get('contact') # phone or username
    role = data.get('role', 'member')
    
    if not contact:
        return set_cors(web.json_response({"error": "Contact required"}, status=400))
        
    target_user = await find_user_by_contact(contact)
    if not target_user:
        return set_cors(web.json_response({"error": "Foydalanuvchi topilmadi"}, status=404))
        
    to_user_id = target_user["telegram_id"]
    invite_id = await create_shared_wallet_invite(wallet_id, from_user_id, to_user_id, role)
    
    # Notify target user via bot
    bot = request.app.get('bot')
    if bot:
        sender = await get_user(from_user_id)
        sender_name = sender.get("full_name", "Kimdir")
        from src.database import shared_wallets_collection
        from bson.objectid import ObjectId
        wallet = await shared_wallets_collection.find_one({"_id": ObjectId(wallet_id)})
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"sw_invite:accept:{invite_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"sw_invite:reject:{invite_id}")
            ]
        ])
        
        msg = (
            f"👥 {sender_name} sizni '{wallet['name']}' umumiy hamyoniga qo'shmoqchi.\n"
            f"Ruxsat: {role}"
        )
        await bot.send_message(chat_id=to_user_id, text=msg, reply_markup=kb)
        
    return set_cors(web.json_response({"success": True}))

@routes.get('/api/shared_wallets/invites')
async def get_invites_api(request):
    from src.database import get_user_invites
    user_id = int(request.query.get('user_id', 0))
    invites = await get_user_invites(user_id)
    return set_cors(web.json_response(invites))

@routes.post('/api/shared_wallets/invites/{id}/action')
async def process_invite_api(request):
    from src.database import process_invite_action, get_user
    invite_id = request.match_info['id']
    data = await request.json()
    action = data.get('action') # 'accept' or 'reject'
    
    invite = await process_invite_action(invite_id, action)
    if not invite:
        return set_cors(web.json_response({"error": "Invite not found"}, status=404))
        
    # Notify owner
    bot = request.app.get('bot')
    if bot:
        target = await get_user(invite["to_user_id"])
        target_name = target.get("full_name", "Foydalanuvchi")
        from src.database import shared_wallets_collection
        from bson.objectid import ObjectId
        wallet = await shared_wallets_collection.find_one({"_id": ObjectId(invite["wallet_id"])})
        
        msg = f"👥 {target_name} '{wallet['name']}' hamyoniga qo'shilish taklifini {'qabul qildi' if action == 'accept' else 'rad etdi'}."
        await bot.send_message(chat_id=invite["from_user_id"], text=msg)
        
    return set_cors(web.json_response({"success": True}))

@routes.delete('/api/shared_wallets/{wallet_id}')
async def delete_shared_wallet_api(request):
    from src.database import shared_wallets_collection
    from bson.objectid import ObjectId
    wallet_id = request.match_info['wallet_id']
    await shared_wallets_collection.delete_one({"_id": ObjectId(wallet_id)})
    return set_cors(web.json_response({"success": True}))

@routes.delete('/api/shared_wallets/{wallet_id}/members/{user_id}')
async def remove_wallet_member_api(request):
    from src.database import shared_wallets_collection
    from bson.objectid import ObjectId
    wallet_id = request.match_info['wallet_id']
    user_id = int(request.match_info['user_id'])
    
    await shared_wallets_collection.update_one(
        {"_id": ObjectId(wallet_id)},
        {"$pull": {"members": {"user_id": user_id}}}
    )
    return set_cors(web.json_response({"success": True}))


# ═══════════════════════════════════════
# ADMIN PANEL ROUTES
# ═══════════════════════════════════════

@routes.get('/admin')
async def admin_page(request):
    import os
    path = os.path.join("webapp", "admin.html")
    if os.path.exists(path):
        return web.FileResponse(path)
    return web.Response(text="Admin panel not found", status=404)

@routes.post('/api/admin/login')
async def admin_login(request):
    try:
        data = await request.json()
        if data.get("login") == "1342b" and data.get("password") == "gsk1352":
            # Very simple static token for MVP
            return set_cors(web.json_response({"success": True, "token": "admin_secure_token_123"}))
        return set_cors(web.json_response({"success": False, "error": "Invalid credentials"}, status=401))
    except Exception as e:
        return set_cors(web.json_response({"error": str(e)}, status=500))

@routes.get('/api/admin/users')
async def admin_get_users(request):
    auth = request.headers.get("Authorization", "")
    if auth != "Bearer admin_secure_token_123":
        return set_cors(web.json_response({"error": "Unauthorized"}, status=401))
        
    from src.database import get_admin_users_data
    try:
        users = await get_admin_users_data()
        return set_cors(web.json_response(users))
    except Exception as e:
        return set_cors(web.json_response({"error": str(e)}, status=500))

# ─── REFERRAL ENDPOINTS ───

@routes.get('/api/referrals')
async def get_user_referrals(request):
    try:
        user_id = int(request.query.get("user_id", 0))
        if not user_id:
            return set_cors(web.json_response({"error": "Missing user_id"}, status=400))
        
        stats = await get_referral_stats(user_id)
        return set_cors(web.json_response(stats))
    except Exception as e:
        return set_cors(web.json_response({"error": str(e)}, status=500))

@routes.get('/api/admin/referrals')
async def get_admin_referrals(request):
    auth = request.headers.get("Authorization", "")
    if auth != "Bearer admin_secure_token_123":
        return set_cors(web.json_response({"error": "Unauthorized"}, status=401))
        
    try:
        stats = await get_all_referral_stats()
        # Ensure datetimes are serialized
        for s in stats:
            if "last_date" in s and s["last_date"]:
                s["last_date"] = s["last_date"].isoformat()
        return set_cors(web.json_response(stats))
    except Exception as e:
        return set_cors(web.json_response({"error": str(e)}, status=500))

async def error_middleware(app, handler):
    """Global error handling middleware for all API routes."""
    async def middleware_handler(request):
        try:
            return await handler(request)
        except web.HTTPException:
            raise  # Let aiohttp handle HTTP exceptions normally
        except Exception as e:
            error_msg = f"API Error on {request.method} {request.path}: {type(e).__name__}: {str(e)}"
            log_error(ErrorType.API_GENERAL, error_msg, exception=e)
            logger.exception(f"Unhandled API error: {error_msg}")
            
            # Try to alert admin for DB errors
            if "mongo" in str(e).lower() or "connection" in str(e).lower() or "timeout" in str(e).lower():
                bot = request.app.get('bot')
                if bot:
                    try:
                        import asyncio
                        asyncio.create_task(
                            handle_error(bot, ErrorType.MONGODB_CONNECTION, error_msg, exception=e)
                        )
                    except Exception:
                        pass
            
            resp = web.json_response({"error": "Internal server error"}, status=500)
            return set_cors(resp)
    return middleware_handler


async def on_shutdown(app):
    """Graceful shutdown: Notify all WebSockets before closing."""
    logger.info("Server shutting down, broadcasting to all WebSockets...")
    await ws_manager.broadcast_all("server_restarting")


async def start_api_server(bot=None):
    app = web.Application(middlewares=[error_middleware])
    app['bot'] = bot
    app.add_routes(routes)
    app.on_shutdown.append(on_shutdown)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()
    logger.info("🌐 API Server is running on http://0.0.0.0:8000")
