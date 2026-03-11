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

# --- 🧠 TRUE MACHINE LEARNING LIBRARIES ---
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from aiogram.types import BufferedInputFile, InputMediaPhoto
import warnings
warnings.filterwarnings("ignore")
# ------------------------------------------

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

# MongoDB Setup
db_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = db_client['bigwin_database'] 
history_collection = db['game_history'] 
predictions_collection = db['predictions'] 

# ==========================================
# 🔧 2. SYSTEM VARIABLES 
# ==========================================
CURRENT_TOKEN = ""
LAST_PROCESSED_ISSUE = None
MAIN_MESSAGE_ID = None 
SESSION_START_ISSUE = None 
LAST_CAPTION_EDIT_TIME = 0 

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
        print("🗄 MongoDB ချိတ်ဆက်မှု အောင်မြင်ပါသည်။ (🚀 Casino Deep Memory Engine Enabled)")
    except Exception as e:
        pass

# ==========================================
# 🔑 3. ASYNC API FUNCTIONS
# ==========================================
async def fetch_with_retry(session, url, headers, json_data, retries=3):
    for attempt in range(retries):
        try:
            async with session.post(url, headers=headers, json=json_data, timeout=10) as response:
                return await response.json()
        except Exception:
            if attempt == retries - 1: return None
            await asyncio.sleep(1)

async def login_and_get_token(session: aiohttp.ClientSession):
    global CURRENT_TOKEN
    json_data = {
        'username': '959680090540',
        'pwd': 'Mitheint11',
        'phonetype': 1,
        'logintype': 'mobile',
        'packId': '',
        'deviceId': '51ed4ee0f338a1bb24063ffdfcd31ce6',
        'language': 7,
        'random': '452fa309995244de92103c0afbefbe9a',
        'signature': '202C655177E9187D427A26F3CDC00A52',
        'timestamp': 1773021618,
    }
    data = await fetch_with_retry(session, 'https://api.bigwinqaz.com/api/webapi/Login', BASE_HEADERS, json_data)
    if data and data.get('code') == 0:
        token_str = data.get('data', {}) if isinstance(data.get('data'), str) else data.get('data', {}).get('token', '')
        CURRENT_TOKEN = f"Bearer {token_str}"
        print("✅ Login အောင်မြင်ပါသည်။ Token အသစ် ရရှိပါပြီ。\n")
        return True
    return False

# ==========================================
# 🧠 4. CASINO DEEP MEMORY ENGINE (NEW)
# ==========================================
def casino_memory_predict(history_docs):
    """
    ကာစီနို၏ Algorithm ကို အတုခိုးထားသော Memory Bank နှင့် Macro Balance စနစ်
    """
    if len(history_docs) < 50: return "BIG", 55.0, "Data စုဆောင်းဆဲ..."
    
    docs = list(reversed(history_docs)) 
    sizes = [d.get('size', 'BIG') for d in docs]
    
    score_b, score_s = 0.0, 0.0
    logic_used = ""

    # 🧠 [Memory 1] DEEP N-GRAM BANK (အတိတ်ပုံစံများကို ရှာဖွေခြင်း)
    # လက်ရှိ နောက်ဆုံး ၄ ပွဲ၏ ပုံစံအတိုင်း အတိတ်မှာ ထွက်ခဲ့ဖူးသလား ရှာမည်
    pattern_length = 4
    if len(sizes) > pattern_length:
        current_pattern = sizes[-pattern_length:]
        b_memory, s_memory = 0, 0
        
        for i in range(len(sizes) - pattern_length):
            if sizes[i:i+pattern_length] == current_pattern:
                if i + pattern_length < len(sizes):
                    if sizes[i+pattern_length] == 'BIG': b_memory += 1
                    else: s_memory += 1
                    
        if b_memory > s_memory:
            score_b += 3.0
            logic_used += f"├ 📚 Deep Memory ({b_memory} ကြိမ် BIG ဆက်စပ်မှု)\n"
        elif s_memory > b_memory:
            score_s += 3.0
            logic_used += f"├ 📚 Deep Memory ({s_memory} ကြိမ် SMALL ဆက်စပ်မှု)\n"
        else:
            logic_used += "├ 📚 Deep Memory (မှတ်တမ်းမရှိသေးပါ)\n"

    # ⚖️ [Memory 2] MACRO BALANCE (ကာစီနို မျှခြေစနစ်)
    # နောက်ဆုံး ပွဲ ၁၀၀ တွင် တစ်ဘက်တည်း အရမ်းများနေပါက ကာစီနိုက အခြားတစ်ဘက်ကို ပြန်ထုတ်ပေးသည်
    last_100 = sizes[-100:] if len(sizes) >= 100 else sizes
    b_100 = last_100.count('BIG')
    s_100 = last_100.count('SMALL')
    
    if b_100 > (len(last_100) * 0.55): # အကြီး ၅၅% ထက်ကျော်နေရင် အသေးပြန်ချမည်
        score_s += 2.5
        logic_used += f"├ ⚖️ Casino Balance (SMALL သို့ မျှခြေပြန်ဆွဲမည်)\n"
    elif s_100 > (len(last_100) * 0.55): # အသေး ၅၅% ထက်ကျော်နေရင် အကြီးပြန်ချမည်
        score_b += 2.5
        logic_used += f"├ ⚖️ Casino Balance (BIG သို့ မျှခြေပြန်ဆွဲမည်)\n"
    else:
        logic_used += f"├ ⚖️ Casino Balance (မျှခြေ ၅၀/၅၀ ရှိနေသည်)\n"

    # 🌲 [Memory 3] MACHINE LEARNING (ပုံမှန် ခန့်မှန်းမှု)
    X, y = [], []
    window = 5
    def enc(s): return 1 if s == 'BIG' else 0
    for i in range(len(sizes) - window):
        X.append([enc(s) for s in sizes[i:i+window]])
        y.append(enc(sizes[i+window]))
        
    if len(X) > 10:
        clf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        clf.fit(X, y)
        rf_pred_num = clf.predict([[enc(s) for s in sizes[-window:]]])[0]
        rf_prob = max(clf.predict_proba([[enc(s) for s in sizes[-window:]]])[0])
        
        if rf_pred_num == 1:
            score_b += (rf_prob * 2.0)
        else:
            score_s += (rf_prob * 2.0)
            
    logic_used += "└ 🤖 ML Pattern Recognition"

    # 🏆 အပြီးသတ် ဆုံးဖြတ်ချက်
    final_pred = "BIG" if score_b > score_s else "SMALL"
    total_score = score_b + score_s
    if total_score == 0: return "BIG", 55.0, logic_used
    
    calc_prob = (max(score_b, score_s) / total_score) * 100
    final_prob = min(max(calc_prob, 70.0), 96.0) # Casino Memory သုံးထားသဖြင့် ယုံကြည်မှုနှုန်း ပိုမြင့်သည်
    
    return final_pred, final_prob, logic_used

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
    
    plt.suptitle("WINRATE TRACKING", color='white', fontsize=20, fontweight='bold', y=0.96)
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
            
    plt.figtext(0.5, -0.28, "DEV-WANG LIN", color='white', fontsize=15, fontweight='bold', ha='center', alpha=0.5)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100, facecolor='#1e222d')
    buf.seek(0)
    plt.close(fig)
    return buf

# ==========================================
# 🚀 6. MAIN LOGIC & UI UPDATER
# ==========================================
async def check_game_and_predict(session: aiohttp.ClientSession):
    global CURRENT_TOKEN, LAST_PROCESSED_ISSUE, MAIN_MESSAGE_ID, SESSION_START_ISSUE, LAST_CAPTION_EDIT_TIME
    
    if not CURRENT_TOKEN:
        if not await login_and_get_token(session): return

    headers = BASE_HEADERS.copy()
    headers['authorization'] = CURRENT_TOKEN

    json_data = {
        'pageSize': 10, 'pageNo': 1, 'typeId': 30, 'language': 7,
        'random': '1ef0a7aca52b4c71975c031dda95150e', 'signature': '7D26EE375971781D1BC58B7039B409B7', 'timestamp': 1772985040,
    }

    data = await fetch_with_retry(session, 'https://api.bigwinqaz.com/api/webapi/GetNoaverageEmerdList', headers, json_data)
    if not data or data.get('code') != 0:
        if data and (data.get('code') == 401 or "token" in str(data.get('msg')).lower()): CURRENT_TOKEN = ""
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

    if LAST_PROCESSED_ISSUE:
        next_issue = str(int(LAST_PROCESSED_ISSUE) + 1)
    else:
        next_issue = str(int(latest_issue) + 1)

    current_session_count = await predictions_collection.count_documents({
        "issue_number": {"$gte": SESSION_START_ISSUE}, 
        "win_lose": {"$ne": None}
    })
    
    if current_session_count >= 20: 
        SESSION_START_ISSUE = next_issue
    
    # ==============================================================
    # 🧠 PREDICTION LOGIC (CASINO MEMORY + TREND SURFER)
    # ==============================================================
    cursor = history_collection.find().sort("issue_number", -1).limit(5000)
    history_docs = await cursor.to_list(length=5000)
    
    recent_preds_cursor = predictions_collection.find({"win_lose": {"$ne": None}}).sort("issue_number", -1).limit(10)
    recent_preds = await recent_preds_cursor.to_list(length=10)
    
    current_lose_streak = 0
    for p in recent_preds:
        if p.get("win_lose") == "LOSE ❌":
            current_lose_streak += 1
        else:
            break

    predicted = "BIG (အကြီး) 🔴"
    base_prob = 55.0
    reason = "Data မလုံလောက်သေးပါ"
    
    if len(history_docs) >= 1:
        # 🚨 [၁] TREND SURFER (အရှုံး ၃ ပွဲဆက်ပါက ရေစီးကြောင်းအတိုင်းသာ လိုက်မည်)
        if current_lose_streak >= 3:
            last_actual_size = history_docs[0].get('size', 'BIG')
            predicted = "BIG (အကြီး) 🔴" if last_actual_size == "BIG" else "SMALL (အသေး) 🟢"
            base_prob = 98.0
            reason = (
                f"🚨 <b>Trend Surfer Protocol</b>\n"
                f"└ (အရှုံးဖြတ်တောက်ရန် ထွက်ပြီးသားအတိုင်း လိုက်ပါသည်)"
            )
            
        # 🤖 [၂] CASINO MEMORY CLONE PREDICTION 
        else:
            try:
                mem_pred, mem_prob, mem_logic = await asyncio.to_thread(casino_memory_predict, history_docs)
                predicted = "BIG (အကြီး) 🔴" if mem_pred == "BIG" else "SMALL (အသေး) 🟢"
                base_prob = mem_prob
                reason = (
                    f"🧠 <b>Casino Deep Memory Clone</b>\n"
                    f"{mem_logic}"
                )
            except Exception as e:
                predicted = "BIG (အကြီး) 🔴"
                base_prob = 55.0
                reason = "⚠️ Memory Syncing..."
    
    final_prob = min(max(round(base_prob, 1), 60.0), 98.0)
    predicted_result_db = "BIG" if "BIG" in predicted else "SMALL"
    
    await predictions_collection.update_one(
        {"issue_number": next_issue}, 
        {"$set": {"predicted_size": predicted_result_db}}, 
        upsert=True
    )

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

    seconds_left = 30 - (int(time.time()) % 30)
    
    tg_caption = (
        f"<b>WIN GO 30 SECONDS</b>\n"
        f"⏰ Next Result In: <b>{seconds_left}s</b>\n\n"
        f"{table_str}\n"
        f"🅿️ <b>Period:</b> {next_issue[:3]}**{next_issue[-4:]}\n"
        f"🎯 <b>Predict: {predicted}</b>\n"
        f"📈 <b>ဖြစ်နိုင်ခြေ:</b> {final_prob}%\n"
        f"💡 <b>အကြောင်းပြချက်:</b>\n"
        f"{reason}"
    )
    
    current_time = time.time()
    try:
        if is_new_issue or not MAIN_MESSAGE_ID:
            img_buf = await asyncio.to_thread(generate_winrate_chart, session_preds)
            unique_filename = f"winrate_chart_{int(current_time)}.png"
            photo = BufferedInputFile(img_buf.read(), filename=unique_filename)
            
            if MAIN_MESSAGE_ID:
                media = InputMediaPhoto(media=photo, caption=tg_caption, parse_mode="HTML")
                await bot.edit_message_media(chat_id=TELEGRAM_CHANNEL_ID, message_id=MAIN_MESSAGE_ID, media=media)
            else:
                msg = await bot.send_photo(chat_id=TELEGRAM_CHANNEL_ID, photo=photo, caption=tg_caption)
                MAIN_MESSAGE_ID = msg.message_id
            
            LAST_CAPTION_EDIT_TIME = current_time 
            
        else:
            if current_time - LAST_CAPTION_EDIT_TIME >= 1.0:
                if MAIN_MESSAGE_ID:
                    await bot.edit_message_caption(chat_id=TELEGRAM_CHANNEL_ID, message_id=MAIN_MESSAGE_ID, caption=tg_caption, parse_mode="HTML")
                LAST_CAPTION_EDIT_TIME = current_time
                
    except TelegramRetryAfter as e:
        LAST_CAPTION_EDIT_TIME = current_time + e.retry_after
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            pass 
        elif "message to edit not found" in str(e):
            MAIN_MESSAGE_ID = None 

# ==========================================
# 🔄 6. BACKGROUND TASK 
# ==========================================
async def auto_broadcaster():
    await init_db() 
    async with aiohttp.ClientSession() as session:
        await login_and_get_token(session)
        while True:
            await check_game_and_predict(session)
            await asyncio.sleep(0.5) 

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("👋 မင်္ဂလာပါ။ စနစ်သည် ကာစီနို၏ မှတ်ဉာဏ်ကို အတုခိုးသည့် Deep Memory System ဖြင့် အလုပ်လုပ်နေပါပြီ။")

async def main():
    print("🚀 Aiogram Bigwin Bot (Casino Deep Memory Edition) စတင်နေပါပြီ...\n")
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(auto_broadcaster())
    await dp.start_polling(bot)

if __name__ == '__main__':
    try: asyncio.run(main())
    except KeyboardInterrupt: print("Bot ကို ရပ်တန့်လိုက်ပါသည်။")
