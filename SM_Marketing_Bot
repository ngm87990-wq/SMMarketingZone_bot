import telebot
import sqlite3
from telebot import types

# --- আপনার তথ্য এখানে দিন ---
API_TOKEN = '8580190323:AAHA3I-zTucbz77NIHKVSr8vklCNY_Ut0u4'
ADMIN_ID = 7225553210 
# আপনার চ্যানেলের ইউজারনেম এখানে দিন (@ সহ)
CHANNEL_USERNAME = "@SMMarketingZone" 
# -------------------------

bot = telebot.TeleBot(API_TOKEN)
bot.remove_webhook()

# ১. ইউজার চ্যানেলে আছে কি না চেক করার ফাংশন
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        if status in ['member', 'administrator', 'creator']:
            return True
        else:
            return False
    except Exception:
        # যদি ইউজার বটের সাথে আগে চ্যাট না করে থাকে বা এরর হয়
        return False

# ডাটাবেস সেটআপ
def init_db():
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (user_id INTEGER PRIMARY KEY, balance REAL DEFAULT 0)''')
    conn.commit()
    conn.close()

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

# মেইন মেনু বাটন
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('Submit Facebook ID 📝', 'ID Submission Deadliness 🕒',
               'Balance 💸', 'Withdraw balance 💰',
               '🍂 Work App 🍁', '🆘 Helps 🆘')
    return markup

# জয়েন করার বাটন (Inline Keyboard)
def join_menu():
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("📢 Join Our Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")
    refresh_btn = types.InlineKeyboardButton("✅ Joined (Check)", callback_data="check_join")
    markup.add(btn)
    markup.add(refresh_btn)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    init_db()
    update_balance(user_id, 0)
    
    # সাবস্ক্রিপশন চেক
    if is_subscribed(user_id):
        bot.send_message(user_id, "🔝 **Main Menu** তে আপনাকে স্বাগতম!",
                         reply_markup=main_menu(), parse_mode="Markdown")
    else:
        bot.send_message(user_id, "⚠️ এই বটটি ব্যবহার করতে হলে আপনাকে আমাদের চ্যানেলে জয়েন থাকতে হবে।",
                         reply_markup=join_menu())

# রিফ্রেশ বাটন ক্লিক হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def callback_check_join(call):
    if is_subscribed(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "✅ ধন্যবাদ! আপনি এখন বটটি ব্যবহার করতে পারেন।", 
                         reply_markup=main_menu())
    else:
        bot.answer_callback_query(call.id, "❌ আপনি এখনো চ্যানেলে জয়েন হননি!", show_alert=True)

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(ADMIN_ID, "🛠 **অ্যাডমিন প্যানেল:**\n\n`/add [ID] [Amount]` - ব্যালেন্স যোগ\n`/minus [ID] [Amount]` - ব্যালেন্স কাটা", parse_mode="Markdown")

@bot.message_handler(commands=['add'])
def add_money(message):
    if message.chat.id == ADMIN_ID:
        try:
            args = message.text.split()
            target_id = int(args[1])
            amount = float(args[2])
            update_balance(target_id, amount)
            bot.send_message(ADMIN_ID, f"✅ সফল! আইডি {target_id} এ {amount} টাকা যোগ হয়েছে।")
            bot.send_message(target_id, f"🎊 অভিনন্দন! আপনার ব্যালেন্সে {amount} টাকা যোগ করা হয়েছে।")
        except:
            bot.reply_to(message, "⚠️ ভুল ফরম্যাট! `/add 123456 50`")

@bot.message_handler(commands=['minus'])
def deduct_money(message):
    if message.chat.id == ADMIN_ID:
        try:
            args = message.text.split()
            target_id = int(args[1])
            amount = float(args[2])
            update_balance(target_id, -amount)
            bot.send_message(ADMIN_ID, f"✅ সফল! আইডি {target_id} থেকে {amount} টাকা কাটা হয়েছে।")
        except:
            bot.reply_to(message, "⚠️ ভুল ফরম্যাট! `/minus 123456 50`")

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    if not is_subscribed(message.chat.id):
        bot.send_message(message.chat.id, "⚠️ জয়েন করুন:", reply_markup=join_menu())
        return
    bot.send_message(message.chat.id, "✅ আপনার ফাইলটি জমা হয়েছে!")
    bot.send_document(ADMIN_ID, message.document.file_id, 
                     caption=f"📩 **New File**\nID: `{message.chat.id}`", parse_mode="Markdown")

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
    elif text == 'Submit Facebook ID 📝':
        msg = bot.send_message(uid, "📧 তথ্য লিখুন বা Excel ফাইল পাঠান:")
        bot.register_next_step_handler(msg, process_fb)
    elif text == 'Withdraw balance 💰':
        bal = get_balance(uid)
        if bal < 100:
            bot.send_message(uid, "❌ সর্বনিম্ন ১০০ টাকা লাগবে।")
        else:
            msg = bot.send_message(uid, "💸 নম্বর ও পরিমাণ লিখুন (উদা: 017xx 100):")
            bot.register_next_step_handler(msg, process_wd)
    # বাকি বাটনগুলো আগের মতোই থাকবে...

def process_fb(message):
    if message.content_type == 'text':
        bot.send_message(ADMIN_ID, f"📩 **New Text**\nID: `{message.chat.id}`\n{message.text}", parse_mode="Markdown")
        bot.send_message(message.chat.id, "✅ জমা হয়েছে!")
    elif message.content_type == 'document':
        handle_docs(message)

def process_wd(message):
    uid = message.chat.id
    try:
        amount = float(message.text.split()[-1])
        if amount > get_balance(uid):
            bot.send_message(uid, "❌ পর্যাপ্ত ব্যালেন্স নেই।")
        else:
            update_balance(uid, -amount)
            bot.send_message(ADMIN_ID, f"💸 **Withdraw**\nID: `{uid}`\nDetails: {message.text}")
            bot.send_message(uid, f"✅ {amount} টাকা কাটা হয়েছে।")
    except:
        bot.send_message(uid, "❌ ভুল ফরম্যাট।")

if __name__ == "__main__":
    init_db()
    print("বট চলছে...")
    bot.infinity_polling()
