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

# --- KEEP ALIVE SYSTEM ---
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
        active_status = ['member', 'administrator', 'creator', 'restricted']
        return (status1 in active_status) and (status2 in active_status)
    except:
        return False

def parse_broadcast_text(text):
    pattern = r"\[([^|]+)\|([^\]]+)\]"
    buttons = re.findall(pattern, text)
    clean_text = re.sub(pattern, "", text).strip()
    markup = types.InlineKeyboardMarkup()
    for name, url in buttons:
        markup.add(types.InlineKeyboardButton(text=name.strip(), url=url.strip()))
    return clean_text, (markup if buttons else None)

def clean_number(num_str):
    # শুধু ডিজিট রাখা
    num_str = re.sub(r'\D', '', num_str)
    # +91 বা 91 দিয়ে শুরু হলে এবং ১০ ডিজিটের বেশি হলে ওয়ার্নিং
    if (num_str.startswith("91") and len(num_str) > 10):
        return "PLUS_91_FOUND"
    return num_str

# --- AUTO DELETE TIMER LOGIC ---
def countdown_timer(chat_id, message_id, original_text, mention_name):
    timer_steps = [40, 30, 20, 10, 5]
    for sec in timer_steps:
        time.sleep(10 if sec > 10 else 5)
        stylish_sec = str(sec).replace('0','𝟢').replace('1','𝟣').replace('2','𝟤').replace('3','𝟥').replace('4','𝟦').replace('5','𝟧')
        try:
            new_footer = f"\n\n👤 ᴜꜱᴇʀ: {mention_name}\n⏳ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ: {stylish_sec}𝗌"
            bot.edit_message_text(original_text + new_footer, chat_id, message_id, parse_mode="HTML")
        except: break
    time.sleep(5)
    try: bot.delete_message(chat_id, message_id)
    except: pass

# --- DATABASE SYNC ---
def register_user(message):
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    first_name = message.from_user.first_name or "User"
    is_ban = "Yes" if banned_col.find_one({"user_id": user_id}) else "No"
    
    if not users_col.find_one({"user_id": user_id}):
        users_col.insert_one({
            "user_id": user_id, 
            "username": username, 
            "name": first_name, 
            "usage_count": 0, 
            "last_use": 0,
            "is_banned": is_ban
        })
    else:
        users_col.update_one({"user_id": user_id}, {"$set": {"username": username, "name": first_name, "is_banned": is_ban}})

    if message.chat.type in ['group', 'supergroup']:
        if not groups_col.find_one({"chat_id": message.chat.id}):
            groups_col.insert_one({"chat_id": message.chat.id, "title": message.chat.title})

# --- COMMANDS ---

@bot.message_handler(commands=['start'])
def start(message):
    register_user(message)
    user_id = message.from_user.id
    
    if not is_subscribed(user_id):
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("ᴊᴏɪɴ ɢʀᴏᴜᴘ", url=f"https://t.me/{GROUP_ID.replace('@','')}")
        btn2 = types.InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{CHANNEL_ID.replace('@','')}")
        btn3 = types.InlineKeyboardButton("✅ ᴠᴇʀɪғʏ ᴍᴇ", callback_data="check_verify")
        markup.add(btn1, btn2, btn3)
        return bot.reply_to(message, "<b>⚠️ ᴀᴄᴄᴇss ᴅᴇɴɪᴇᴅ!</b>\n\nʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ɢʀᴏᴜᴘ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ.", reply_markup=markup)

    if message.chat.type == 'private':
        markup = types.InlineKeyboardMarkup()
        btn_add = types.InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f"https://t.me/{bot.get_me().username}?startgroup=true")
        markup.add(btn_add)
        bot.reply_to(message, f"<b>👋 ʜᴇʟʟᴏ {message.from_user.first_name}!</b>\n\nɪ ᴀᴍ ᴀʟɪᴠᴇ ᴀɴᴅ ʀᴇᴀᴅʏ. ᴘʟᴇᴀsᴇ ᴀᴅᴅ ᴍᴇ ᴛᴏ ᴀ ɢʀᴏᴜᴘ ᴛᴏ ᴜsᴇ ɴᴜᴍʙᴇʀ ɪɴғᴏ sᴇᴀʀᴄʜ.", reply_markup=markup)
    else:
        bot.reply_to(message, "<b>✅ ʙᴏᴛ ɪs ᴀᴄᴛɪᴠᴇ!</b>\n\nᴘʟᴇᴀsᴇ ᴜsᴇ: <code>/num 9876543210</code> ᴛᴏ ɢᴇᴛ ᴅᴇᴛᴀɪʟs.")

@bot.callback_query_handler(func=lambda call: call.data == "check_verify")
def verify(call):
    if is_subscribed(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Verified Successfully!", show_alert=False)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "<b>✅ ᴠᴇʀɪғɪᴇᴅ!</b> ᴜsᴇ: <code>/num ɴᴜᴍʙᴇʀ</code>")
    else:
        bot.answer_callback_query(call.id, "❌ ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟs ғɪʀsᴛ!", show_alert=True)

@bot.message_handler(commands=['num'])
def info_fetch(message):
    register_user(message)
    if not bot_running: return
    uid = message.from_user.id
    
    # গ্রুপ মেম্বার চেক (<৫০ হলে লিভ)
    if message.chat.type in ['group', 'supergroup']:
        try:
            m_count = bot.get_chat_member_count(message.chat.id)
            if m_count < 50:
                bot.reply_to(message, "<b>⚠️ ᴛʜɪs ɢʀᴏᴜᴘ ʜᴀs ʟᴇss ᴛʜᴀɴ 𝟻𝟶 ᴍᴇᴍʙᴇʀs. ʙᴏᴛ ɪs ʟᴇᴀᴠɪɴɢ!</b>")
                bot.leave_chat(message.chat.id)
                return
        except: pass
    
    if not is_subscribed(uid):
        return bot.reply_to(message, "<b>❌ ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ & ɢʀᴏᴜᴘ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ!</b>")

    if message.chat.type == 'private':
        return bot.reply_to(message, "<b>❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!</b>")

    text = message.text.split()
    if len(text) < 2: 
        return bot.reply_to(message, "<b>⚠️ ᴜsᴀɢᴇ:</b> <code>/num 9876543210</code>")

    raw_num = "".join(text[1:])
    cleaned_num = clean_number(raw_num)

    if cleaned_num == "PLUS_91_FOUND":
        return bot.reply_to(message, "<b>⚠️ ᴇʀʀᴏʀ: ᴅᴏ ɴᴏᴛ ᴜsᴇ +𝟿𝟷 ᴏʀ 𝟿𝟷.</b>\nᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴏɴʟʏ 𝟷𝟶 ᴅɪɢɪᴛ ɴᴜᴍʙᴇʀ.")

    if len(cleaned_num) != 10:
        return bot.reply_to(message, "<b>⚠️ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!</b>\nᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ 𝟷𝟶 ᴅɪɢɪᴛ ᴍᴏʙɪʟᴇ ɴᴜᴍʙᴇʀ.")

    user_data = users_col.find_one({"user_id": uid})
    now = time.time()
    if now - user_data.get('last_use', 0) < 3600 and user_data.get('usage_count', 0) >= 10:
        return bot.reply_to(message, "<b>🚫 ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ! ᴛʀʏ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 𝟷 ʜᴏᴜʀ.</b>")

    try:
        sent_wait = bot.reply_to(message, "<b>🔍 sᴇᴀʀᴄʜɪɴɢ ᴅᴀᴛᴀʙᴀsᴇ... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.</b>")
        
        # API Request with better parsing logic
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(f"{API_URL}{cleaned_num}", headers=headers, timeout=15)
        res = response.json()
        
        bot.delete_message(message.chat.id, sent_wait.message_id)

        # ডাটা চেক করার জন্য আরও সঠিক লজিক (data.result অথবা সরাসরি result)
        results = []
        if res.get('data') and res['data'].get('result'):
            results = res['data']['result']
        elif res.get('result'):
            results = res['result']

        if not results:
            return bot.reply_to(message, f"<b>😔 sᴏʀʀʏ! ɴᴏ ᴅᴀᴛᴀ ғᴏᴜɴᴅ ғᴏʀ</b> <code>{cleaned_num}</code>\nᴏᴜʀ ᴅᴀᴛᴀʙᴀsᴇ ᴅᴏᴇsɴ'ᴛ ʜᴀᴠᴇ ɪɴғᴏ ᴏɴ ᴛʜɪs ɴᴜᴍʙᴇʀ.")

        mention_name = f"<a href='tg://user?id={uid}'>{message.from_user.first_name}</a>"
        is_ban = "Yes" if banned_col.find_one({"user_id": uid}) else "No"
        
        # ইউজার ডিটেইলস হেডার
        user_info = (
            f"👤 <b>ᴜsᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 ɴᴀᴍᴇ: <code>{message.from_user.first_name}</code>\n"
            f"📧 ᴜsᴇʀɴᴀᴍᴇ: @{message.from_user.username or 'N/A'}\n"
            f"🆔 ɪᴅ: <code>{uid}</code>\n"
            f"🌐 ɢʀᴏᴜᴘ ɪᴅ: <code>{message.chat.id}</code>\n"
            f"🚫 ʙᴀɴ sᴛᴀᴛᴜs: <code>{is_ban}</code>\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
        )

        full_response = user_info + f"<b>📱 ᴅᴇᴛᴀɪʟs ғᴏʀ:</b> <code>{cleaned_num}</code>\n"
        
        # ডাটা ফিল্ডস (সবগুলো অ্যাড করা হয়েছে)
        for idx, item in enumerate(results, 1):
            full_response += f"\n<b>ʀᴇᴄᴏʀᴅ {idx}</b>\n━━━━━━━━━━━━━━━━━━\n"
            full_response += f"👤 <b>ɴᴀᴍᴇ:</b> <code>{item.get('name') or 'N/A'}</code>\n"
            full_response += f"👴 <b>ғᴀᴛʜᴇʀ:</b> <code>{item.get('father_name') or 'N/A'}</code>\n"
            full_response += f"📱 <b>ᴍᴏʙɪʟᴇ:</b> <code>{item.get('mobile') or 'N/A'}</code>\n"
            full_response += f"📞 <b>ᴀʟᴛ ᴍᴏʙɪʟᴇ:</b> <code>{item.get('alt_mobile') or 'N/A'}</code>\n"
            full_response += f"🆔 <b>ɪᴅ ɴᴜᴍʙᴇʀ:</b> <code>{item.get('id_number') or 'N/A'}</code>\n"
            full_response += f"🏢 <b>ᴄɪʀᴄʟᴇ:</b> <code>{item.get('circle') or 'N/A'}</code>\n"
            full_response += f"📧 <b>ᴇᴍᴀɪʟ:</b> <code>{item.get('email') or 'N/A'}</code>\n"
            full_response += f"📍 <b>ᴀᴅᴅʀᴇss:</b> <code>{item.get('address') or 'N/A'}</code>\n"
            full_response += "━━━━━━━━━━━━━━━━━━\n"
        
        full_response += f"<blockquote>ᴅᴇᴠ: ᴅx–ᴄᴏᴅᴇx | @termuxcodex</blockquote>"
        footer = f"\n\n👤 ᴜꜱᴇʀ: {mention_name}\n⏳ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ: 𝟦𝟢ꜱ"
        
        # রিপ্লাই ট্যাগ দিয়ে মেসেজ সেন্ড
        sent_msg = bot.reply_to(message, full_response + footer)
        
        # ডাটাবেস আপডেট
        users_col.update_one({"user_id": uid}, {"$set": {"usage_count": (user_data.get('usage_count', 0) + 1 if now - user_data.get('last_use', 0) < 3600 else 1), "last_use": now}})
        
        # টাইমার স্টার্ট
        threading.Thread(target=countdown_timer, args=(message.chat.id, sent_msg.message_id, full_response, mention_name)).start()

    except Exception as e:
        bot.reply_to(message, f"<b>❌ sʏsᴛᴇᴍ ᴇʀʀᴏʀ:</b> <code>{str(e)}</code>")

# --- BROADCAST SYSTEM ---
@bot.message_handler(commands=['broadcast'], func=lambda m: m.from_user.id in OWNER_IDS)
def broadcast_manager(message):
    msg = message.reply_to_message if message.reply_to_message else message
    msg_parts = message.text.split(maxsplit=1)
    
    raw_text = ""
    if len(msg_parts) > 1: raw_text = msg_parts[1]
    elif msg.caption: raw_text = msg.caption
    elif msg.text and not msg.text.startswith('/broadcast'): raw_text = msg.text

    clean_msg, markup = parse_broadcast_text(raw_text)
    
    targets = list(set([u['user_id'] for u in users_col.find()] + [g['chat_id'] for g in groups_col.find()]))
    success = 0
    prog = bot.reply_to(message, "<b>🚀 ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ɪɴ ᴘʀᴏɢʀᴇss...</b>")

    for tid in targets:
        try:
            if msg.photo: bot.send_photo(tid, msg.photo[-1].file_id, caption=clean_msg, reply_markup=markup)
            elif msg.document: bot.send_document(tid, msg.document.file_id, caption=clean_msg, reply_markup=markup)
            elif msg.video: bot.send_video(tid, msg.video.file_id, caption=clean_msg, reply_markup=markup)
            else: bot.send_message(tid, clean_msg, reply_markup=markup)
            success += 1
            time.sleep(0.1)
        except: pass
    
    bot.edit_message_text(f"<b>✅ ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!</b>\n\n🎯 sᴜᴄᴄᴇss: {success}", message.chat.id, prog.message_id)

# --- OWNER ACTIONS ---
@bot.message_handler(commands=['id', 'stop', 'run', 'ping', 'ban', 'unban'], func=lambda m: m.from_user.id in OWNER_IDS)
def owner_actions(message):
    global bot_running
    cmd = message.text.split()
    if '/id' in message.text:
        content = "ID | Username | Name\n" + "\n".join([f"{u['user_id']} | @{u.get('username','N/A')} | {u.get('name','N/A')}" for u in users_col.find()])
        with open("users.txt", "w") as f: f.write(content)
        with open("users.txt", "rb") as f: bot.send_document(message.chat.id, f)
        os.remove("users.txt")
    elif '/stop' in message.text: bot_running = False; bot.reply_to(message, "<b>🔴 ʙᴏᴛ sᴛᴏᴘᴘᴇᴅ.</b>")
    elif '/run' in message.text: bot_running = True; bot.reply_to(message, "<b>🟢 ʙᴏᴛ ʀᴜɴɴɪɴɢ.</b>")
    elif '/ping' in message.text: bot.reply_to(message, "<b>🏓 ᴘᴏɴɢ!</b>")
    elif '/ban' in message.text and len(cmd) > 1:
        banned_col.update_one({"user_id": int(cmd[1])}, {"$set": {"user_id": int(cmd[1])}}, upsert=True)
        bot.reply_to(message, f"<b>🚫 ʙᴀɴɴᴇᴅ:</b> <code>{cmd[1]}</code>")
    elif '/unban' in message.text and len(cmd) > 1:
        banned_col.delete_one({"user_id": int(cmd[1])})
        bot.reply_to(message, f"<b>✅ ᴜɴʙᴀɴɴᴇᴅ:</b> <code>{cmd[1]}</code>")

if __name__ == "__main__":
    keep_alive()
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
