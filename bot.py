import telebot
import requests
import time
import json
import os
from telebot import types
from flask import Flask
from threading import Thread

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

# --- CONFIGURATION ---
TOKEN = "8339809079:AAGyTLUuk4gjjsshw8EJi6BolkfZnuft04Y"
OWNER_ID = 6703335929
CHANNEL_ID = "@alphacodex369" 
GROUP_ID = "@CodexGroupTm"     
DB_FILE = "database.json"
USER_DATA_FILE = "user_usage.json"
API_URL = "https://check-api-sage.vercel.app/?num="

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
bot_running = True

# --- DATABASE HELPERS ---
def load_db():
    if not os.path.exists(DB_FILE): return {"users": [], "groups": [], "banned": []}
    with open(DB_FILE, "r") as f: return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

def load_usage():
    if not os.path.exists(USER_DATA_FILE): return {}
    with open(USER_DATA_FILE, "r") as f: return json.load(f)

def save_usage(data):
    with open(USER_DATA_FILE, "w") as f: json.dump(data, f, indent=4)

def is_subscribed(user_id):
    try:
        status1 = bot.get_chat_member(CHANNEL_ID, user_id).status
        status2 = bot.get_chat_member(GROUP_ID, user_id).status
        return status1 != 'left' and status2 != 'left'
    except: return False

# --- COMMANDS ---
@bot.message_handler(commands=['start'])
def start(message):
    if not bot_running and message.from_user.id != OWNER_ID: return
    db = load_db()
    if message.from_user.id not in db["users"]:
        db["users"].append(message.from_user.id)
        save_db(db)
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
        bot.edit_message_text("<b>ᴀᴅᴅᴇᴅ: ᴠᴇʀɪғɪᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!</b>\nʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴜsᴇ /ɴᴜᴍ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ.", call.message.chat.id, call.message.message_id, reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, "❌ ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ғɪʀsᴛ!", show_alert=True)

@bot.message_handler(content_types=['new_chat_members'])
def group_check(message):
    db = load_db()
    if message.chat.id not in db["groups"]:
        db["groups"].append(message.chat.id)
        save_db(db)
    if bot.get_chat_member_count(message.chat.id) < 50:
        bot.send_message(message.chat.id, "<blockquote>ᴛʜɪs ɢʀᴏᴜᴘ ʜᴀs ʟᴇss ᴛʜᴀɴ 50 ᴍᴇᴍʙᴇʀs. ʙᴏᴛ ʟᴇᴀᴠɪɴɢ...</blockquote>")
        bot.leave_chat(message.chat.id)

@bot.message_handler(commands=['num'])
def info_fetch(message):
    if not bot_running: return
    uid = message.from_user.id
    db = load_db()
    if uid in db["banned"]: return
    if not is_subscribed(uid):
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("ᴊᴏɪɴ ɢʀᴏᴜᴘ", url=f"https://t.me/{GROUP_ID.replace('@','')}")
        btn2 = types.InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{CHANNEL_ID.replace('@','')}")
        markup.add(btn1, btn2)
        return bot.reply_to(message, "<b>ᴀᴅᴅᴇᴅ: ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ғɪʀsᴛ!</b>", reply_markup=markup)
    usage = load_usage()
    now = time.time()
    u_str = str(uid)
    if u_str in usage:
        count, l_time = usage[u_str]
        if now - l_time < 3600 and count >= 10:
            return bot.reply_to(message, "<b>ᴀᴅᴅᴇᴅ: ʟɪᴍɪᴛ ᴇxᴄᴇᴇᴅᴇᴅ! ᴛʀʏ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 1 ʜᴏᴜʀ.</b>")
        if now - l_time >= 3600: usage[u_str] = [1, now]
        else: usage[u_str][0] += 1
    else: usage[u_str] = [1, now]
    save_usage(usage)
    text = message.text.split()
    if len(text) < 2: return bot.reply_to(message, "<b>ᴀᴅᴅᴇᴅ: ᴜsᴀɢᴇ:</b> <code>/num 9876543210</code>")
    num = text[1]
    try:
        res = requests.get(f"{API_URL}{num}").json()
        if not res.get("success"): return bot.reply_to(message, "<b>ᴀᴅᴅᴇᴅ: ɴᴏ ᴅᴀᴛᴀ ғᴏᴜɴᴅ!</b>")
        response = f"<b>ᴀᴅᴅᴇᴅ ɪɴғᴏ ғᴏʀ:</b> <code>{num}</code>\n"
        response += "━━━━━━━━━━━━━━━━━━\n"
        for key in sorted(res.keys()):
            if key.isdigit():
                item = res[key]
                response += f"👤 <b>ɴᴀᴍᴇ:</b> <code>{item.get('name') or 'N/A'}</code>\n"
                response += f"👴 <b>ғᴀᴛʜᴇʀ:</b> <code>{item.get('father_name') or 'N/A'}</code>\n"
                response += f"📱 <b>ᴍᴏʙɪʟᴇ:</b> <code>{item.get('mobile') or 'N/A'}</code>\n"
                response += f"📞 <b>ᴀʟᴛ:</b> <code>{item.get('alt_mobile') or 'N/A'}</code>\n"
                response += f"🆔 <b>ɪᴅ:</b> <code>{item.get('id_number') or 'N/A'}</code>\n"
                response += f"🏢 <b>ᴄɪʀᴄʟᴇ:</b> <code>{item.get('circle') or 'N/A'}</code>\n"
                response += f"📧 <b>ᴇᴍᴀɪʟ:</b> <code>{item.get('email') or 'N/A'}</code>\n"
                response += f"📍 <b>ᴀᴅᴅʀᴇss:</b> <code>{item.get('address') or 'N/A'}</code>\n"
                response += "━━━━━━━━━━━━━━━━━━\n"
        response += f"<blockquote>ɴᴏᴛᴇ: ᴄᴏᴅᴇ–ɪɴꜰᴏ\nᴅᴇᴠ: ᴅx–ᴄᴏᴅᴇx\nsᴏᴜʀᴄᴇ: @ᴛᴇʀᴍᴜxᴄᴏᴅᴇx</blockquote>"
        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, f"<b>ᴀᴅᴅᴇᴅ: ᴀᴘɪ ᴇʀʀᴏʀ!</b>")

# --- OWNER CONTROLS ---
@bot.message_handler(commands=['stop', 'run', 'ping', 'ban', 'public', 'id'], func=lambda m: m.from_user.id == OWNER_ID)
def owner_actions(message):
    global bot_running
    cmd = message.text.split()
    if '/stop' in message.text: 
        bot_running = False
        bot.reply_to(message, "<b>ᴀᴅᴅᴇᴅ: ʙᴏᴛ sᴛᴏᴘᴘᴇᴅ.</b>")
    elif '/run' in message.text: 
        bot_running = True
        bot.reply_to(message, "<b>ᴀᴅᴅᴇᴅ: ʙᴏᴛ ʀᴜɴɴɪɴɢ.</b>")
    elif '/ping' in message.text: 
        bot.reply_to(message, "<b>ᴀᴅᴅᴇᴅ: ᴘᴏɴɢ! sᴘᴇᴇᴅ: ᴇxᴄᴇʟʟᴇɴᴛ</b>")
    elif '/id' in message.text:
        bot.reply_to(message, f"<b>ᴀᴅᴅᴇᴅ: ʏᴏᴜʀ ɪᴅ:</b> <code>{message.from_user.id}</code>")
    elif '/ban' in message.text and len(cmd) > 1:
        db = load_db(); db["banned"].append(int(cmd[1])); save_db(db)
        bot.reply_to(message, f"<b>ᴀᴅᴅᴇᴅ: ᴜsᴇʀ {cmd[1]} ʙᴀɴɴᴇᴅ.</b>")
    elif '/public' in message.text and message.reply_to_message:
        db = load_db(); count = 0
        for user in db["users"]:
            try:
                bot.copy_message(user, message.chat.id, message.reply_to_message.message_id)
                count += 1
            except: pass
        bot.send_message(OWNER_ID, f"<b>ᴀᴅᴅᴇᴅ: ʙʀᴏᴀᴅᴄᴀsᴛ sᴜᴄᴄᴇssғᴜʟ ᴛᴏ {count} ᴜsᴇʀs.</b>")

if __name__ == "__main__":
    keep_alive() # Start the web server
    bot.infinity_polling()
