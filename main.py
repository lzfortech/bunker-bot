import os
import asyncio
import random
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest

from cards_db import (
    CATASTROPHES, BUNKERS, RANDOM_EVENTS, PROFESSIONS,
    CARDS_POOL, CARD_LABELS, generate_character, generate_epilogue
)

# ================= SOZLAMALAR =================
BOT_TOKEN = "8944273231:AAGCZQhkoGIq4im_ncxTTkf5KgONIKl8src"
MIN_PLAYERS = 2          # Minimal o'yinchilar soni (test uchun 2 qilishingiz mumkin)
LOBBY_TIMEOUT = 300      # O'yinga odam yig'ilmasa bekor qilish vaqti (300 s = 5 daqiqa)
DISCUSSION_TIMEOUT = 120 # Karta ochish va muhokama vaqti (120 s = 2 daqiqa)
VOTING_TIMEOUT = 60      # Ovoz berish vaqti (60 s = 1 daqiqa)
# ==============================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

games = {}
user_group = {}


# ================= YORDAMCHI VA SINXRONIZATSIYA FUNKSIYALARI =================

def cancel_phase_timer(game: dict):
    """Joriy bosqich taymerini xavfsiz to'xtatish"""
    task = game.get("phase_task")
    if task and not task.done():
        task.cancel()
    game["phase_task"] = None


async def is_host_or_admin(chat_id: int, user_id: int) -> bool:
    """Foydalanuvchi o'yin egasi (Host) yoki guruh admini ekanligini tekshirish"""
    if chat_id in games and games[chat_id]["host_id"] == user_id:
        return True
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except Exception:
        return False


def format_dossier(player: dict, reveal_all: bool = False) -> str:
    """O'yinchining barcha 12 ta kartasini matn ko'rinishiga keltirish"""
    lines = [f"👤 <b>{player['name']}</b> dosyesi:\n━━━━━━━━━━━━━━━━━━"]
    for k, label in CARD_LABELS.items():
        card = player["cards"][k]
        if reveal_all or card["opened"]:
            status = "✅ (Ochiq)" if card["opened"] else "🔓"
            lines.append(f"{status} <b>{label}:</b> {card['val']}")
        else:
            lines.append(f"🔒 <b>{label}:</b> <i>Yashirin</i>")
    return "\n".join(lines)


def get_pm_cards_keyboard(player: dict) -> InlineKeyboardMarkup:
    """LS (Shaxsiy chat) uchun kartalarni ochish tugmalari"""
    buttons = []
    for k, label in CARD_LABELS.items():
        card = player["cards"][k]
        if k == "maxsus":
            if not card["used"]:
                buttons.append([InlineKeyboardButton(
                    text=f"⚡ ISHLATISH: {label}",
                    callback_data="spec_menu"
                )])
        else:
            if not card["opened"]:
                clean_val = card['val'].replace("<b>", "").replace("</b>", "")
                buttons.append([InlineKeyboardButton(
                    text=f"🃏 Ochish: {label} ({clean_val[:22]}...)",
                    callback_data=f"reveal:{k}"
                )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def sync_player_pm(game: dict, player: dict, notice: str = None):
    """Maxsus karta ishlatilganda yoki karta ochilganda o'yinchining LS xabarlarini yangilash"""
    uid = player["id"]
    dossier_text = format_dossier(player, reveal_all=True)

    # 1. Boshida berilgan birinchi dosye xabarini yangilash
    if player.get("init_msg_id"):
        try:
            await bot.edit_message_text(
                chat_id=uid,
                message_id=player["init_msg_id"],
                text=f"📋 <b>SIZNING JORIY DOSYENGIZ (Yangilangan):</b>\n\n{dossier_text}",
                parse_mode="HTML"
            )
        except Exception:
            pass

    # 2. Joriy aylanadagi faol tugmalar xabarini yangilash
    if player.get("pm_msg_id") and game["phase"] == "DISCUSSION" and player["alive"]:
        kb = get_pm_cards_keyboard(player)
        status_line = "✅ <i>Siz bu aylanada karta ochib bo'ldingiz.</i>" if player["opened_in_round"] else "👇 <i>Ushbu aylanada ochish uchun karta tanlang:</i>"
        try:
            await bot.edit_message_text(
                chat_id=uid,
                message_id=player["pm_msg_id"],
                text=f"🔄 <b>{game['round']}-Aylana</b> | {status_line}\n\n{dossier_text}",
                reply_markup=kb,
                parse_mode="HTML"
            )
        except Exception:
            pass

    # 3. Agar unga nisbatan maxsus karta ishlatilgan bo'lsa, ogohlantirish yuborish
    if notice:
        try:
            await bot.send_message(uid, f"🔔 <b>DIQQAT!</b>\n{notice}\n\nSizning dosye ma'lumotlaringiz yangilandi!", parse_mode="HTML")
        except Exception:
            pass


def format_group_board(game: dict) -> str:
    """Guruh uchun umumiy vaziyat va o'yinchilarning ochiq ma'lumotlari"""
    cat = game["catastrophe"]
    bunk = game["bunker"]
    alive_players = [p for p in game["players"].values() if p["alive"]]

    text = (
        f"☢️ <b>FALOKAT: {cat['title']}</b>\n"
        f"<i>{cat['desc']}</i>\n"
        f"⏳ Muddat: <b>{cat['duration']}</b> | 🛡️ Bunker sig'imi: <b>{game['capacity']} kishi</b>\n\n"
        f"🏢 <b>Bunker:</b> {bunk['name']} ({bunk['size']})\n"
        f"🚪 <b>Xonalar:</b> {', '.join(bunk['rooms'])}\n"
        f"📦 <b>Zaxira:</b> {bunk['supplies']}\n"
        f"{bunk['problem']}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔄 <b>{game['round']}-AYLANA | TIRIKLAR ({len(alive_players)}/{len(game['players'])}):</b>\n\n"
    )

    for idx, p in enumerate(game["players"].values(), 1):
        status_icon = "🟢" if p["alive"] else "💀"
        shield_icon = " 🛡(Immunitet)" if p.get("shielded") else ""
        text += f"{idx}. {status_icon} <b>{p['name']}</b>{shield_icon}:\n"
        opened_list = []
        for k, label in CARD_LABELS.items():
            if p["cards"][k]["opened"]:
                opened_list.append(f"  • <i>{label}:</i> {p['cards'][k]['val']}")
        if opened_list:
            text += "\n".join(opened_list) + "\n\n"
        else:
            text += "  • <i>Hali karta ochmagan</i>\n\n"

    return text


def get_group_control_kb(bot_username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🃏 Kartalarni ochish (Botga o'tish)", url=f"https://t.me/{bot_username}")],
        [
            InlineKeyboardButton(text="📋 Umumiy doska", callback_data="show_board"),
            InlineKeyboardButton(text="🗳 Ovoz berishni boshlash", callback_data="start_vote")
        ]
    ])


# ================= TAYMER FUNKSIYALARI (LOBBY, MUHOKAMA, OVOZ BERISH) =================

async def auto_cancel_lobby(chat_id: int):
    """5 daqiqa ichida o'yin boshlanmasa avtomatik bekor qilish"""
    try:
        await asyncio.sleep(LOBBY_TIMEOUT)
        if chat_id in games and games[chat_id]["phase"] == "LOBBY":
            game = games[chat_id]
            for uid in game["players"]:
                user_group.pop(uid, None)
            msg_id = game.get("lobby_msg_id")
            del games[chat_id]

            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=msg_id,
                    text="⏳ <b>Qabul vaqti tugadi!</b>\nBelgilangan 5 daqiqa ichida o'yin boshlanmagani sababli avtomatik bekor qilindi.\n\n🔄 Qayta boshlash: /bunker",
                    parse_mode="HTML"
                )
            except Exception:
                await bot.send_message(chat_id, "⏳ Vaqt tugagani uchun o'yin qabuli avtomatik yopildi.")
    except asyncio.CancelledError:
        pass


async def discussion_timer_task(chat_id: int, round_num: int):
    """Karta ochish va muhokama taymeri. Vaqt tugasa AFK o'yinchilar kartasini avto-ochib, ovoz berishga o'tkazadi"""
    try:
        half_time = DISCUSSION_TIMEOUT // 2
        await asyncio.sleep(half_time)

        if chat_id not in games or games[chat_id]["phase"] != "DISCUSSION" or games[chat_id]["round"] != round_num:
            return

        game = games[chat_id]
        not_opened = [p["name"] for p in game["players"].values() if p["alive"] and not p["opened_in_round"]]
        if not_opened:
            await bot.send_message(
                chat_id,
                f"⏳ <b>Karta ochish va muhokama tugashiga {half_time} soniya qoldi!</b>\n"
                f"❗️ Hali karta ochmaganlar: {', '.join(not_opened)}",
                parse_mode="HTML"
            )

        await asyncio.sleep(DISCUSSION_TIMEOUT - half_time)

        if chat_id not in games or games[chat_id]["phase"] != "DISCUSSION" or games[chat_id]["round"] != round_num:
            return

        # Vaqt tugadi! Karta ochmaganlarning kartasini majburan ochamiz
        auto_revealed_msgs = []
        for p in game["players"].values():
            if p["alive"] and not p["opened_in_round"]:
                if round_num == 1 and not p["cards"]["kasb"]["opened"]:
                    chosen_key = "kasb"
                else:
                    closed_keys = [k for k, v in p["cards"].items() if not v["opened"] and k != "maxsus"]
                    chosen_key = random.choice(closed_keys) if closed_keys else None

                if chosen_key:
                    p["cards"][chosen_key]["opened"] = True
                    p["opened_in_round"] = True
                    lbl = CARD_LABELS[chosen_key]
                    val = p["cards"][chosen_key]["val"]
                    auto_revealed_msgs.append(f"• <b>{p['name']}</b> [{lbl}]: {val}")
                    await sync_player_pm(game, p)

        if auto_revealed_msgs:
            await bot.send_message(
                chat_id,
                f"⏰ <b>Muhokama vaqti tugadi!</b> Vaqtida karta ochmagan o'yinchilarning kartalari avtomatik ochildi:\n\n"
                + "\n".join(auto_revealed_msgs),
                parse_mode="HTML"
            )
        else:
            await bot.send_message(chat_id, "⏰ <b>Muhokama vaqti tugadi!</b> Avtomatik ovoz berish bosqichiga o'tilmoqda...", parse_mode="HTML")

        await trigger_voting_phase(chat_id)

    except asyncio.CancelledError:
        pass


async def voting_timer_task(chat_id: int, round_num: int):
    """Ovoz berish taymeri (60 soniya)"""
    try:
        await asyncio.sleep(VOTING_TIMEOUT - 20)
        if chat_id not in games or games[chat_id]["phase"] != "VOTING" or games[chat_id]["round"] != round_num:
            return

        game = games[chat_id]
        not_voted = [p["name"] for uid, p in game["players"].items() if p["alive"] and uid not in game["votes"]]
        if not_voted:
            await bot.send_message(
                chat_id,
                f"⏳ <b>Ovoz berish tugashiga 20 soniya qoldi!</b>\n❗️ Ovoz bermaganlar: {', '.join(not_voted)}",
                parse_mode="HTML"
            )

        await asyncio.sleep(20)
        if chat_id not in games or games[chat_id]["phase"] != "VOTING" or games[chat_id]["round"] != round_num:
            return

        await bot.send_message(chat_id, "⏰ <b>Ovoz berish vaqti tugadi!</b> Natijalar hisoblanmoqda...", parse_mode="HTML")
        await finalize_voting(chat_id)

    except asyncio.CancelledError:
        pass


# ================= 1. GURUHDA O'YIN YARATISH =================

@dp.message(Command("bunker"))
async def cmd_bunker_group(message: types.Message):
    if message.chat.type == "private":
        return await message.answer("⚠️ Bu buyruq faqat guruhlarda ishlaydi! Botni guruhga qo'shing va /bunker yozing.")

    chat_id = message.chat.id
    if chat_id in games and games[chat_id]["phase"] != "ENDED":
        return await message.answer("⚠️ Guruhda allaqachon o'yin ketmoqda! To'xtatish uchun: /stopbunker")

    bot_info = await bot.get_me()
    timeout_task = asyncio.create_task(auto_cancel_lobby(chat_id))

    games[chat_id] = {
        "chat_id": chat_id,
        "host_id": message.from_user.id,
        "phase": "LOBBY",
        "round": 1,
        "capacity": 2,
        "catastrophe": random.choice(CATASTROPHES),
        "bunker": random.choice(BUNKERS),
        "used_professions": [],
        "players": {},
        "votes": {},
        "lobby_msg_id": None,
        "phase_task": timeout_task
    }

    join_url = f"https://t.me/{bot_info.username}?start=join_{chat_id}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚪 O'yinga qo'shilish", url=join_url)],
        [InlineKeyboardButton(text=f"▶️ Boshlash (Kamida {MIN_PLAYERS} kishi)", callback_data="force_start")]
    ])

    sent = await message.answer(
        f"☢️ <b>BUNKER O'YINIGA QABUL BOSHLANDI!</b>\n"
        f"👑 Boshlovchi: <b>{message.from_user.full_name}</b>\n"
        f"⏳ Qabul vaqti: <b>5 daqiqa</b>\n\n"
        f"O'yinga qo'shilish uchun quyidagi tugmani bosing va botga <b>START</b> bering.\n\n"
        f"👥 <b>Qo'shilgan o'yinchilar (0/{MIN_PLAYERS}):</b>\n<i>Hozircha hech kim yo'q...</i>",
        reply_markup=kb,
        parse_mode="HTML"
    )
    games[chat_id]["lobby_msg_id"] = sent.message_id


@dp.message(Command("stopbunker"))
async def cmd_stop_bunker(message: types.Message):
    if message.chat.type == "private":
        return

    chat_id = message.chat.id
    if chat_id not in games:
        return await message.answer("⚠️ Guruhda hozir faol o'yin yo'q.")

    if not await is_host_or_admin(chat_id, message.from_user.id):
        return await message.reply("⛔ O'yinni faqat uni boshlagan odam yoki guruh adminlari to'xtata oladi!")

    game = games[chat_id]
    cancel_phase_timer(game)

    for uid in game["players"]:
        user_group.pop(uid, None)
    del games[chat_id]
    await message.answer(f"🛑 Bunker o'yini <b>{message.from_user.full_name}</b> tomonidan to'xtatildi.", parse_mode="HTML")


# ================= 2. BOTGA START BOSIB QO'SHILISH =================

@dp.message(CommandStart())
async def cmd_start_private(message: types.Message, command: CommandObject):
    if message.chat.type != "private":
        return

    args = command.args
    if not args or not args.startswith("join_"):
        return await message.answer(
            "👋 <b>Bunker Botga xush kelibsiz!</b>\n\n"
            "Bu o'yin do'stlar bilan guruhda o'ynaladi. Botni guruhingizga qo'shing va u yerda /bunker buyrug'ini yozing!",
            parse_mode="HTML"
        )

    try:
        chat_id = int(args.replace("join_", ""))
    except ValueError:
        return await message.answer("❌ Noto'g'ri havola.")

    if chat_id not in games or games[chat_id]["phase"] != "LOBBY":
        return await message.answer("⚠️ Bu guruhda hozir o'yinga qabul yopilgan yoki o'yin allaqachon boshlangan.")

    uid = message.from_user.id
    name = message.from_user.full_name
    game = games[chat_id]

    if uid in game["players"]:
        return await message.answer("✅ Siz allaqachon o'yinga qo'shilgansiz! Guruhda o'yin boshlanishini kuting.")

    if uid in user_group and user_group[uid] in games and games[user_group[uid]]["phase"] != "ENDED":
        return await message.answer("⚠️ Siz hozir boshqa guruhdagi o'yinda ishtirok etyapsiz! Avval o'sha o'yinni yakunlang.")

    game["players"][uid] = {
        "id": uid,
        "name": name,
        "alive": True,
        "opened_in_round": False,
        "shielded": False,
        "vote_weight": 1,
        "init_msg_id": None,
        "pm_msg_id": None,
        "cards": generate_character(game["used_professions"])
    }
    user_group[uid] = chat_id

    dossier_text = format_dossier(game["players"][uid], reveal_all=True)
    sent_init = await message.answer(
        f"✅ <b>Siz o'yinga muvaffaqiyatli qo'shildingiz!</b>\n\n"
        f"{dossier_text}\n\n"
        f"⏳ <i>Guruhda kamida {MIN_PLAYERS} ta o'yinchi yig'ilgach o'yin boshlanadi.</i>",
        parse_mode="HTML"
    )
    game["players"][uid]["init_msg_id"] = sent_init.message_id

    bot_info = await bot.get_me()
    join_url = f"https://t.me/{bot_info.username}?start=join_{chat_id}"
    p_names = "\n".join([f"{i}. 👤 {p['name']}" for i, p in enumerate(game["players"].values(), 1)])
    count = len(game["players"])

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚪 O'yinga qo'shilish", url=join_url)],
        [InlineKeyboardButton(text=f"▶️ Boshlash ({count}/{MIN_PLAYERS})", callback_data="force_start")]
    ])

    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=game["lobby_msg_id"],
            text=(
                f"☢️ <b>BUNKER O'YINIGA QABUL DAVOM ETMOQDA!</b>\n\n"
                f"👥 <b>Qo'shilgan o'yinchilar ({count} ta):</b>\n{p_names}\n\n"
                f"{'✅ <b>Yetarli o\'yinchi yig\'ildi! Boshlash tugmasini bosing!</b>' if count >= MIN_PLAYERS else f'⏳ Yana {MIN_PLAYERS - count} ta o\'yinchi kerak...'}"
            ),
            reply_markup=kb,
            parse_mode="HTML"
        )
    except TelegramBadRequest:
        pass


# ================= 3. GURUHDA O'YINNI BOSHLASH =================

@dp.callback_query(F.data == "force_start")
async def cb_start_game(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    if chat_id not in games:
        return await call.answer("O'yin topilmadi!", show_alert=True)

    if not await is_host_or_admin(chat_id, call.from_user.id):
        return await call.answer("⛔ O'yinni faqat uni yaratgan boshlovchi yoki guruh admini boshlay oladi!", show_alert=True)

    game = games[chat_id]
    if game["phase"] != "LOBBY":
        return await call.answer("O'yin allaqachon boshlangan!", show_alert=True)

    if len(game["players"]) < MIN_PLAYERS:
        return await call.answer(f"⚠️ Kamida {MIN_PLAYERS} ta ishtirokchi kerak! Hozir: {len(game['players'])} ta.", show_alert=True)

    cancel_phase_timer(game)
    game["phase"] = "DISCUSSION"
    game["round"] = 1
    game["capacity"] = max(1, len(game["players"]) // 2)

    bot_info = await bot.get_me()
    board_text = format_group_board(game)

    await call.message.edit_text(
        board_text + f"\n📢 <b>1-Aylana boshlandi! (Vaqt: {DISCUSSION_TIMEOUT} soniya)</b>\nBarcha o'yinchilar botning shaxsiy chatiga (LS) o'tib, o'z <b>1. Kasb</b> kartasini ochsin!",
        reply_markup=get_group_control_kb(bot_info.username),
        parse_mode="HTML"
    )

    for uid, pdata in game["players"].items():
        try:
            sent_pm = await bot.send_message(
                uid,
                f"🚨 <b>O'YIN BOSHLANDI! (1-Aylana | ⏱ {DISCUSSION_TIMEOUT} s)</b>\n"
                f"Quyidagi tugmalardan birini bosib kartangizni guruhga oching (1-aylanada <b>1. Kasb</b> ochilishi shart):\n\n"
                f"{format_dossier(pdata, reveal_all=True)}",
                reply_markup=get_pm_cards_keyboard(pdata),
                parse_mode="HTML"
            )
            pdata["pm_msg_id"] = sent_pm.message_id
        except Exception:
            pass

    # 1-aylana taymerini yoqamiz
    game["phase_task"] = asyncio.create_task(discussion_timer_task(chat_id, game["round"]))


# ================= 4. BOT ICHIDA (LS) KARTANI OCHISH =================

@dp.callback_query(F.data.startswith("reveal:"))
async def cb_reveal_card(call: types.CallbackQuery):
    uid = call.from_user.id
    chat_id = user_group.get(uid)

    if not chat_id or chat_id not in games:
        return await call.answer("Siz faol o'yinda emassiz!", show_alert=True)

    game = games[chat_id]
    player = game["players"].get(uid)

    if not player or not player["alive"]:
        return await call.answer("💀 Siz bunkerdan quvilgansiz!", show_alert=True)

    if game["phase"] != "DISCUSSION":
        return await call.answer("Hozir karta ochish bosqichi emas!", show_alert=True)

    if player["opened_in_round"]:
        return await call.answer("⚠️ Siz bu aylanada allaqachon 1 ta karta ochdingiz!", show_alert=True)

    card_key = call.data.split(":")[1]

    if game["round"] == 1 and not player["cards"]["kasb"]["opened"] and card_key != "kasb":
        return await call.answer("⚠️ 1-Aylanada birinchi bo'lib '1. Kasb' kartangizni ochishingiz shart!", show_alert=True)

    if player["cards"][card_key]["opened"]:
        return await call.answer("Bu karta allaqachon ochilgan!", show_alert=True)

    player["cards"][card_key]["opened"] = True
    player["opened_in_round"] = True
    label_name = CARD_LABELS[card_key]
    val_text = player["cards"][card_key]["val"]

    await call.answer(f"✅ {label_name} kartangiz guruhda e'lon qilindi!")
    await sync_player_pm(game, player)

    opened_count = sum(1 for p in game["players"].values() if p["alive"] and p["opened_in_round"])
    alive_count = sum(1 for p in game["players"].values() if p["alive"])
    bot_info = await bot.get_me()

    extra_note = "\n\n✅ <b>Barcha o'yinchilar karta ochib bo'ldi!</b> Boshlovchi ovoz berishni boshlashi yoki taymer tugashini kutishingiz mumkin." if opened_count >= alive_count else ""

    await bot.send_message(
        chat_id,
        f"🃏 <b>{player['name']}</b> o'zining <b>[{label_name}]</b> kartasini ochdi:\n"
        f"👉 <b>{val_text}</b>\n\n"
        f"📊 <i>Bu aylanada karta ochganlar: {opened_count}/{alive_count}</i>{extra_note}",
        reply_markup=get_group_control_kb(bot_info.username),
        parse_mode="HTML"
    )


# ================= 5. MAXSUS KARTANI ISHLATISH (12-BAND) =================

@dp.callback_query(F.data == "spec_menu")
async def cb_special_menu(call: types.CallbackQuery):
    uid = call.from_user.id
    chat_id = user_group.get(uid)
    if not chat_id or chat_id not in games:
        return

    game = games[chat_id]
    player = game["players"].get(uid)
    if not player or not player["alive"] or player["cards"]["maxsus"]["used"]:
        return await call.answer("Maxsus kartani ishlatib bo'lmaydi!", show_alert=True)

    buttons = []
    for tid, tp in game["players"].items():
        if tp["alive"]:
            buttons.append([InlineKeyboardButton(text=f"🎯 {tp['name']}", callback_data=f"use_spec:{tid}")])
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_cards")])

    await call.message.edit_text(
        f"⚡ <b>Maxsus kartangiz:</b>\n{player['cards']['maxsus']['val']}\n\n"
        f"Qaysi o'yinchiga nisbatan ishlatmoqchisiz?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )


@dp.callback_query(F.data == "back_to_cards")
async def cb_back_cards(call: types.CallbackQuery):
    uid = call.from_user.id
    chat_id = user_group.get(uid)
    if not chat_id or chat_id not in games:
        return
    game = games[chat_id]
    player = game["players"][uid]
    await sync_player_pm(game, player)


@dp.callback_query(F.data.startswith("use_spec:"))
async def cb_execute_special(call: types.CallbackQuery):
    uid = call.from_user.id
    chat_id = user_group.get(uid)
    if not chat_id or chat_id not in games:
        return

    game = games[chat_id]
    player = game["players"].get(uid)
    target_id = int(call.data.split(":")[1])
    target = game["players"].get(target_id)

    if not player or not player["alive"] or player["cards"]["maxsus"]["used"] or not target:
        return await call.answer("Xatolik!", show_alert=True)

    spec = player["cards"]["maxsus"]
    spec["used"] = True
    spec["opened"] = True
    code = spec["code"]

    effect_msg = ""
    target_notice = ""

    if code == "heal":
        target["cards"]["salomatlik"]["val"] = "Mutlaqo sog'lom (Davolangan ✨)"
        target["cards"]["salomatlik"]["opened"] = True
        effect_msg = f"💉 <b>{player['name']}</b> maxsus kartasini ishlatib, <b>{target['name']}</b>ning salomatligini <b>'Mutlaqo sog'lom'</b> holatiga o'zgartirdi!"
        target_notice = f"💉 <b>{player['name']}</b> sizning Salomatlik kartangizni 'Mutlaqo sog'lom' holatiga davoladi!"

    elif code == "spy":
        closed_keys = [k for k, v in target["cards"].items() if not v["opened"] and k != "maxsus"]
        if closed_keys:
            rk = random.choice(closed_keys)
            target["cards"][rk]["opened"] = True
            effect_msg = (
                f"🕵️‍♂️ <b>{player['name']}</b> maxsus kartasini ishlatib, <b>{target['name']}</b>ning yashirin "
                f"<b>[{CARD_LABELS[rk]}]</b> kartasini barchaga fosh qildi:\n👉 <b>{target['cards'][rk]['val']}</b>"
            )
            target_notice = f"🕵️‍♂️ <b>{player['name']}</b> sizning [{CARD_LABELS[rk]}] kartangizni guruhga fosh qildi!"
        else:
            effect_msg = f"🕵️‍♂️ <b>{player['name']}</b> maxsus karta ishlatdi, lekin <b>{target['name']}</b>ning barcha kartalari allaqachon ochiq edi!"

    elif code == "reroll_job":
        new_job, new_tag = random.choice(PROFESSIONS)
        target["cards"]["kasb"]["val"] = f"{new_job} (Almashtirilgan 🔄)"
        target["cards"]["kasb"]["tag"] = new_tag
        target["cards"]["kasb"]["opened"] = True
        effect_msg = f"🔄 <b>{player['name']}</b> maxsus kartasini ishlatib, <b>{target['name']}</b>ning kasbini <b>'{new_job}'</b>ga o'zgartirib yubordi!"
        target_notice = f"🔄 <b>{player['name']}</b> sizning Kasbingizni '{new_job}'ga o'zgartirib yubordi!"

    elif code == "cure_phobia":
        target["cards"]["fobiya"]["val"] = "Fobiya yo'q (Bartaraf etildi ✨)"
        target["cards"]["fobiya"]["opened"] = True
        target["cards"]["zaiflik"]["val"] = "Zaiflik yo'q (Bartaraf etildi ✨)"
        target["cards"]["zaiflik"]["opened"] = True
        effect_msg = f"🧠 <b>{player['name']}</b> maxsus kartasini ishlatib, <b>{target['name']}</b>ni fobiya va zaiflikdan butunlay xalos qildi!"
        target_notice = f"🧠 <b>{player['name']}</b> sizning Fobiya va Zaifligingizni butunlay yo'q qildi!"

    elif code == "steal_bag":
        stolen_item = target["cards"]["jihoz"]["val"]
        player["cards"]["jihoz"]["val"] += f" + {stolen_item}"
        player["cards"]["jihoz"]["opened"] = True
        target["cards"]["jihoz"]["val"] = "Bo'sh (O'g'irlangan 😭)"
        target["cards"]["jihoz"]["opened"] = True
        effect_msg = f"🎒 <b>{player['name']}</b> maxsus karta orqali <b>{target['name']}</b>ning jihozini (<i>{stolen_item}</i>) tortib oldi!"
        target_notice = f"🎒 <b>{player['name']}</b> sizning 9-Jihozingizni o'g'irlab oldi!"

    elif code == "swap_health":
        my_h = player["cards"]["salomatlik"]["val"]
        tg_h = target["cards"]["salomatlik"]["val"]
        player["cards"]["salomatlik"]["val"] = tg_h
        target["cards"]["salomatlik"]["val"] = my_h
        player["cards"]["salomatlik"]["opened"] = True
        target["cards"]["salomatlik"]["opened"] = True
        effect_msg = f"🔀 <b>{player['name']}</b> o'z salomatligini (<i>{my_h}</i>) <b>{target['name']}</b>ning salomatligi (<i>{tg_h}</i>) bilan almashtirdi!"
        target_notice = f"🔀 <b>{player['name']}</b> o'zining Salomatligini ({my_h}) sizniki bilan almashtirdi!"

    elif code == "shield":
        target["shielded"] = True
        effect_msg = f"🛡 <b>{player['name']}</b> maxsus karta orqali <b>{target['name']}</b>ga <b>Immunitet</b> berdi! Bu aylanada unga qarshi ovoz berib bo'lmaydi."
        target_notice = f"🛡 <b>{player['name']}</b> sizga ushbu aylana uchun Ovoz berish Immunitetini berdi!"

    elif code == "double_vote":
        target["vote_weight"] = 2
        effect_msg = f"⚖️ <b>{player['name']}</b> maxsus karta ishlatdi: navbatdagi ovoz berishda <b>{target['name']}</b>ning ovozi <b>2 ta ovoz</b>ga teng bo'ladi!"
        target_notice = f"⚖️ <b>{player['name']}</b> sizning ovoz kuchingizni 2 barobarga oshirdi!"

    elif code == "rejuvenate":
        gender = target["cards"]["bio"].get("gender", "Inson")
        target["cards"]["bio"]["val"] = f"{gender}, 24 yoshda — Sog'lom, nasl qoldira oladi ✨"
        target["cards"]["bio"]["fertile"] = True
        target["cards"]["bio"]["opened"] = True
        effect_msg = f"🧬 <b>{player['name']}</b> maxsus karta bilan <b>{target['name']}</b>ning biologiyasini 24 yoshli sog'lom va nasl qoldira oladigan holatga yangiladi!"
        target_notice = f"🧬 <b>{player['name']}</b> sizning Biologiyangizni '24 yosh, sog'lom' holatiga yangiladi!"

    # Kartani ishlatgan o'yinchining o'z LS xabarlarini yangilash
    await sync_player_pm(game, player)

    # Agar boshqa o'yinchiga ishlatilgan bo'lsa, uning ham LS dosyesi va tugmalarini darhol yangilash!
    if target_id != uid:
        await sync_player_pm(game, target, notice=target_notice)

    await call.answer("⚡ Maxsus karta muvaffaqiyatli ishlatildi!")

    await bot.send_message(
        chat_id,
        f"⚡ <b>MAXSUS KARTA ISHLATILDI!</b>\n\n{effect_msg}",
        parse_mode="HTML"
    )


# ================= 6. DOSKANI KO'RISH VA OVOZ BERISH =================

@dp.callback_query(F.data == "show_board")
async def cb_show_board(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    if chat_id not in games:
        return await call.answer("O'yin topilmadi!", show_alert=True)

    bot_info = await bot.get_me()
    await call.message.answer(
        format_group_board(games[chat_id]),
        reply_markup=get_group_control_kb(bot_info.username),
        parse_mode="HTML"
    )
    await call.answer()


@dp.callback_query(F.data == "start_vote")
async def cb_start_voting(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    if chat_id not in games:
        return await call.answer("O'yin topilmadi!", show_alert=True)

    if not await is_host_or_admin(chat_id, call.from_user.id):
        return await call.answer("⛔ Ovoz berishni faqat boshlovchi yoki guruh admini boshlay oladi!", show_alert=True)

    game = games[chat_id]
    if game["phase"] != "DISCUSSION":
        return await call.answer("Hozir ovoz berishni boshlab bo'lmaydi!", show_alert=True)

    await call.answer()
    await trigger_voting_phase(chat_id)


async def trigger_voting_phase(chat_id: int):
    """Ovoz berish bosqichini boshlash va 60 soniyalik taymer yoqish"""
    if chat_id not in games:
        return
    game = games[chat_id]
    cancel_phase_timer(game)

    game["phase"] = "VOTING"
    game["votes"] = {}

    bot_info = await bot.get_me()
    await bot.send_message(
        chat_id,
        f"🗳 <b>{game['round']}-AYLANA OVOZ BERISH BOSHLANDI! (⏱ Vaqt: {VOTING_TIMEOUT} soniya)</b>\n\n"
        f"Barcha tirik o'yinchilar botning shaxsiy chatiga (LS) o'tib, bunkerga noloyiq deb bilgan 1 ta o'yinchiga ovoz bersin!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗳 Ovoz berish (Botga o'tish)", url=f"https://t.me/{bot_info.username}")],
            [InlineKeyboardButton(text="⚡ Ovozlarni majburan yakunlash", callback_data="force_end_vote")]
        ]),
        parse_mode="HTML"
    )

    for uid, pdata in game["players"].items():
        if not pdata["alive"]:
            continue

        vote_buttons = []
        for tid, tp in game["players"].items():
            if tp["alive"] and tid != uid and not tp.get("shielded"):
                open_job = tp["cards"]["kasb"]["val"] if tp["cards"]["kasb"]["opened"] else "Kasbi noma'lum"
                vote_buttons.append([InlineKeyboardButton(
                    text=f"❌ {tp['name']} ({open_job[:25]})",
                    callback_data=f"vote:{tid}"
                )])

        try:
            await bot.send_message(
                uid,
                f"🗳 <b>{game['round']}-Aylana: Ovoz berish vaqti! (⏱ {VOTING_TIMEOUT} s)</b>\nKimni bunkerdan chetlatish kerak deb hisoblaysiz?",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=vote_buttons),
                parse_mode="HTML"
            )
        except Exception:
            pass

    game["phase_task"] = asyncio.create_task(voting_timer_task(chat_id, game["round"]))


@dp.callback_query(F.data.startswith("vote:"))
async def cb_cast_vote(call: types.CallbackQuery):
    uid = call.from_user.id
    chat_id = user_group.get(uid)
    if not chat_id or chat_id not in games:
        return await call.answer("O'yin topilmadi!", show_alert=True)

    game = games[chat_id]
    if game["phase"] != "VOTING":
        return await call.answer("Ovoz berish yakunlangan!", show_alert=True)

    player = game["players"].get(uid)
    if not player or not player["alive"]:
        return await call.answer("Siz ovoz bera olmaysiz!", show_alert=True)

    if uid in game["votes"]:
        return await call.answer("Siz allaqachon ovoz bergansiz!", show_alert=True)

    target_id = int(call.data.split(":")[1])
    target = game["players"].get(target_id)
    if not target or not target["alive"] or target.get("shielded"):
        return await call.answer("Bu nomzodga ovoz berib bo'lmaydi!", show_alert=True)

    game["votes"][uid] = target_id
    await call.message.edit_text(f"✅ Siz <b>{target['name']}</b>ga qarshi ovoz berdingiz. Boshqalarni kutamiz...", parse_mode="HTML")

    alive_count = sum(1 for p in game["players"].values() if p["alive"])
    voted_count = len(game["votes"])

    await bot.send_message(
        chat_id,
        f"✉️ <b>{player['name']}</b> o'z ovozini berdi ({voted_count}/{alive_count}).",
        parse_mode="HTML"
    )

    if voted_count >= alive_count:
        await finalize_voting(chat_id)


@dp.callback_query(F.data == "force_end_vote")
async def cb_force_end_vote(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    if not await is_host_or_admin(chat_id, call.from_user.id):
        return await call.answer("⛔ Faqat boshlovchi yoki guruh admini ovozlarni yakunlay oladi!", show_alert=True)

    if chat_id in games and games[chat_id]["phase"] == "VOTING":
        await finalize_voting(chat_id)
    await call.answer()


async def finalize_voting(chat_id: int):
    if chat_id not in games:
        return
    game = games[chat_id]
    cancel_phase_timer(game)

    if not game["votes"]:
        game["phase"] = "DISCUSSION"
        await bot.send_message(chat_id, "⚠️ Hech kim ovoz bermadi! Muhokama davom etadi.")
        game["phase_task"] = asyncio.create_task(discussion_timer_task(chat_id, game["round"]))
        return

    tally = {}
    vote_details = []
    for voter_id, target_id in game["votes"].items():
        weight = game["players"][voter_id].get("vote_weight", 1)
        tally[target_id] = tally.get(target_id, 0) + weight
        voter_name = game["players"][voter_id]["name"]
        target_name = game["players"][target_id]["name"]
        w_str = f" (x{weight} ovoz)" if weight > 1 else ""
        vote_details.append(f"• {voter_name}{w_str} ➡️ {target_name}")

    max_votes = max(tally.values())
    candidates = [tid for tid, count in tally.items() if count == max_votes]
    kicked_id = random.choice(candidates)
    kicked_player = game["players"][kicked_id]
    kicked_player["alive"] = False
    user_group.pop(kicked_id, None)

    full_dossier = format_dossier(kicked_player, reveal_all=True)
    details_str = "\n".join(vote_details)

    await bot.send_message(
        chat_id,
        f"📊 <b>OVOZ BERISH YAKUNLANDI!</b>\n\n"
        f"<b>Kim kimga ovoz berdi:</b>\n{details_str}\n\n"
        f"💀 Ko'pchilik ovozi ({max_votes} ta) bilan <b>{kicked_player['name']}</b> bunkerdan quvib chiqarildi!\n\n"
        f"📂 <b>Chiqib ketgan o'yinchining to'liq ma'lumotlari:</b>\n{full_dossier}",
        parse_mode="HTML"
    )

    alive_players = [p for p in game["players"].values() if p["alive"]]
    if len(alive_players) <= game["capacity"]:
        game["phase"] = "ENDED"
        winners_text = "\n\n".join([format_dossier(p, reveal_all=True) for p in alive_players])
        epilogue_text = generate_epilogue(game, alive_players)

        await bot.send_message(
            chat_id,
            f"🏆 <b>O'YIN YAKUNLANDI! BUNKER ESHIKLARI YOPILDI!</b>\n\n"
            f"🎉 <b>Bunkerga kirgan va omon qolgan ishtirokchilar ({len(alive_players)} kishi):</b>\n\n"
            f"{winners_text}\n\n"
            f"{epilogue_text}\n\n"
            f"🔄 Yangi o'yin boshlash uchun /bunker buyrug'ini yozing!",
            parse_mode="HTML"
        )
        for uid in list(game["players"].keys()):
            user_group.pop(uid, None)
        del games[chat_id]
    else:
        game["phase"] = "DISCUSSION"
        game["round"] += 1
        for p in game["players"].values():
            p["opened_in_round"] = False
            p["shielded"] = False
            p["vote_weight"] = 1

        event_text = ""
        if random.random() < 0.5:
            event_text = "\n\n" + random.choice(RANDOM_EVENTS)

        bot_info = await bot.get_me()
        await bot.send_message(
            chat_id,
            f"🔄 <b>{game['round']}-AYLANA BOSHLANDI! (⏱ Vaqt: {DISCUSSION_TIMEOUT} soniya)</b>\n"
            f"Tirik qolgan o'yinchilar botning shaxsiy chatiga (LS) kirib, navbatdagi 1 tadan kartasini ochsin!"
            f"{event_text}",
            reply_markup=get_group_control_kb(bot_info.username),
            parse_mode="HTML"
        )

        for pdata in alive_players:
            try:
                sent_pm = await bot.send_message(
                    pdata["id"],
                    f"🔄 <b>{game['round']}-Aylana boshlandi! (⏱ {DISCUSSION_TIMEOUT} s)</b>\n"
                    f"Navbatdagi kartangizni oching:\n\n"
                    f"{format_dossier(pdata, reveal_all=True)}",
                    reply_markup=get_pm_cards_keyboard(pdata),
                    parse_mode="HTML"
                )
                pdata["pm_msg_id"] = sent_pm.message_id
            except Exception:
                pass

        # Yangi aylana taymerini yoqamiz
        game["phase_task"] = asyncio.create_task(discussion_timer_task(chat_id, game["round"]))


# ================= RENDER UCHUN WEB-SERVER VA ISHGA TUSHIRISH =================

async def health_check(request):
    return web.Response(text="Bunker Bot 24/7 ishlamoqda!")

async def start_dummy_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Dummy server {port}-portda ishga tushdi")

async def main():
    print("🤖 Bunker PRO Guruh Boti (Taymerlar bilan) ishga tushdi!")
    await start_dummy_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
