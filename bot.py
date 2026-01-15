import telebot
import requests
import time
import json
import os
import re
import threading
from telebot import types
from flask import Flask
from threading import Thread
from pymongo import MongoClient

# --- KEEP ALIVE SYSTEM FOR RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CONFIGURATION & DATABASE ---
TOKEN = "8522785774:AAGAan9a0iS0nQB7poDRsQ6SY33acLXdLrI"
OWNER_IDS = [6703335929, 6041728084] 
CHANNEL_ID = "@alphacodex369" 
GROUP_ID = "@CodexGroupTm"      
API_URL = "https://info-ekansh.vercel.app/api/number?num="

# MongoDB Connection
MONGO_URI = "mongodb+srv://darkgangdarks_db_user:aEEYR59YEVameS1y@cluster0.iyakwh0.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client['bot_database']
users_col = db['users']
groups_col = db['groups']
banned_col = db['banned']

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
bot_running = True

# --- HELPERS ---
def is_subscribed(user_id):
    try:
        status1 = bot.get_chat_member(CHANNEL_ID, user_id).status
        status2 = bot.get_chat_member(GROUP_ID, user_id).status
        allowed = ['member', 'administrator', 'creator', 'restricted']
        return status1 in allowed and status2 in allowed
    except: return False

def parse_broadcast_text(text):
    pattern = r"\[([^|]+)\|([^\]]+)\]"
    buttons = re.findall(pattern, text)
    clean_text = re.sub(pattern, "", text).strip()
    
    markup = types.InlineKeyboardMarkup()
    for name, url in buttons:
        markup.add(types.InlineKeyboardButton(text=name.strip(), url=url.strip()))
    
    return clean_text, markup if buttons else None

# --- AUTO DELETE TIMER LOGIC ---
def countdown_timer(chat_id, message_id, original_text, mention_name):
    timer_steps = [40, 30, 20, 10, 5]
    for sec in timer_steps:
        time.sleep(10 if sec > 10 else 5)
        stylish_sec = str(sec).replace('0','𝟢').replace('1','𝟣').replace('2','𝟤').replace('3','𝟥').replace('4','𝟦').replace('5','𝟧')
        try:
            new_footer = f"\n\n👤 ᴜꜱᴇʀ: {mention_name}\n⏳ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ: {stylish_sec}𝗌"
            bot.edit_message_text(original_text + new_footer, chat_id, message_id, parse_mode="HTML")
        except:
            break
    
    time.sleep(5)
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

# --- DATABASE SYNC ---
def register_user(message):
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    first_name = message.from_user.first_name or "User"
    
    if not users_col.find_one({"user_id": user_id}):
        users_col.insert_one({
            "user_id": user_id,
            "username": username,
            "name": first_name,
            "usage_count": 0,
            "last_use": 0
        })
    
    if message.chat.type in ['group', 'supergroup']:
        if not groups_col.find_one({"chat_id": message.chat.id}):
            groups_col.insert_one({"chat_id": message.chat.id, "title": message.chat.title})

# --- COMMANDS ---
@bot.message_handler(commands=['start'])
def start(message):
    register_user(message)
    if not bot_running and message.from_user.id not in OWNER_IDS: return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("ᴊᴏɪɴ ɢʀᴏᴜᴘ", url=f"https://t.me/{GROUP_ID.replace('@','')}")
    btn2 = types.InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{CHANNEL_ID.replace('@','')}")
    btn3 = types.InlineKeyboardButton("ᴄʜᴇᴄᴋ sᴛᴀᴛᴜs", callback_data="check_verify")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, "<b>ᴀᴅᴅᴇᴅ: ᴡᴇʟᴄᴏᴍᴇ! ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ᴛᴏ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ.</b>", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_verify")
def verify(call):
    if is_subscribed(call.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f"https://t.me/{bot.get_me().username}?startgroup=true"))
        bot.edit_message_text("<b>ᴀᴅᴅᴇᴅ: ᴠᴇʀɪғɪᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!</b>\nʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴜsᴇ /num ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ.", call.message.chat.id, call.message.message_id, reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, "❌ ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ғɪʀsᴛ!", show_alert=True)

@bot.message_handler(commands=['num'])
def info_fetch(message):
    register_user(message)
    if not bot_running: return
    uid = message.from_user.id
    
    if banned_col.find_one({"user_id": uid}): return
    
    if not is_subscribed(uid):
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("ᴊᴏɪɴ ɢʀᴏᴜᴘ", url=f"https://t.me/{GROUP_ID.replace('@','')}")
        btn2 = types.InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{CHANNEL_ID.replace('@','')}")
        markup.add(btn1, btn2)
        return bot.reply_to(message, "<b>ᴀᴅᴅᴇᴅ: ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ғɪʀsᴛ!</b>", reply_markup=markup)

    user_data = users_col.find_one({"user_id": uid})
    now = time.time()
    
    if now - user_data.get('last_use', 0) < 3600 and user_data.get('usage_count', 0) >= 10:
        return bot.reply_to(message, "<b>ᴀᴅᴅᴇᴅ: ʟɪᴍɪᴛ ᴇxᴄᴇᴇᴅᴇᴅ! ᴛʀʏ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 1 ʜᴏᴜʀ.</b>")
    
    new_count = 1 if now - user_data.get('last_use', 0) >= 3600 else user_data.get('usage_count', 0) + 1
    users_col.update_one({"user_id": uid}, {"$set": {"usage_count": new_count, "last_use": now}})

    text = message.text.split()
    if len(text) < 2: return bot.reply_to(message, "<b>ᴀᴅᴅᴇᴅ: ᴜsᴀɢᴇ:</b> <code>/num 9876543210</code>")
    num = text[1]

    try:
        res = requests.get(f"{API_URL}{num}").json()
        if not res.get("success") or not res.get('data', {}).get('result'):
            return bot.reply_to(message, "<b>ᴀᴅᴅᴇᴅ: ɴᴏ ᴅᴀᴛᴀ ғᴏᴜɴᴅ!</b>")
        
        results = res['data']['result']
        mention_name = f"<a href='tg://user?id={uid}'>{message.from_user.first_name}</a>"
        
        for item in results:
            response = f"<b>ᴀᴅᴅᴇᴅ ɪɴғᴏ ғᴏʀ:</b> <code>{num}</code>\n"
            response += "━━━━━━━━━━━━━━━━━━\n"
            response += f"👤 <b>ɴᴀᴍᴇ:</b> <code>{item.get('name') or 'N/A'}</code>\n"
            response += f"👴 <b>ғᴀᴛʜᴇʀ:</b> <code>{item.get('father_name') or 'N/A'}</code>\n"
            response += f"📱 <b>ᴍᴏʙɪʟᴇ:</b> <code>{item.get('mobile') or 'N/A'}</code>\n"
            response += f"📞 <b>ᴀʟᴛ:</b> <code>{item.get('alt_mobile') or 'N/A'}</code>\n"
            response += f"🆔 <b>ɪᴅ:</b> <code>{item.get('id_number') or 'N/A'}</code>\n"
            response += f"🏢 <b>ᴄɪʀᴄʟᴇ:</b> <code>{item.get('circle') or 'N/A'}</code>\n"
            response += f"📧 <b>ᴇᴍᴀɪʟ:</b> <code>{item.get('email') or 'N/A'}</code>\n"
            response += f"📍 <b>ᴀᴅᴅʀᴇss:</b> <code>{item.get('address') or 'N/A'}</code>\n"
            response += "━━━━━━━━━━━━━━━━━━\n"
            response += f"<blockquote>ɴᴏᴛᴇ: ᴄᴏᴅᴇ–ɪɴꜰᴏ\nᴅᴇᴠ: ᴅx–ᴄᴏᴅᴇx\nsᴏᴜʀᴄᴇ: @termuxcodex</blockquote>"
            
            footer = f"\n\n👤 ᴜꜱᴇʀ: {mention_name}\n⏳ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ: 𝟦𝟢ꜱ"
            sent_msg = bot.send_message(message.chat.id, response + footer)
            
            threading.Thread(target=countdown_timer, args=(message.chat.id, sent_msg.message_id, response, mention_name)).start()
            time.sleep(1)
            
    except Exception as e:
        bot.reply_to(message, f"<b>ᴄᴏᴅᴇx: ᴇʀʀᴏʀ!</b>")

# --- OWNER CONTROLS ---
@bot.message_handler(commands=['id'], func=lambda m: m.from_user.id in OWNER_IDS)
def send_user_list(message):
    all_users = users_col.find()
    file_content = "ID | Username | Name\n" + "-"*35 + "\n"
    for u in all_users:
        file_content += f"{u['user_id']} | @{u.get('username','N/A')} | {u.get('name','User')}\n"
    
    filename = "bot_users.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(file_content)
    
    with open(filename, "rb") as f:
        bot.send_document(message.chat.id, f, caption="<b>ᴀᴅᴅᴇᴅ: ʙᴏᴛ ᴜsᴇʀs ʟɪsᴛ</b>")
    os.remove(filename)

@bot.message_handler(commands=['broadcast'], func=lambda m: m.from_user.id in OWNER_IDS)
def broadcast_manager(message):
    raw_text = message.text.replace("/broadcast", "").strip()
    if not raw_text: return bot.reply_to(message, "<b>ᴜsᴀɢᴇ:</b> /broadcast ᴛᴇxᴛ [ʙᴛɴ ɴᴀᴍᴇ | URL]")

    clean_msg, markup = parse_broadcast_text(raw_text)
    users = users_col.find(); groups = groups_col.find()
    count = 0
    for u in users:
        try: bot.send_message(u['user_id'], clean_msg, reply_markup=markup); count += 1
        except: pass
    for g in groups:
        try: bot.send_message(g['chat_id'], clean_msg, reply_markup=markup); count += 1
        except: pass
    bot.reply_to(message, f"<b>ᴀᴅᴅᴇᴅ: ʙʀᴏᴀᴅᴄᴀsᴛ sᴜᴄᴄᴇssғᴜʟ ᴛᴏ {count} ᴛᴀʀɢᴇᴛs.</b>")

@bot.message_handler(commands=['stop', 'run', 'ping', 'ban', 'unban'], func=lambda m: m.from_user.id in OWNER_IDS)
def owner_actions(message):
    global bot_running
    cmd = message.text.split()
    if '/stop' in message.text: bot_running = False; bot.reply_to(message, "<b>ᴀᴅᴅᴇᴅ: ʙᴏᴛ sᴛᴏᴘᴘᴇᴅ.</b>")
    elif '/run' in message.text: bot_running = True; bot.reply_to(message, "<b>ᴀᴅᴅᴇᴅ: ʙᴏᴛ ʀᴜɴɴɪɴɢ.</b>")
    elif '/ping' in message.text: bot.reply_to(message, "<b>ᴀᴅᴅᴇᴅ: ᴘᴏɴɢ! sᴘᴇᴇᴅ: ᴇxᴄᴇʟʟᴇɴᴛ</b>")
    elif '/ban' in message.text and len(cmd) > 1:
        banned_col.update_one({"user_id": int(cmd[1])}, {"$set": {"user_id": int(cmd[1])}}, upsert=True)
        bot.reply_to(message, f"<b>ᴀᴅᴅᴇᴅ: ᴜsᴇʀ {cmd[1]} ʙᴀɴɴᴇᴅ.</b>")
    elif '/unban' in message.text and len(cmd) > 1:
        banned_col.delete_one({"user_id": int(cmd[1])})
        bot.reply_to(message, f"<b>ᴀᴅᴅᴇᴅ: ᴜsᴇʀ {cmd[1]} ᴜɴʙᴀɴɴᴇᴅ.</b>")

if __name__ == "__main__":
    keep_alive()
    print("Bot is starting with Auto-Delete System...")
    # Error fix: Remove webhook and old polling conflict
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
