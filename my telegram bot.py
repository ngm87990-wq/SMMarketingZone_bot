import telebot
import sqlite3
from telebot import types

# --- আপনার তথ্য এখানে দিন ---
API_TOKEN = '8566392445:AAEHOtiZPOljA4bvnxqWVQ0xQXBqqfRmG-g'
ADMIN_ID = 7569158704
CHANNEL_USERNAME = "@SMMarketingZone" 
# -------------------------

bot = telebot.TeleBot(API_TOKEN)
bot.remove_webhook()

# ১. ডাটাবেস ফাংশনসমূহ
def init_db():
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    # ইউজার টেবিল
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (user_id INTEGER PRIMARY KEY, balance REAL DEFAULT 0)''')
    # সেটিংস টেবিল (ডেডলাইন এবং অ্যাপ লিঙ্ক সেভ করার জন্য)
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings
                      (key TEXT PRIMARY KEY, value TEXT)''')
    conn.commit()
    conn.close()

# সেটিংস আপডেট করার ফাংশন
def update_setting(key, value):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

# সেটিংস পড়ার ফাংশন
def get_setting(key, default_value):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else default_value

def get_balance(user_id):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def update_balance(user_id, amount):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)", (user_id,))
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()

# ২. সাবস্ক্রিপশন চেক
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

# ৩. কিবোর্ড মেনু
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

# ৪. কমান্ড হ্যান্ডলার
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    init_db()
    update_balance(user_id, 0)
    
    if is_subscribed(user_id):
        bot.send_message(user_id, "🔝 **Main Menu** তে আপনাকে স্বাগতম!",
                         reply_markup=main_menu(), parse_mode="Markdown")
    else:
        bot.send_message(user_id, "⚠️ এই বটটি ব্যবহার করতে হলে আপনাকে আমাদের চ্যানেলে জয়েন থাকতে হবে।",
                         reply_markup=join_menu())

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id == ADMIN_ID:
        msg = ("🛠 **অ্যাডমিন প্যানেল:**\n\n"
               "`/add [ID] [Amount]` - ব্যালেন্স যোগ\n"
               "`/minus [ID] [Amount]` - ব্যালেন্স কাটা\n"
               "`/set_deadline [Text]` - ডেডলাইন সেট করুন\n"
               "`/reset_deadline` - ডেডলাইন মুছুন\n"
               "`/set_app [Link/Text]` - অ্যাপ লিঙ্ক সেট করুন\n"
               "`/reset_app` - অ্যাপ লিঙ্ক মুছুন")
        bot.send_message(ADMIN_ID, msg, parse_mode="Markdown")

# ৫. অ্যাডমিন অ্যাকশন (Deadline & Work App)
@bot.message_handler(commands=['set_deadline'])
def set_deadline_cmd(message):
    if message.chat.id == ADMIN_ID:
        new_text = message.text.replace('/set_deadline', '').strip()
        if not new_text:
            bot.reply_to(message, "⚠️ ব্যবহার: `/set_deadline আগামীকাল রাত ১০টা পর্যন্ত`")
            return
        update_setting('deadline', new_text)
        bot.send_message(ADMIN_ID, "✅ ডেডলাইন আপডেট করা হয়েছে!")

@bot.message_handler(commands=['reset_deadline'])
def reset_deadline_cmd(message):
    if message.chat.id == ADMIN_ID:
        update_setting('deadline', "বর্তমানে কোনো ডেডলাইন সেট করা নেই।")
        bot.send_message(ADMIN_ID, "🗑 ডেডলাইন মুছে ফেলা হয়েছে।")

@bot.message_handler(commands=['set_app'])
def set_app_cmd(message):
    if message.chat.id == ADMIN_ID:
        new_app_info = message.text.replace('/set_app', '').strip()
        if not new_app_info:
            bot.reply_to(message, "⚠️ ব্যবহার: `/set_app https://example.com` অথবা অ্যাপের নাম।")
            return
        update_setting('work_app', new_app_info)
        bot.send_message(ADMIN_ID, "✅ Work App তথ্য আপডেট করা হয়েছে!")

@bot.message_handler(commands=['reset_app'])
def reset_app_cmd(message):
    if message.chat.id == ADMIN_ID:
        update_setting('work_app', "বর্তমানে কোনো অ্যাপ লিঙ্ক দেওয়া নেই।")
        bot.send_message(ADMIN_ID, "🗑 অ্যাপ লিঙ্ক মুছে ফেলা হয়েছে।")

# ৬. ব্যালেন্স ম্যানেজমেন্ট
@bot.message_handler(commands=['add'])
def add_money(message):
    if message.chat.id == ADMIN_ID:
        try:
            args = message.text.split()
            target_id, amount = int(args[1]), float(args[2])
            update_balance(target_id, amount)
            bot.send_message(ADMIN_ID, f"✅ আইডি {target_id} এ {amount} টাকা যোগ হয়েছে।")
            bot.send_message(target_id, f"🎊 আপনার ব্যালেন্সে {amount} টাকা যোগ হয়েছে।")
        except:
            bot.reply_to(message, "⚠️ ভুল ফরম্যাট! `/add 123456 50`")

@bot.message_handler(commands=['minus'])
def minus_money(message):
    if message.chat.id == ADMIN_ID:
        try:
            args = message.text.split()
            target_id, amount = int(args[1]), float(args[2])
            update_balance(target_id, -amount)
            bot.send_message(ADMIN_ID, f"✅ আইডি {target_id} থেকে {amount} টাকা কাটা হয়েছে।")
        except:
            bot.reply_to(message, "⚠️ ভুল ফরম্যাট! `/minus 123456 50`")

# ৭. ইউজার বাটন হ্যান্ডলার
@bot.message_handler(func=lambda message: True)
def handle_all(message):
    uid = message.chat.id
    if not is_subscribed(uid):
        bot.send_message(uid, "⚠️ আগে চ্যানেলে জয়েন করুন:", reply_markup=join_menu())
        return

    text = message.text
    if text == 'Balance 💸':
        bal = get_balance(uid)
        bot.send_message(uid, f"💰 আপনার বর্তমান ব্যালেন্স: **{bal}** টাকা।", parse_mode="Markdown")
        
    elif text == 'ID Submission Deadliness 🕒':
        deadline = get_setting('deadline', "বর্তমানে কোনো ডেডলাইন সেট করা নেই।")
        bot.send_message(uid, f"🕒 **আইডি সাবমিশন সময়সীমা:**\n\n{deadline}", parse_mode="Markdown")

    elif text == '🍂 Work App 🍁':
        app_info = get_setting('work_app', "বর্তমানে কোনো অ্যাপ লিঙ্ক দেওয়া নেই।")
        bot.send_message(uid, f"📲 **কাজের অ্যাপ লিঙ্ক:**\n\n{app_info}", parse_mode="Markdown", disable_web_page_preview=False)

    elif text == 'Submit Facebook ID 📝':
        msg = bot.send_message(uid, "📧 তথ্য লিখুন বা Excel ফাইল পাঠান:")
        bot.register_next_step_handler(msg, process_fb)

    elif text == 'Withdraw balance 💰':
        bal = get_balance(uid)
        if bal < 100:
            bot.send_message(uid, "❌ সর্বনিম্ন ১০০ টাকা ব্যালেন্স থাকতে হবে।")
        else:
            msg = bot.send_message(uid, "💸 নম্বর ও পরিমাণ লিখুন (উদা: 017xx 100):")
            bot.register_next_step_handler(msg, process_wd)

    elif text == '🆘 Helps 🆘':
        bot.send_message(uid, "🆘 যেকোনো প্রয়োজনে যোগাযোগ করুন: @Your_Admin_Username")

# ৮. অন্যান্য ফাংশন
def process_fb(message):
    if message.content_type in ['text', 'document']:
        bot.send_message(ADMIN_ID, f"📩 **New Submission**\nID: `{message.chat.id}`")
        if message.content_type == 'text':
            bot.send_message(ADMIN_ID, message.text)
        else:
            bot.send_document(ADMIN_ID, message.document.file_id)
        bot.send_message(message.chat.id, "✅ আপনার তথ্য জমা হয়েছে!")

def process_wd(message):
    uid = message.chat.id
    try:
        amount = float(message.text.split()[-1])
        if amount > get_balance(uid):
            bot.send_message(uid, "❌ পর্যাপ্ত ব্যালেন্স নেই।")
        else:
            update_balance(uid, -amount)
            bot.send_message(ADMIN_ID, f"💸 **Withdraw Request**\nID: `{uid}`\nDetails: {message.text}")
            bot.send_message(uid, f"✅ রিকোয়েস্ট পাঠানো হয়েছে। {amount} টাকা কাটা হয়েছে।")
    except:
        bot.send_message(uid, "❌ ভুল ফরম্যাট।")

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def callback_check_join(call):
    if is_subscribed(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "✅ ধন্যবাদ! আপনি এখন বটটি ব্যবহার করতে পারেন।", reply_markup=main_menu())
    else:
        bot.answer_callback_query(call.id, "❌ আপনি এখনো চ্যানেলে জয়েন হননি!", show_alert=True)

if __name__ == "__main__":
    init_db()
    print("বট সফলভাবে চালু হয়েছে...")
    bot.infinity_polling()
