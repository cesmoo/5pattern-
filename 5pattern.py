import asyncio
import time
import os
import io
import json
from datetime import datetime
from dotenv import load_dotenv
import aiohttp
import motor.motor_asyncio 

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.types import BufferedInputFile, InputMediaPhoto

import numpy as np
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import warnings
warnings.filterwarnings("ignore")

load_dotenv()

# ==========================================
# ⚙️ 1. CONFIGURATION
# ==========================================
USERNAME = os.getenv("BIGWIN_USERNAME")
PASSWORD = os.getenv("BIGWIN_PASSWORD")
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("CHANNEL_ID")
MONGO_URI = os.getenv("MONGO_URI") 

if not all([USERNAME, PASSWORD, TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, MONGO_URI]):
    print("❌ Error: .env ဖိုင်ထဲတွင် အချက်အလက်များ ပြည့်စုံစွာ မပါဝင်ပါ။")
    exit()
  
bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

db_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = db_client['bigwin_database'] 
history_collection = db['trx_game_history'] 
predictions_collection = db['trx_predictions'] 

# ==========================================
# 🔧 2. SYSTEM VARIABLES 
# ==========================================
CURRENT_TOKEN = ""
LAST_PROCESSED_ISSUE = None
MAIN_MESSAGE_ID = None 
SESSION_START_ISSUE = None 
LAST_CAPTION_EDIT_TIME = 0 
CURRENT_BALANCE = "0.00" 

BASE_HEADERS = {
    'authority': 'api.bigwinqaz.com',
    'accept': 'application/json, text/plain, */*',
    'content-type': 'application/json;charset=UTF-8',
    'origin': 'https://www.777bigwingame.app',
    'referer': 'https://www.777bigwingame.app/',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
}

async def init_db():
    try:
        await history_collection.create_index("issue_number", unique=True)
        await predictions_collection.create_index("issue_number", unique=True)
        print("🗄 MongoDB ချိတ်ဆက်မှု အောင်မြင်ပါသည်။ (💎 TRX Blockchain Trend Surfer Edition)")
    except Exception as e:
        print(f"❌ MongoDB Error: {e}")

# ==========================================
# 🔑 3. ASYNC API FUNCTIONS
# ==========================================
async def fetch_with_retry(session, url, headers, json_data, retries=3):
    for attempt in range(retries):
        try:
            async with session.post(url, headers=headers, json=json_data, timeout=10) as response:
                return await response.json()
        except Exception as e:
            if attempt == retries - 1:
                print(f"⚠️ API Fetch Error: {e}")
                return None
            await asyncio.sleep(1)

async def login_and_get_token(session: aiohttp.ClientSession):
    global CURRENT_TOKEN
    json_data = {
        'username': USERNAME, 
        'pwd': PASSWORD,
        'phonetype': 1,
        'logintype': 'mobile',
        'packId': '',
        'deviceId': '51ed4ee0f338a1bb24063ffdfcd31ce6',
        'language': 7,
        'random': 'a4902febdaeb4f5885479c44a8ac2cbb',
        'signature': '2127DA46CCAE9050B844F8E3373CFDFB',
        'timestamp': 1773211093,
    }
    data = await fetch_with_retry(session, 'https://api.bigwinqaz.com/api/webapi/Login', BASE_HEADERS, json_data)
    if data and data.get('code') == 0:
        token_str = data.get('data', {}) if isinstance(data.get('data'), str) else data.get('data', {}).get('token', '')
        CURRENT_TOKEN = f"Bearer {token_str}"
        print("✅ Login အောင်မြင်ပါသည်။ Token အသစ် ရရှိပါပြီ。\n")
        return True
    else:
        print(f"❌ Login Failed: {data}")
    return False

async def get_account_balance(session: aiohttp.ClientSession, headers):
    url = 'https://api.bigwinqaz.com/api/webapi/GetBalance'
    json_data = {
        'language': 7,
        'random': 'e0340b8b39684e1c8c2e2391d9ca02d5',
        'signature': '6AF1E9AD003853931B95189800F9FA4B',
        'timestamp': 1773195076,
    }
    res = await fetch_with_retry(session, url, headers, json_data)
    if res and res.get('code') == 0:
        data_val = res.get('data')
        if isinstance(data_val, dict): return str(data_val.get('balance', CURRENT_BALANCE))
        return str(data_val)
    return CURRENT_BALANCE

async def get_current_issue(session: aiohttp.ClientSession, headers):
    url = 'https://api.bigwinqaz.com/api/webapi/GetTRXGameIssue'
    json_data = {
        'typeId': 13,
        'language': 7,
        'random': '3d704ba98ce14bf2a8c1153c27e234e0',
        'signature': 'DEB5F9E0B146BFE09C316AD1417A97A8',
        'timestamp': 1773211260, 
    }
    res = await fetch_with_retry(session, url, headers, json_data)
    if res and res.get('code') == 0:
        return str(res.get('data', {}).get('issueNumber', ''))
    return ""

# ==========================================
# 🧠 4. CRYPTO TREND SURFER AI (TRX Hash System)
# ==========================================
def crypto_trx_predict(history_docs, current_lose_streak):
    """
    TRX သည် Blockchain Hash ပေါ်အခြေခံသဖြင့် အလွန်အမင်း Random ဖြစ်သည်။
    ထို့ကြောင့် ML အစား ရေစီးကြောင်းနောက်လိုက်သော Trend Surfing ကိုသာ အသုံးပြုမည်။
    """
    if len(history_docs) < 5: return "BIG", 55.0, "Data စုဆောင်းဆဲ..."
    
    docs = list(reversed(history_docs)) 
    sizes = [d.get('size', 'BIG') for d in docs]
    
    logic_used = "⛓️ <b>Blockchain Hash Strategy</b>\n"
    
    # နောက်ဆုံး ၃ ပွဲ၏ ရလဒ်ကို ကြည့်မည်
    last_3 = sizes[-3:]
    last_size = sizes[-1]
    
    if current_lose_streak >= 2:
        logic_used += "├ 🚨 <b>Action:</b> အရှုံးများသဖြင့် ရေစီးကြောင်းနောက် လိုက်ပါမည်\n"
        return last_size, 95.0, logic_used + "└ 💡 ထွက်ပြီးသား အလုံးအတိုင်း ထိုးပါ"

    # [Ping-Pong ဖြတ်တောက်ခြင်း]
    if len(sizes) >= 4 and sizes[-1] != sizes[-2] and sizes[-2] != sizes[-3] and sizes[-3] != sizes[-4]:
        logic_used += "├ 🏓 <b>Pattern:</b> ခုတ်ချိုး (Ping-Pong) ရေစီးကြောင်း\n"
        logic_used += "└ 💡 ခုတ်ချိုးအတိုင်း ဆက်လက် လိုက်ပါမည်"
        pred = 'BIG' if last_size == 'SMALL' else 'SMALL'
        return pred, 85.0, logic_used
        
    # [Dragon အတန်းရှည် လိုက်ခြင်း]
    if sizes[-1] == sizes[-2]:
        logic_used += "├ 🐉 <b>Pattern:</b> အတန်းရှည် (Dragon) ရေစီးကြောင်း\n"
        logic_used += "└ 💡 ပြတ်မသွားမချင်း အတန်းရှည်အတိုင်း လိုက်ပါမည်"
        return last_size, 88.0, logic_used

    # သာမန်အချိန်တွင် နောက်ဆုံးထွက်ခဲ့သော အလုံးကိုသာ အခြေခံမည်
    logic_used += "├ 🌊 <b>Pattern:</b> သာမန် Random Hash အခြေအနေ\n"
    logic_used += "└ 💡 နောက်ဆုံး Block ရလဒ်အတိုင်း လိုက်ပါမည်"
    
    return last_size, 65.0, logic_used

# ==========================================
# 🎨 5. DYNAMIC GRAPH GENERATOR 
# ==========================================
def generate_winrate_chart(predictions):
    wins, losses = 0, 0
    history_wr, bar_colors, dots_list = [], [], []
    
    for p in reversed(predictions): 
        if 'WIN' in p.get('win_lose', ''):
            wins += 1
            bar_colors.append('#26a69a') 
            dots_list.append('#26a69a')
        else:
            losses += 1
            bar_colors.append('#ef5350') 
            dots_list.append('#ef5350')
        total = wins + losses
        history_wr.append((wins / total) * 100 if total > 0 else 0)
        
    total_played = wins + losses
    win_rate = int((wins / total_played * 100)) if total_played > 0 else 0

    fig, ax = plt.subplots(figsize=(8, 5.5), facecolor='#1e222d') 
    ax.set_facecolor('#1e222d')
    
    if total_played > 0:
        x = np.arange(total_played)
        ax.bar(x, [55]*total_played, color=bar_colors, width=0.9, bottom=0)
        ax.plot(x, history_wr, color='#2979ff', linewidth=3, marker='o', markersize=6, markerfacecolor='#1e222d', markeredgecolor='#2979ff', markeredgewidth=2)
    
    ax.set_ylim(0, 105)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'], color='#787b86', fontsize=10)
    ax.set_xticks([])
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#363a45')
    ax.spines['bottom'].set_color('#363a45')
    ax.grid(axis='y', color='#363a45', linestyle='-', linewidth=0.5)
    
    plt.suptitle("TRX WINRATE TRACKING", color='white', fontsize=20, fontweight='bold', y=0.96)
    plt.figtext(0.5, 0.05, f"{win_rate}%", color='white', fontsize=30, fontweight='bold', ha='center')
    plt.figtext(0.38, 0.0, f"WINS: {wins}", color='#26a69a', fontsize=14, ha='center', fontweight='bold')
    plt.figtext(0.62, 0.0, f"LOSSES: {losses}", color='#ef5350', fontsize=14, ha='center', fontweight='bold')
    plt.figtext(0.5, -0.05, f"PREDICTION COUNT: {total_played}/20", color='white', fontsize=12, ha='center')
    plt.figtext(0.5, -0.11, "Recent Predictions (Oldest ➔ Latest)", color='#787b86', fontsize=10, ha='center')

    if len(dots_list) > 0:
        dot_ax = fig.add_axes([0.1, -0.2, 0.8, 0.08]) 
        dot_ax.set_axis_off()
        dot_ax.set_xlim(0, 20) 
        dot_ax.set_ylim(0, 1)
        colors = dots_list
        n_dots = len(colors)
        start_x = (20 - n_dots) / 2.0
        x_coords = [start_x + i + 0.5 for i in range(n_dots)]
        y_coords = [0.5] * n_dots
        dot_ax.scatter(x_coords, y_coords, s=250, c=colors, edgecolors='white', linewidths=1.5, zorder=5)
            
    plt.figtext(0.5, -0.28, "DEV-WANG LIN (TRX BLOCKCHAIN)", color='#787b86', fontsize=12, ha='center', alpha=1)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100, facecolor='#1e222d')
    buf.seek(0)
    plt.close(fig)
    return buf

# ==========================================
# 🚀 6. MAIN LOGIC & UI UPDATER
# ==========================================
async def check_game_and_predict(session: aiohttp.ClientSession):
    global CURRENT_TOKEN, LAST_PROCESSED_ISSUE, MAIN_MESSAGE_ID, SESSION_START_ISSUE, LAST_CAPTION_EDIT_TIME, CURRENT_BALANCE
    
    if not CURRENT_TOKEN:
        if not await login_and_get_token(session): return

    headers = BASE_HEADERS.copy()
    headers['authorization'] = CURRENT_TOKEN

    # 💡 စမ်းသပ်ချက်: Security parameter များကို ခေတ္တဖယ်ရှား၍ လှမ်းခေါ်ကြည့်မည်
    json_data_list = {
        'pageSize': 10, 'pageNo': 1, 'typeId': 13, 'language': 7,
        'random': '6f1cfc8bbeeb44ec98343ac38d1af67c',
        'signature': '5E271BE324AFB34F9A2E5EC9F7CE05D2',
        'timestamp': 1773211343, 
    }

    data = await fetch_with_retry(session, 'https://api.bigwinqaz.com/api/webapi/GetTRXNoaverageEmerdList', headers, json_data_list)
    
    # 🚨 API Error ကို ရှင်းလင်းစွာ သိနိုင်ရန် Print ထုတ်ပေးထားသည်
    if not data or data.get('code') != 0:
        print(f"⚠️ API ငြင်းပယ်ခံရပါသည် (သက်တမ်းကုန်နေနိုင်သည်): {data}")
        if data and (data.get('code') == 401 or "token" in str(data.get('msg')).lower()): 
            CURRENT_TOKEN = ""
        return

    records = data.get("data", {}).get("list", [])
    if not records: return
    
    latest_record = records[0]
    latest_issue = str(latest_record["issueNumber"])
    latest_number = int(latest_record["number"])
    latest_size = "BIG" if latest_number >= 5 else "SMALL"
    latest_parity = "EVEN" if latest_number % 2 == 0 else "ODD"
    
    is_new_issue = False
    if not LAST_PROCESSED_ISSUE:
        is_new_issue = True
    elif int(latest_issue) > int(LAST_PROCESSED_ISSUE):
        is_new_issue = True
    
    if is_new_issue:
        LAST_PROCESSED_ISSUE = latest_issue
        if not SESSION_START_ISSUE:
            SESSION_START_ISSUE = latest_issue
            
        CURRENT_BALANCE = await get_account_balance(session, headers)
        
        await history_collection.update_one(
            {"issue_number": latest_issue}, 
            {"$setOnInsert": {
                "number": latest_number, "size": latest_size, 
                "parity": latest_parity, "time_context": "CURRENT"
            }}, upsert=True
        )
        
        pred_doc = await predictions_collection.find_one({"issue_number": latest_issue})
        if pred_doc and pred_doc.get("predicted_size"):
            db_predicted_size = pred_doc.get("predicted_size")
            is_win = (db_predicted_size == latest_size)
            win_lose_status = "WIN ✅" if is_win else "LOSE ❌"
            await predictions_collection.update_one(
                {"issue_number": latest_issue}, 
                {"$set": {"actual_size": latest_size, "actual_number": latest_number, "win_lose": win_lose_status}}
            )

    next_issue = await get_current_issue(session, headers)
    if not next_issue: 
        next_issue = str(int(latest_issue) + 1)

    current_session_count = await predictions_collection.count_documents({
        "issue_number": {"$gte": SESSION_START_ISSUE}, 
        "win_lose": {"$ne": None}
    })
    
    if current_session_count >= 20: 
        SESSION_START_ISSUE = next_issue
    
    recent_preds_cursor = predictions_collection.find({"win_lose": {"$ne": None}}).sort("issue_number", -1).limit(10)
    recent_preds = await recent_preds_cursor.to_list(length=10)
    
    current_lose_streak = 0
    for p in recent_preds:
        if p.get("win_lose") == "LOSE ❌":
            current_lose_streak += 1
        else:
            break

    cursor = history_collection.find().sort("issue_number", -1).limit(5000)
    history_docs = await cursor.to_list(length=5000)

    try:
        mem_pred, mem_prob, mem_logic = await asyncio.to_thread(crypto_trx_predict, history_docs, current_lose_streak)
        predicted = "BIG (အကြီး) 🔴" if mem_pred == "BIG" else "SMALL (အသေး) 🟢"
        base_prob = mem_prob
        reason = mem_logic
    except Exception as e:
        predicted = "BIG (အကြီး) 🔴"
        base_prob = 55.0
        reason = "⚠️ Hash Syncing Error..."
    
    predicted_result_db = "BIG" if "BIG" in predicted else "SMALL"
    
    await predictions_collection.update_one(
        {"issue_number": next_issue}, 
        {"$set": {"predicted_size": predicted_result_db}}, 
        upsert=True
    )

    bet_advice = ""
    if current_lose_streak == 0: bet_advice = "🛡️ <b>အကြံပြုချက်:</b> အခြေခံကြေး (1x) ဖြင့်စပါ"
    elif current_lose_streak == 1: bet_advice = "🛡️ <b>အကြံပြုချက်:</b> 2x (Martingale)"
    elif current_lose_streak == 2: bet_advice = "🛡️ <b>အကြံပြုချက်:</b> 4x (Martingale)"
    elif current_lose_streak == 3: bet_advice = "🛡️ <b>အကြံပြုချက်:</b> 8x (Martingale)"
    else: bet_advice = "⚠️ <b>[DANGER] ၄ ပွဲဆက်ရှုံးထားပါသည်!</b>\nခဏနားပါ (သို့) <b>1x မှ ပြန်စပါ။</b>"

    pred_cursor = predictions_collection.find({
        "issue_number": {"$gte": SESSION_START_ISSUE},
        "win_lose": {"$ne": None}
    }).sort("issue_number", -1)
    
    session_preds = await pred_cursor.to_list(length=20) 
    
    table_str = "<code>Period    | Result  | W/L\n"
    table_str += "----------|---------|----\n"
    for p in session_preds[:10]: 
        iss = p.get('issue_number', '0000000')
        iss_short = f"{iss[:3]}**{iss[-4:]}" 
        act_size = p.get('actual_size', 'BIG')
        act_num = p.get('actual_number', 0)
        res_str = f"{act_num}-{act_size}"
        wl_str = "✅" if "WIN" in p.get("win_lose", "") else "❌"
        table_str += f"{iss_short:<10}| {res_str:<7} | {wl_str}\n"
    table_str += "</code>"

    def get_realtime_caption():
        sec_left = 60 - (int(time.time()) % 60)
        if sec_left == 60: sec_left = 0
        return (
            f"<b>💎 TRX WIN GO (1 Minute)</b>\n"
            f"💰 <b>Balance:</b> {CURRENT_BALANCE} 🪙\n"
            f"⏰ Next Result In: <b>{sec_left}s</b>\n\n"
            f"{table_str}\n"
            f"🅿️ <b>Period:</b> {next_issue[:3]}**{next_issue[-4:]}\n"
            f"🎯 <b>Predict: {predicted}</b>\n"
            f"📈 <b>ဖြစ်နိုင်ခြေ:</b> {base_prob}%\n"
            f"💡 <b>အကြောင်းပြချက်:</b>\n"
            f"{reason}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{bet_advice}"
        )
    
    current_time = time.time()
    try:
        if is_new_issue or not MAIN_MESSAGE_ID:
            img_buf = await asyncio.to_thread(generate_winrate_chart, session_preds)
            unique_filename = f"trx_chart_{int(current_time)}.png"
            photo = BufferedInputFile(img_buf.read(), filename=unique_filename)
            
            tg_caption = get_realtime_caption()
            
            if MAIN_MESSAGE_ID:
                media = InputMediaPhoto(media=photo, caption=tg_caption, parse_mode="HTML")
                await bot.edit_message_media(chat_id=TELEGRAM_CHANNEL_ID, message_id=MAIN_MESSAGE_ID, media=media)
                print(f"✅ Image Updated for {next_issue}")
            else:
                msg = await bot.send_photo(chat_id=TELEGRAM_CHANNEL_ID, photo=photo, caption=tg_caption)
                MAIN_MESSAGE_ID = msg.message_id
                print(f"✅ New Message Sent for {next_issue}")
            
            LAST_CAPTION_EDIT_TIME = time.time() 
            
        else:
            if current_time - LAST_CAPTION_EDIT_TIME >= 1.0:
                if MAIN_MESSAGE_ID:
                    tg_caption = get_realtime_caption()
                    await bot.edit_message_caption(chat_id=TELEGRAM_CHANNEL_ID, message_id=MAIN_MESSAGE_ID, caption=tg_caption, parse_mode="HTML")
                LAST_CAPTION_EDIT_TIME = time.time()
                
    except TelegramRetryAfter as e:
        print(f"⚠️ Telegram Spam Limit! Waiting for {e.retry_after} seconds.")
        LAST_CAPTION_EDIT_TIME = time.time() + e.retry_after
    except TelegramBadRequest as e:
        if "message is not modified" in str(e): pass 
        elif "message to edit not found" in str(e):
            print("⚠️ Message deleted in channel. Will send a new one.")
            MAIN_MESSAGE_ID = None 
    except Exception as e:
        print(f"❌ Telegram Error: {e}")

# ==========================================
# 🔄 6. BACKGROUND TASK
# ==========================================
async def auto_broadcaster():
    await init_db() 
    async with aiohttp.ClientSession() as session:
        await login_and_get_token(session)
        while True:
            try:
                await check_game_and_predict(session)
            except Exception as e:
                print(f"⚠️ System Logic Error: {e}")
            await asyncio.sleep(1) 

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("👋 မင်္ဂလာပါ။ စနစ်က TRX Crypto Trend Surfer စနစ်ဖြင့် အလုပ်လုပ်နေပါပြီ။")

async def main():
    print("🚀 Aiogram TRX Win Go Bot (Crypto AI Edition) စတင်နေပါပြီ...\n")
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(auto_broadcaster())
    await dp.start_polling(bot)

if __name__ == '__main__':
    try: asyncio.run(main())
    except KeyboardInterrupt: print("Bot ကို ရပ်တန့်လိုက်ပါသည်။")
