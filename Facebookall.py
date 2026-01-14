
import telebot
import sqlite3
from telebot import types

# --- আপনার তথ্য এখানে দিন ---
API_TOKEN = '8566392445:AAHcUyiE2qBL-EeY1MVpLUulpqUqs-xQ5bk'
ADMIN_ID = 7569158704
CHANNEL_USERNAME = "@SMMarketingZone" 
SUPPORT_BOT = "@SMMarketingZone_Supportbot" # সাপোর্ট আইডির ইউজারনেম
# -------------------------

bot = telebot.TeleBot(API_TOKEN, threaded=False)

# --- ১. ডাটাবেস ফাংশনসমূহ ---
def init_db():
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (user_id INTEGER PRIMARY KEY, 
                       balance REAL DEFAULT 0, 
                       is_banned INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings
                      (key TEXT PRIMARY KEY, value TEXT)''')
    conn.commit()
    conn.close()

def execute_query(query, params=(), fetchone=False):
    conn = sqlite3.connect('bot_data.db', timeout=10)
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        if fetchone:
            return cursor.fetchone()
    except Exception as e:
        print(f"DB Error: {e}")
    finally:
        conn.close()
    return None

# --- ২. হেল্পার ফাংশনসমূহ ---
def is_user_banned(user_id):
    res = execute_query("SELECT is_banned FROM users WHERE user_id=?", (user_id,), fetchone=True)
    return res[0] == 1 if res else False

def ban_check_msg(uid):
    bot.send_message(uid, f"❌ আপনি বর্তমানে এই বট থেকে <b>ব্যান</b> আছেন।\n\nযেকোনো সমস্যায় এখানে কথা বলুন: {SUPPORT_BOT}", parse_mode="HTML")

def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return status in ['member', 'administrator', 'creator']
    except Exception:
        return False

# --- ৩. কিবোর্ড মেনু ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('Submit Facebook ID 📝', 'ID Submission Deadliness 🕒',
               'Balance 💸', 'Withdraw balance 💰',
               '🍂 Work App 🍁', '🆘 Helps 🆘')
    return markup

def join_menu():
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("📢 Join Our Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")
    refresh_btn = types.InlineKeyboardButton("✅ Joined (Check)", callback_data="check_join")
    markup.add(btn)
    markup.add(refresh_btn)
    return markup

# --- ৪. কমান্ড হ্যান্ডলার ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    uid = message.chat.id
    init_db()
    execute_query("INSERT OR IGNORE INTO users (user_id, balance, is_banned) VALUES (?, 0, 0)", (uid,))
    
    if is_user_banned(uid):
        ban_check_msg(uid)
        return

    if is_subscribed(uid):
        bot.send_message(uid, "🔝 <b>Main Menu</b> তে আপনাকে স্বাগতম!", reply_markup=main_menu(), parse_mode="HTML")
    else:
        bot.send_message(uid, "⚠️ এই বটটি ব্যবহার করতে হলে আপনাকে আমাদের চ্যানেলে জয়েন থাকতে হবে।", reply_markup=join_menu())

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id == ADMIN_ID:
        msg = ("🛠 <b>অ্যাডমিন প্যানেল কমান্ডসমূহ:</b>\n\n"
               "➕ <code>/add ID Amount</code> - ব্যালেন্স যোগ\n"
               "➖ <code>/minus ID Amount</code> - ব্যালেন্স কাটা\n"
               "🚫 <code>/ban ID</code> - ইউজার ব্যান\n"
               "✅ <code>/unban ID</code> - ইউজার আনব্যান\n\n"
               "🕒 <b>Settings:</b>\n"
               "📝 <code>/set_deadline Text</code> - ডেডলাইন সেট\n"
               "🗑 <code>/del_deadline</code> - ডেডলাইন মুছুন\n\n"
               "📲 <code>/set_app Link</code> - অ্যাপ লিঙ্ক সেট\n"
               "🗑 <code>/del_app</code> - অ্যাপ লিঙ্ক মুছুন")
        bot.send_message(ADMIN_ID, msg, parse_mode="HTML")

# --- ৫. অ্যাডমিন অ্যাকশন হ্যান্ডলার ---
@bot.message_handler(commands=['add', 'minus', 'ban', 'unban', 'set_deadline', 'del_deadline', 'set_app', 'del_app'])
def handle_admin_commands(message):
    if message.chat.id != ADMIN_ID: return
    cmd_parts = message.text.split(maxsplit=2)
    cmd = cmd_parts[0]
    
    try:
        if cmd == '/add' or cmd == '/minus':
            uid, amount = int(cmd_parts[1]), float(cmd_parts[2])
            if cmd == '/add':
                execute_query("UPDATE users SET balance = round(balance + ?, 2) WHERE user_id = ?", (amount, uid))
                bot.send_message(ADMIN_ID, f"✅ আইডি {uid} এ {amount} টাকা যোগ হয়েছে।")
            else:
                execute_query("UPDATE users SET balance = round(balance - ?, 2) WHERE user_id = ?", (amount, uid))
                bot.send_message(ADMIN_ID, f"✅ আইডি {uid} থেকে {amount} টাকা কাটা হয়েছে।")
        
        elif cmd == '/ban':
            uid = int(cmd_parts[1])
            execute_query("UPDATE users SET is_banned = 1 WHERE user_id = ?", (uid,))
            bot.send_message(ADMIN_ID, f"🚫 ইউজার {uid} কে ব্যান করা হয়েছে।")
            bot.send_message(uid, f"❌ আপনাকে এই বট থেকে ব্যান করা হয়েছে। যোগাযোগ: {SUPPORT_BOT}")

        elif cmd == '/unban':
            uid = int(cmd_parts[1])
            execute_query("UPDATE users SET is_banned = 0 WHERE user_id = ?", (uid,))
            bot.send_message(ADMIN_ID, f"✅ ইউজার {uid} কে আনব্যান করা হয়েছে।")
            bot.send_message(uid, "🎉 অভিনন্দন! আপনাকে আনব্যান করা হয়েছে। এখন আপনি বটটি ব্যবহার করতে পারবেন।")

        elif cmd == '/set_deadline':
            text = cmd_parts[1] + " " + (cmd_parts[2] if len(cmd_parts)>2 else "")
            execute_query("INSERT OR REPLACE INTO settings (key, value) VALUES ('deadline', ?)", (text,))
            bot.send_message(ADMIN_ID, "✅ ডেডলাইন আপডেট হয়েছে।")
            
        elif cmd == '/del_deadline':
            execute_query("DELETE FROM settings WHERE key='deadline'")
            bot.send_message(ADMIN_ID, "🗑 ডেডলাইন মুছে ফেলা হয়েছে।")

        elif cmd == '/set_app':
            link = cmd_parts[1]
            execute_query("INSERT OR REPLACE INTO settings (key, value) VALUES ('work_app', ?)", (link,))
            bot.send_message(ADMIN_ID, "✅ অ্যাপ লিঙ্ক আপডেট হয়েছে।")

        elif cmd == '/del_app':
            execute_query("DELETE FROM settings WHERE key='work_app'")
            bot.send_message(ADMIN_ID, "🗑 অ্যাপ লিঙ্ক মুছে ফেলা হয়েছে।")

    except Exception as e:
        bot.reply_to(message, "❌ ভুল কমান্ড ফরম্যাট বা আইডি খুঁজে পাওয়া যায়নি!")

# --- ৬. সাবমিশন সিস্টেম ---
pending_submissions = {}

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    uid = message.chat.id
    
    # ব্যান চেক (প্রথমেই)
    if is_user_banned(uid):
        ban_check_msg(uid)
        return

    if not is_subscribed(uid):
        bot.send_message(uid, "⚠️ আগে জয়েন করুন!", reply_markup=join_menu())
        return

    text = message.text
    if text == 'Balance 💸':
        res = execute_query("SELECT balance FROM users WHERE user_id=?", (uid,), fetchone=True)
        bal = res[0] if res else 0.0
        bot.send_message(uid, f"💰 আপনার বর্তমান ব্যালেন্স: <b>{bal}</b> টাকা।", parse_mode="HTML")
        
    elif text == 'Submit Facebook ID 📝':
        msg = bot.send_message(uid, "📧 আপনার ফাইলটি (xlsx) পাঠান অথবা টেক্সট আকারে ডেটা লিখুন :")
        bot.register_next_step_handler(msg, ask_confirmation)
        
    elif text == 'ID Submission Deadliness 🕒':
        res = execute_query("SELECT value FROM settings WHERE key='deadline'", fetchone=True)
        deadline = res[0] if res else "বর্তমানে কোনো ডেডলাইন নেই।"
        bot.send_message(uid, f"🕒 <b>সময়সীমা:</b>\n\n{deadline}", parse_mode="HTML")

    elif text == 'Withdraw balance 💰':
        res = execute_query("SELECT balance FROM users WHERE user_id=?", (uid,), fetchone=True)
        bal = res[0] if res else 0
        if bal < 100:
            bot.send_message(uid,"❌ দুঃখিত! আপনার ব্যালেন্স ১০০ টাকার কম।")  
        else:
            msg = bot.send_message(uid, "💸 নম্বর ও পরিমাণ লিখুন (উদা: 017xx 100 টাকা):")
            bot.register_next_step_handler(msg, process_withdraw_request)
    
    elif text == '🍂 Work App 🍁':
        res = execute_query("SELECT value FROM settings WHERE key='work_app'", fetchone=True)
        app = res[0] if res else "বর্তমানে কোনো অ্যাপ লিঙ্ক নেই।"
        bot.send_message(uid, f"📲 <b>অ্যাপ লিঙ্ক:</b>\n\n{app}", parse_mode="HTML")

    elif text == '🆘 Helps 🆘':
        bot.send_message(uid, f"🆘 যোগাযোগ: {SUPPORT_BOT}")

# --- ৭. কনফার্মেশন ও প্রসেস ---
def ask_confirmation(message):
    uid = message.chat.id
    if is_user_banned(uid):
        ban_check_msg(uid)
        return
        
    pending_submissions[uid] = message
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Confirm", callback_data="sub_confirm"),
               types.InlineKeyboardButton("❌ Cancel", callback_data="sub_cancel"))
    bot.send_message(uid, "❓ আপনি কি এই তথ্যটি সাবমিট করতে নিশ্চিত?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["sub_confirm", "sub_cancel"])
def handle_submission_callback(call):
    uid = call.from_user.id
    if is_user_banned(uid):
        bot.answer_callback_query(call.id, "❌ আপনি ব্যান আছেন!", show_alert=True)
        ban_check_msg(uid)
        return

    if call.data == "sub_confirm":
        if uid in pending_submissions:
            data_msg = pending_submissions[uid]
            user_name = f"@{call.from_user.username}" if call.from_user.username else "No Username"
            
            if data_msg.content_type == 'text':
                caption = (f"📩 <b>New Text Submission</b>\n\n👤 User: {user_name}\n🆔 ID: <code>{uid}</code>\n\n📝 Data: {data_msg.text}")
                bot.send_message(ADMIN_ID, caption, parse_mode="HTML")
            elif data_msg.content_type == 'document':
                caption = (f"📩 <b>New File Submission</b>\n\n👤 User: {user_name}\n🆔 ID: <code>{uid}</code>")
                bot.send_document(ADMIN_ID, data_msg.document.file_id, caption=caption, parse_mode="HTML")
            
            bot.edit_message_text("✅ আপনার তথ্য সফলভাবে এডমিনের কাছে পাঠানো হয়েছে!", uid, call.message.message_id)
            del pending_submissions[uid]
        else:
            bot.answer_callback_query(call.id, "❌ কোনো তথ্য পাওয়া যায়নি।")
            
    elif call.data == "sub_cancel":
        if uid in pending_submissions:
            del pending_submissions[uid]
        bot.edit_message_text("❌ আপনার সাবমিশনটি বাতিল করা হয়েছে।", uid, call.message.message_id)

def process_withdraw_request(message):
    uid = message.chat.id
    if is_user_banned(uid):
        ban_check_msg(uid)
        return

    user_name = f"@{message.from_user.username}" if message.from_user.username else "No Username"
    try:
        amount = float(message.text.split()[-1])
        res = execute_query("SELECT balance FROM users WHERE user_id=?", (uid,), fetchone=True)
        if amount > (res[0] if res else 0):
            bot.send_message(uid, "❌ পর্যাপ্ত ব্যালেন্স নেই।")
        else:
            execute_query("UPDATE users SET balance = round(balance - ?, 2) WHERE user_id=?", (amount, uid))
            msg = (f"💸 <b>Withdraw Request</b>\n\n👤 User: {user_name}\n🆔 ID: <code>{uid}</code>\n📝 Info: {message.text}")
            bot.send_message(ADMIN_ID, msg, parse_mode="HTML")
            bot.send_message(uid, "✅ উইথড্র অনুরোধ পাঠানো হয়েছে।")
    except:
        bot.send_message(uid, "❌ ভুল ফরম্যাট।")

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def callback_check_join(call):
    uid = call.from_user.id
    if is_user_banned(uid):
        bot.answer_callback_query(call.id, "❌ আপনি ব্যান আছেন!", show_alert=True)
        ban_check_msg(uid)
        return

    if is_subscribed(uid):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "✅ স্বাগতম!", reply_markup=main_menu())
    else:
        bot.answer_callback_query(call.id, "❌ আগে জয়েন করুন!", show_alert=True)

if __name__ == "__main__":
    init_db()
    print("Bot is running with Advanced Ban System...")
    bot.infinity_polling()

