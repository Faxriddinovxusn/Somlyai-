"""
HTTP API Server for the Telegram WebApp.
Runs using aiohttp.
"""

import json
from aiohttp import web
from src.database import (
    get_user, get_user_all_balances, get_active_debts, transactions_collection,
    get_custom_categories, add_custom_category, delete_custom_category
)
from src.categories import SYSTEM_CATEGORIES
from src.config import BOT_TOKEN
# For real Telegram auth validation, we'd use hashlib and hmac with BOT_TOKEN.
# To keep this simple and robust for this demo, we mock auth or just parse user_id.

routes = web.RouteTableDef()

# Allow CORS for development
def set_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@routes.options('/{path:.*}')
async def options_handler(request):
    return set_cors(web.Response())

@routes.get('/api/dashboard')
async def get_dashboard(request):
    # In production, parse initData. For now, take from query or default.
    user_id = int(request.query.get('user_id', 0))
    if not user_id:
        return set_cors(web.json_response({"error": "Missing user_id"}, status=400))
    
    # Get balances
    balances_dict = await get_user_all_balances(user_id)
    balances_list = []
    for cur, data in balances_dict.items():
        balances_list.append({"currency": cur, "amount": data.get("amount", 0)})
    
    if not balances_list:
        balances_list = [{"currency": "UZS", "amount": 0}]

    # Get debts
    bergan = await get_active_debts(user_id, "bergan")
    olgan = await get_active_debts(user_id, "olgan")
    
    b_total = sum(d["amount"] - d.get("paid_amount",0) for d in bergan)
    o_total = sum(d["amount"] - d.get("paid_amount",0) for d in olgan)

    # Get recent transactions
    cursor = transactions_collection.find({"telegram_id": user_id}).sort("created_at", -1).limit(5)
    txs = await cursor.to_list(length=5)
    formatted_txs = []
    for tx in txs:
        formatted_txs.append({
            "id": str(tx["_id"]),
            "type": tx["type"],
            "amount": tx["amount"],
            "category": tx.get("category", "Boshqa"),
            "date": tx.get("date", "")
        })

    # Mock stats for the pie chart for now
    stats = [
        {"name": "Kirim", "value": 1, "color": "#30D158"},
        {"name": "Chiqim", "value": 1, "color": "#FF453A"}
    ]

    response_data = {
        "balances": balances_list,
        "stats": stats,
        "debts": {
            "berishimKerak": o_total,
            "olishimKerak": b_total
        },
        "transactions": formatted_txs
    }

    return set_cors(web.json_response(response_data))


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
        
        if not all([user_id, name, emoji, cat_type]):
            return set_cors(web.json_response({"error": "Missing fields"}, status=400))
            
        cat_id = await add_custom_category(user_id, emoji, name, cat_type)
        return set_cors(web.json_response({"success": True, "id": cat_id}))
    except Exception as e:
        return set_cors(web.json_response({"error": str(e)}, status=500))

@routes.delete('/api/categories/{cat_id}')
async def delete_category(request):
    cat_id = request.match_info['cat_id']
    await delete_custom_category(cat_id)
    return set_cors(web.json_response({"success": True}))


async def start_api_server():
    app = web.Application()
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()
    print("🌐 API Server is running on http://0.0.0.0:8000")
