"""
Admin operations handler.
Commands:
- /stats
- /user [id]
- /admin [id]
- /remove_admin [id]
- /channels
- /add_channel [link] [nomi]
- /setchannel [num] [link_yoki_username]
- /remove_channel [link]
- /send (fsm: waiting for message, then confirm)
- /setwebapp [link]
"""

import asyncio
from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import Message, MenuButtonWebApp, WebAppInfo, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.database import (
    is_admin, add_admin, remove_admin,
    add_channel, remove_channel, get_all_channels, update_channel_by_index,
    get_bot_statistics, get_user_full_stats, users_collection
)
from src.config import ADMIN_ID

router = Router()

class BroadcastState(StatesGroup):
    waiting_for_message = State()

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not await is_admin(message.from_user.id):
        return
    stats = await get_bot_statistics()
    text = (
        f"📊 <b>Somly AI statistikasi:</b>\n"
        f"👥 Jami foydalanuvchilar: {stats['total_users']:,}\n"
        f"📅 Bugun qo'shilganlar: {stats['today_users']:,}\n"
        f"🔄 Aktiv (7 kun): {stats['active_users']:,}\n"
        f"💬 Bugungi xabarlar: {stats['today_messages']:,}\n"
        f"📊 Bugungi tranzaksiyalar: {stats['today_txs']:,}\n"
        f"💰 Jami tranzaksiyalar: {stats['total_txs']:,}\n"
        f"🌍 Tillar: {stats['langs']}"
    )
    await message.answer(text, parse_mode="HTML")

@router.message(Command("user"))
async def cmd_user(message: Message):
    if not await is_admin(message.from_user.id):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Xato! Format: /user [telegram_id]")
        return
    try:
        user_id = int(args[1])
        u_stats = await get_user_full_stats(user_id)
        if not u_stats:
            await message.answer("❌ Foydalanuvchi topilmadi.")
            return
            
        b_uzs = u_stats['balances'].get('UZS', {}).get('amount', 0)
        b_usd = u_stats['balances'].get('USD', {}).get('amount', 0)
        
        text = (
            f"👤 Foydalanuvchi: {u_stats['full_name']}\n"
            f"📱 Telefon: {u_stats['phone']}\n"
            f"📅 Ro'yxat: {u_stats['created_at']}\n"
            f"💰 Balans: {b_uzs:,} UZS | {b_usd:,} USD\n"
            f"📊 Tranzaksiyalar: {u_stats['tx_count']}\n"
            f"🔄 Oxirgi faollik: {u_stats['last_active']}"
        )
        await message.answer(text)
    except ValueError:
        await message.answer("❌ ID faqat raqamlardan iborat bo'lishi kerak.")

@router.message(Command("channels"))
async def cmd_channels(message: Message):
    if not await is_admin(message.from_user.id):
        return
    channels = await get_all_channels()
    if not channels:
        await message.answer("Hozircha kanallar yo'q.")
        return
        
    msg = "<b>Hozirgi kanallar:</b>\n"
    for idx, c in enumerate(channels, 1):
        msg += f"{idx}. {c['name']} ({c['link']})\n"
    
    msg += "\nO'zgartirish: <code>/setchannel 1 @yangi_kanal</code>"
    await message.answer(msg, parse_mode="HTML")

@router.message(Command("setchannel"))
async def cmd_setchannel(message: Message):
    if not await is_admin(message.from_user.id):
        return
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("Xato! Format: /setchannel [tartib_raqami] [@kanal_yoki_link] [Kanal nomi - ixtiyoriy]")
        return
        
    try:
        index = int(args[1]) - 1
        new_link = args[2]
        new_name = "Yangi kanal" if len(args) == 3 else args[2] # If name provided
        
        # Check if they provided a 4th arg for name implicitly
        if not new_link.startswith("http") and not new_link.startswith("@"):
             await message.answer("Link @ bilan yoki https bilan boshlanishi kerak.")
             return
             
        channels = await get_all_channels()
        if index < 0 or index >= len(channels):
             await message.answer("❌ Bunday raqamli kanal yo'q. /channels orqali raqamlarni ko'ring.")
             return
             
        if await update_channel_by_index(index, new_link, new_name):
             await message.answer(f"✅ {index+1}-kanal o'zgartirildi: {new_link}")
        else:
             await message.answer("❌ Xatolik yuz berdi.")
             
    except ValueError:
        await message.answer("❌ Tartib raqami son bo'lishi kerak.")

@router.message(Command("admin"))
async def cmd_add_admin(message: Message):
    if not await is_admin(message.from_user.id):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Xato! Format: /admin [telegram_id]")
        return
    try:
        new_admin_id = int(args[1])
        if await add_admin(new_admin_id):
            await message.answer(f"✅ {new_admin_id} adminlar ro'yxatiga qo'shildi.")
        else:
            await message.answer("❌ Bu ID allaqachon admin yoki xatolik.")
    except ValueError:
        await message.answer("❌ ID faqat raqamlardan iborat bo'lishi kerak.")


@router.message(Command("remove_admin"))
async def cmd_remove_admin(message: Message):
    if not await is_admin(message.from_user.id):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Xato! Format: /remove_admin [telegram_id]")
        return
    try:
        target_id = int(args[1])
        if await remove_admin(target_id):
            await message.answer(f"✅ {target_id} adminlikdan o'chirildi.")
        else:
            await message.answer("❌ Bosh adminni o'chirib bo'lmaydi yoki bunday admin yo'q.")
    except ValueError:
        await message.answer("❌ ID faqat raqamlardan iborat bo'lishi kerak.")


@router.message(Command("add_channel"))
async def cmd_add_channel(message: Message):
    if not await is_admin(message.from_user.id):
        return
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("Xato! Format: /add_channel [link] [Kanal nomi]")
        return
    
    link = args[1]
    name = args[2]
    
    if await add_channel(link, name):
        await message.answer(f"✅ Kanal qo'shildi!\nNom: {name}\nLink: {link}\n\nEslatma: Botni shu kanalga admin qilishni unutmang!")
    else:
        await message.answer("❌ Bu kanal allaqachon qo'shilgan.")


@router.message(Command("remove_channel"))
async def cmd_remove_channel(message: Message):
    if not await is_admin(message.from_user.id):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        # Show all channels to help
        channels = await get_all_channels()
        if not channels:
            await message.answer("Hozircha kanallar yo'q.")
            return
        msg = "Qaysi kanalni o'chirmoqchisiz?\nFormat: /remove_channel [link]\n\nMavjud kanallar:\n"
        for c in channels:
            msg += f"- {c['name']} : {c['link']}\n"
        await message.answer(msg)
        return
    
    link = args[1]
    if await remove_channel(link):
        await message.answer("✅ Kanal olib tashlandi.")
    else:
        await message.answer("❌ Bunday link topilmadi.")


# ─── BROADCAST SYSTEM ───

@router.message(Command("send"))
async def cmd_send(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    await state.set_state(BroadcastState.waiting_for_message)
    await message.answer("📣 Yuboriladigan xabarni (rasm, video, matn) yuboring.\nBekor qilish uchun /cancel bosing.")


@router.message(BroadcastState.waiting_for_message)
async def process_broadcast_message(message: Message, state: FSMContext, bot: Bot):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Xabar yuborish bekor qilindi.")
        return

    await state.clear()
    
    total_users = await users_collection.count_documents({"is_active": True})
    
    # Kbd confirmation
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yuborish", callback_data="confirm_send"),
            InlineKeyboardButton(text="❌ Bekor", callback_data="cancel_send")
        ]
    ])
    
    # Saqlab qoyamiz message detailsni state data ichiga
    await state.update_data(broadcast_msg_id=message.message_id, broadcast_chat_id=message.chat.id, total_users=total_users)
    
    await message.answer(
        f"{total_users} ta foydalanuvchiga yuborilsinmi?\n\n<i>Yuborayotgan xabaringiz yuqorida.</i>",
        reply_markup=kb, parse_mode="HTML"
    )

@router.callback_query(F.data == "confirm_send")
async def confirm_send_callback(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if not await is_admin(callback.from_user.id):
        return
        
    data = await state.get_data()
    msg_id = data.get("broadcast_msg_id")
    chat_id = data.get("broadcast_chat_id")
    total_users = data.get("total_users", 0)
    
    if not msg_id:
        await callback.message.edit_text("❌ Xato! Xabar topilmadi.")
        return
        
    await callback.message.edit_text(f"⏳ Yuborilmoqda: 0 / {total_users}")
    
    cursor = users_collection.find({"is_active": True})
    users = await cursor.to_list(length=100000)
    
    success_count = 0
    fail_count = 0
    
    for i, user in enumerate(users, 1):
        try:
            await bot.copy_message(
                chat_id=user["telegram_id"],
                from_chat_id=chat_id,
                message_id=msg_id
            )
            success_count += 1
        except Exception:
            fail_count += 1
            
        # Update progress every 50 users or at the end
        if i % 50 == 0 or i == total_users:
            try:
                await callback.message.edit_text(f"⏳ Yuborildi: {success_count} / {total_users}\n(Xato: {fail_count})")
            except Exception:
                pass # Ignore if same message content error
                
        await asyncio.sleep(0.05) # Rate limit
            
    await callback.message.edit_text(f"✅ Tarqatish yakunlandi!\n\nJo'natildi: {success_count} ta\nXato: {fail_count} ta")
    await state.clear()

@router.callback_query(F.data == "cancel_send")
async def cancel_send_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Yuborish bekor qilindi.")
    await state.clear()


@router.message(Command("setwebapp"))
async def cmd_setwebapp(message: Message, bot: Bot):
    if not await is_admin(message.from_user.id):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Xato! Format: /setwebapp [link]\nMasalan: /setwebapp https://...ngrok-free.app")
        return
    url = args[1]
    if not url.startswith("https://"):
        await message.answer("❌ Xato! Link 'https://' bilan boshlanishi shart.")
        return
        
    try:
        from src.database import set_webapp_url
        await set_webapp_url(url)
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="Ochish", web_app=WebAppInfo(url=url))
        )
        await message.answer(f"✅ Web App tugmasi ('Ochish') muvaffaqiyatli o'rnatildi!\nLink: {url}")
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")
