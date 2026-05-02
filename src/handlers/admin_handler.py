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
- /ban [id]
- /unban [id]
"""

import asyncio
import logging
from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import Message, MenuButtonWebApp, WebAppInfo, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class BroadcastState(StatesGroup):
    waiting_for_message = State()

class ChannelAdminStates(StatesGroup):
    waiting_for_add_link = State()
    waiting_for_add_name = State()
    waiting_for_change_selection = State()
    waiting_for_change_link = State()
    waiting_for_change_name = State()
from src.database import (
    is_admin, add_admin, remove_admin,
    add_channel, remove_channel, get_all_channels, update_channel_by_index,
    get_bot_statistics, get_user_full_stats, users_collection,
    set_user_blacklist
)
from src.config import ADMIN_ID
from src.services.error_handler import handle_error, ErrorType

router = Router()
logger = logging.getLogger(__name__)

class BroadcastState(StatesGroup):
    waiting_for_message = State()

async def check_admin(user_id: int, message_or_cb, bot: Bot) -> bool:
    """Check if user is admin. If not, alert real admin and reject."""
    if await is_admin(user_id):
        return True
    
    # Reject message
    if isinstance(message_or_cb, Message):
        await message_or_cb.answer("❌ Ruxsat yo'q.")
        command = message_or_cb.text
    else:
        await message_or_cb.answer("❌ Ruxsat yo'q.", show_alert=True)
        command = message_or_cb.data
        
    # Alert real admin
    await handle_error(
        bot, 
        ErrorType.TELEGRAM_GENERAL, 
        f"Unauthorized admin access attempt by User ID: {user_id}\nCommand: {command}", 
        user_id
    )
    return False

@router.message(Command("stats"))
async def cmd_stats(message: Message, bot: Bot):
    if not await check_admin(message.from_user.id, message, bot): return
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
async def cmd_user(message: Message, bot: Bot):
    if not await check_admin(message.from_user.id, message, bot): return
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
        blacklisted = "Ha 🚫" if u_stats.get("is_blacklisted") else "Yo'q"
        
        text = (
            f"👤 Foydalanuvchi: {u_stats['full_name']}\n"
            f"📱 Telefon: {u_stats['phone']}\n"
            f"📅 Ro'yxat: {u_stats['created_at']}\n"
            f"💰 Balans: {b_uzs:,} UZS | {b_usd:,} USD\n"
            f"📊 Tranzaksiyalar: {u_stats['tx_count']}\n"
            f"🔄 Oxirgi faollik: {u_stats['last_active']}\n"
            f"🚫 Qora ro'yxatda: {blacklisted}"
        )
        await message.answer(text)
    except ValueError:
        await message.answer("❌ ID faqat raqamlardan iborat bo'lishi kerak.")

@router.message(Command("ban"))
async def cmd_ban(message: Message, bot: Bot):
    if not await check_admin(message.from_user.id, message, bot): return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Xato! Format: /ban [telegram_id]")
        return
    try:
        user_id = int(args[1])
        if await set_user_blacklist(user_id, True):
            await message.answer(f"✅ User {user_id} qora ro'yxatga kiritildi. Endi bot undan xabar qabul qilmaydi.")
        else:
            await message.answer("❌ Foydalanuvchi topilmadi.")
    except ValueError:
        await message.answer("❌ ID faqat raqamlardan iborat bo'lishi kerak.")

@router.message(Command("unban"))
async def cmd_unban(message: Message, bot: Bot):
    if not await check_admin(message.from_user.id, message, bot): return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Xato! Format: /unban [telegram_id]")
        return
    try:
        user_id = int(args[1])
        if await set_user_blacklist(user_id, False):
            await message.answer(f"✅ User {user_id} qora ro'yxatdan chiqarildi.")
        else:
            await message.answer("❌ Foydalanuvchi topilmadi.")
    except ValueError:
        await message.answer("❌ ID faqat raqamlardan iborat bo'lishi kerak.")

@router.message(Command("channels"))
async def cmd_channels(message: Message, bot: Bot):
    if not await check_admin(message.from_user.id, message, bot): return
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
async def cmd_setchannel(message: Message, bot: Bot):
    if not await check_admin(message.from_user.id, message, bot): return
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("Xato! Format: /setchannel [tartib_raqami] [@kanal_yoki_link] [Kanal nomi - ixtiyoriy]")
        return
        
    try:
        index = int(args[1]) - 1
        new_link = args[2]
        new_name = "Yangi kanal" if len(args) == 3 else args[2]
        
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
async def cmd_add_admin(message: Message, bot: Bot):
    if not await check_admin(message.from_user.id, message, bot): return
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
async def cmd_remove_admin(message: Message, bot: Bot):
    if not await check_admin(message.from_user.id, message, bot): return
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
async def cmd_add_channel(message: Message, state: FSMContext, bot: Bot):
    if not await check_admin(message.from_user.id, message, bot): return
    await message.answer("Yangi kanal qoshish:\\nKanal linkini yuboring (Masalan: https://t.me/kanal_nomi):")
    await state.set_state(ChannelAdminStates.waiting_for_add_link)

@router.message(ChannelAdminStates.waiting_for_add_link)
async def process_add_link(message: Message, state: FSMContext):
    link = message.text.strip()
    if not link.startswith("http") and not link.startswith("@"):
         await message.answer("Xato! Link 'https://' yoki '@' bilan boshlanishi kerak. Qaytadan yuboring:")
         return
    await state.update_data(new_channel_link=link)
    await message.answer("Bu kanal uchun tugma nomini qanday qo'yamiz? (Masalan: Somly AI Rasmiy)")
    await state.set_state(ChannelAdminStates.waiting_for_add_name)

@router.message(ChannelAdminStates.waiting_for_add_name)
async def process_add_name(message: Message, state: FSMContext):
    name = message.text.strip()
    data = await state.get_data()
    link = data.get("new_channel_link")
    
    if await add_channel(link, name):
        await message.answer(f"✅ Kanal muvaffaqiyatli qo'shildi!\\nNom: {name}\\nLink: {link}\\n\\nEslatma: Botni shu kanalga admin qilishni unutmang!")
    else:
        await message.answer("❌ Bu kanal allaqachon qo'shilgan yoki xatolik yuz berdi.")
    await state.clear()


@router.message(Command("change_channel"))
async def cmd_change_channel(message: Message, state: FSMContext, bot: Bot):
    if not await check_admin(message.from_user.id, message, bot): return
    channels = await get_all_channels()
    if not channels:
        await message.answer("Hozircha kanallar yo'q. Avval /add_channel orqali kanal qo'shing.")
        return
        
    msg = "Qaysi kanalni o'zgartirmoqchisiz? Raqamini yuboring:\\n\\n"
    for idx, c in enumerate(channels, 1):
        msg += f"{idx}. {c['name']} ({c['link']})\\n"
    
    await message.answer(msg)
    await state.set_state(ChannelAdminStates.waiting_for_change_selection)
    # Kanallar sonini saqlab qolamiz tekshirish uchun
    await state.update_data(channels_count=len(channels))

@router.message(ChannelAdminStates.waiting_for_change_selection)
async def process_change_selection(message: Message, state: FSMContext):
    try:
        index = int(message.text.strip()) - 1
        data = await state.get_data()
        channels_count = data.get("channels_count", 0)
        
        if index < 0 or index >= channels_count:
             await message.answer("❌ Noto'g'ri raqam! Iltimos, ro'yxatdagi raqamlardan birini yuboring:")
             return
             
        await state.update_data(change_channel_index=index)
        await message.answer("Yangi kanal linkini yuboring:")
        await state.set_state(ChannelAdminStates.waiting_for_change_link)
    except ValueError:
        await message.answer("❌ Iltimos, faqat raqam yuboring:")

@router.message(ChannelAdminStates.waiting_for_change_link)
async def process_change_link(message: Message, state: FSMContext):
    link = message.text.strip()
    if not link.startswith("http") and not link.startswith("@"):
         await message.answer("Xato! Link 'https://' yoki '@' bilan boshlanishi kerak. Qaytadan yuboring:")
         return
    await state.update_data(change_channel_link=link)
    await message.answer("Yangi kanal uchun tugma nomini qanday qo'yamiz?")
    await state.set_state(ChannelAdminStates.waiting_for_change_name)

@router.message(ChannelAdminStates.waiting_for_change_name)
async def process_change_name(message: Message, state: FSMContext):
    name = message.text.strip()
    data = await state.get_data()
    index = data.get("change_channel_index")
    link = data.get("change_channel_link")
    
    if await update_channel_by_index(index, link, name):
         await message.answer(f"✅ Kanal o'zgartirildi!\\nYangi nom: {name}\\nYangi link: {link}")
    else:
         await message.answer("❌ Xatolik yuz berdi.")
    await state.clear()


# ─── BROADCAST SYSTEM ───

@router.message(Command("send"))
async def cmd_send(message: Message, state: FSMContext, bot: Bot):
    if not await check_admin(message.from_user.id, message, bot): return
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
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yuborish", callback_data="confirm_send"),
            InlineKeyboardButton(text="❌ Bekor", callback_data="cancel_send")
        ]
    ])
    
    await state.update_data(broadcast_msg_id=message.message_id, broadcast_chat_id=message.chat.id, total_users=total_users)
    
    await message.answer(
        f"{total_users} ta foydalanuvchiga yuborilsinmi?\n\n<i>Yuborayotgan xabaringiz yuqorida.</i>",
        reply_markup=kb, parse_mode="HTML"
    )

@router.callback_query(F.data == "confirm_send")
async def confirm_send_callback(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if not await check_admin(callback.from_user.id, callback, bot): return
        
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
    
    from src.services.error_handler import safe_send_message
    
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
            
        if i % 50 == 0 or i == total_users:
            try:
                await callback.message.edit_text(f"⏳ Yuborildi: {success_count} / {total_users}\n(Xato: {fail_count})")
            except Exception:
                pass
                
        await asyncio.sleep(0.05)
            
    await callback.message.edit_text(f"✅ Tarqatish yakunlandi!\n\nJo'natildi: {success_count} ta\nXato: {fail_count} ta")
    await state.clear()

@router.callback_query(F.data == "cancel_send")
async def cancel_send_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Yuborish bekor qilindi.")
    await state.clear()


@router.message(Command("setwebapp"))
async def cmd_setwebapp(message: Message, bot: Bot):
    if not await check_admin(message.from_user.id, message, bot): return
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


@router.message(Command("web"))
async def cmd_web(message: Message, bot: Bot):
    if not await check_admin(message.from_user.id, message, bot): return
    
    text = (
        "🌐 <b>Admin Panel</b>\n\n"
        "Barcha foydalanuvchilar haqidagi (demografik) ma'lumotlarni ko'rish uchun quyidagi manzilga kiring:\n"
        "👉 http://localhost:8000/admin\n\n"
        "<b>Login:</b> <code>1342b</code>\n"
        "<b>Parol:</b> <code>gsk1352</code>"
    )
    await message.answer(text, parse_mode="HTML")


# ─── DYNAMIC KNOWLEDGE BASE (QISM 8) ───

@router.message(Command("teach"))
async def cmd_teach(message: Message, bot: Bot):
    if not await check_admin(message.from_user.id, message, bot): return
    # format: /teach topic: content
    text = message.text.replace("/teach", "", 1).strip()
    if ":" not in text:
        await message.answer("❌ Xato! Format: /teach [mavzu]: [matn]")
        return
        
    topic, content = text.split(":", 1)
    topic = topic.strip()
    content = content.strip()
    
    if not topic or not content:
        await message.answer("❌ Mavzu va matn bo'sh bo'lishi mumkin emas.")
        return
        
    from src.database import add_knowledge
    success = await add_knowledge(topic, content, message.from_user.id)
    if success:
        await message.answer(f"✅ Yangi bilim qo'shildi:\n<b>Mavzu:</b> {topic}", parse_mode="HTML")
    else:
        await message.answer(f"❌ '{topic}' mavzusi allaqachon mavjud. Yangilash uchun /editteach ishlating.")

@router.message(Command("knowledge"))
async def cmd_knowledge(message: Message, bot: Bot):
    if not await check_admin(message.from_user.id, message, bot): return
    
    from src.database import get_all_knowledges
    knowledges = await get_all_knowledges()
    
    if not knowledges:
        await message.answer("📚 Bilimlar bazasi bo'sh.")
        return
        
    text = f"📚 <b>Bilimlar bazasi ({len(knowledges)} ta):</b>\n\n"
    for i, k in enumerate(knowledges, 1):
        status = "✅" if k.get("active") else "❌"
        usage = k.get("usage_count", 0)
        text += f"{i}. <code>{k['topic']}</code> {status} ({usage} marta)\n"
        
    text += "\n<i>Yangi bilim qo'shish: /teach mavzu: matn</i>\n"
    text += "<i>O'chirish: /unteach mavzu</i>\n"
    text += "<i>Tahrirlash: /editteach mavzu: matn</i>"
    
    await message.answer(text, parse_mode="HTML")

@router.message(Command("unteach"))
async def cmd_unteach(message: Message, bot: Bot):
    if not await check_admin(message.from_user.id, message, bot): return
    topic = message.text.replace("/unteach", "", 1).strip()
    if not topic:
        await message.answer("❌ Xato! Format: /unteach [mavzu]")
        return
        
    from src.database import set_knowledge_active
    success = await set_knowledge_active(topic, False)
    if success:
        await message.answer(f"✅ '{topic}' mavzusi o'chirildi (arxivlandi).")
    else:
        await message.answer(f"❌ '{topic}' mavzusi topilmadi.")

@router.message(Command("editteach"))
async def cmd_editteach(message: Message, bot: Bot):
    if not await check_admin(message.from_user.id, message, bot): return
    text = message.text.replace("/editteach", "", 1).strip()
    if ":" not in text:
        await message.answer("❌ Xato! Format: /editteach [mavzu]: [yangi matn]")
        return
        
    topic, content = text.split(":", 1)
    topic = topic.strip()
    content = content.strip()
    
    from src.database import update_knowledge
    success = await update_knowledge(topic, content)
    if success:
        await message.answer(f"✅ '{topic}' mavzusi yangilandi.")
    else:
        await message.answer(f"❌ '{topic}' mavzusi topilmadi. Yangi qo'shish uchun /teach ishlating.")
