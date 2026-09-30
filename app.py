import os
import telebot
from telebot import types
from flask import Flask, request

TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID', '0'))
BINANCE_ID = os.environ.get('BINANCE_ID', 'YOUR_BINANCE_ID')
ADMIN_BKASH = os.environ.get('ADMIN_BKASH', '01XXXXXXXXX')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'SAIM_9X')
DOLAR_RATE = float(os.environ.get('DOLAR_RATE', '119'))

bot = telebot.TeleBot(TOKEN, threaded=False)
server = Flask(__name__)

user_state = {}
bot_status = {"is_active": True}

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_sell = types.KeyboardButton("💵 SELL DOLLER")
    btn_support = types.KeyboardButton("📞 SUPPORT")
    btn_admin = types.KeyboardButton("👑 ADMIN PANEL")
    markup.add(btn_sell, btn_support, btn_admin)
    return markup

@server.route(f'/{TOKEN}', methods=['POST'])
def webhook_handler():
    if request.headers.get('content-type') == 'application/json':
        json_data = request.get_json(force=True)
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])
        return '', 200
    return 'Invalid Request', 403

@server.route("/")
def index():
    return "Bot is running perfectly!", 200

# Webhook Auto-Setter on Startup
def set_webhook_url():
    bot.remove_webhook()
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        bot.set_webhook(url=f"{render_url}/{TOKEN}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not bot_status["is_active"] and message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⚠️ দুঃখিত, বর্তমানে বট বন্ধ রয়েছে।")
        return
    
    user_state.pop(message.from_user.id, None)
    welcome_text = (
        f"🌟 **স্বাগতম! আমাদের প্রিমিয়াম ডলার সেল জোনে আপনাকে স্বাগতম।** 🌟\n\n"
        f"বর্তমান ডলার রেট: **৳{DOLAR_RATE}**\n"
        f"নিচের বাটন থেকে অপশন সিলেক্ট করুন:"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text

    if not bot_status["is_active"] and user_id != ADMIN_ID:
        bot.reply_to(message, "⚠️ বটটি বর্তমানে অফলাইন রয়েছে।")
        return

    if text == "💵 SELL DOLLER":
        user_state[user_id] = {"step": "waiting_amount"}
        msg = (
            f"🎉 **অভিনন্দন! আপনি নিরাপদভাবে ডলার সেল করতে পারবেন।**\n\n"
            f"💱 বর্তমান রেট: **৳{DOLAR_RATE} / USD**\n\n"
            f"✏️ কত ডলার সেল করতে চান? সংখ্যাটি নিচে লিখে পাঠান:"
        )
        bot.send_message(user_id, msg, parse_mode="Markdown")

    elif text == "📞 SUPPORT":
        support_msg = (
            f"🛠 **কাস্টমার সাপোর্ট সেন্টার**\n\n"
            f"এডমিনের সাথে যোগাযোগ করতে:\n"
            f"👤 ইউজারনেম: @{ADMIN_USERNAME}"
        )
        bot.send_message(user_id, support_msg, parse_mode="Markdown")

    elif text == "👑 ADMIN PANEL":
        if user_id != ADMIN_ID:
            bot.send_message(user_id, "❌ আপনার এই প্যানেল ব্যবহারের অনুমতি নেই!")
            return
        
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
            types.InlineKeyboardButton("💱 Change Rate", callback_data="admin_rate"),
            types.InlineKeyboardButton("🔄 Bot On/Off", callback_data="admin_toggle")
        )
        bot.send_message(user_id, "👑 **এডমিন কন্ট্রোল প্যানেল**", parse_mode="Markdown", reply_markup=admin_markup)

    elif user_state.get(user_id, {}).get("step") == "waiting_broadcast":
        if user_id == ADMIN_ID:
            user_state.pop(user_id, None)
            bot.send_message(user_id, f"✅ ব্রডকাস্ট সফল হয়েছে!\n\nমেসেজ:\n{text}")

    elif user_state.get(user_id, {}).get("step") == "waiting_amount":
        try:
            amount = float(text)
            total_taka = amount * DOLAR_RATE
            user_state[user_id]["amount"] = amount
            user_state[user_id]["total_taka"] = total_taka
            user_state[user_id]["step"] = "waiting_order_id"

            binance_msg = (
                f"✅ আপনি **{amount} USD** সেল করতে চান।\n"
                f"💰 মোট পাবেন: **৳{total_taka}**\n\n"
                f"👇 নিচের Binance Pay ID তে ডলার সেন্ড করুন:\n\n"
                f"🆔 Binance ID: `{BINANCE_ID}`\n\n"
                f"পাঠানোর পর আপনার **Order ID (TXID)** দিন:"
            )
            bot.send_message(user_id, binance_msg, parse_mode="Markdown")
        except ValueError:
            bot.send_message(user_id, "⚠️ সঠিক সংখ্যা লিখুন (যেমন: 10)")

    elif user_state.get(user_id, {}).get("step") == "waiting_order_id":
        user_state[user_id]["order_id"] = text
        user_state[user_id]["step"] = "waiting_screenshot"
        bot.send_message(user_id, "✅ Order ID নেওয়া হয়েছে। এখন আপনার Binance Payment-এর **screenshot** দিন:")

    elif user_state.get(user_id, {}).get("step") == "waiting_bkash":
        user_state[user_id]["bkash_number"] = text
        data = user_state[user_id]
        user_state[user_id]["step"] = "completed"

        summary_msg = (
            f"🎉 **আপনার অর্ডার সফলভাবে সাবমিট হয়েছে!**\n\n"
            f"💵 ডলার: {data['amount']} USD\n"
            f"💰 টাকা: ৳{data['total_taka']}\n"
            f"🆔 Order ID: {data['order_id']}\n"
            f"📱 বিকাশ: {data['bkash_number']}\n\n"
            f"⏳ **১৫ মিনিট অপেক্ষা করুন। পেমেন্ট গেলে এসএমএস পাবেন।**"
        )
        bot.send_message(user_id, summary_msg, parse_mode="Markdown", reply_markup=main_menu())

        admin_notification = (
            f"🚨 **NEW DOLLAR SELL ORDER!** 🚨\n\n"
            f"👤 User ID: `{user_id}`\n"
            f"💵 Dollar: **{data['amount']} USD**\n"
            f"💱 Taka: **৳{data['total_taka']}**\n"
            f"🆔 Order ID: `{data['order_id']}`\n"
            f"📱 bKash: `{data['bkash_number']}`"
        )
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("✅ Approve", callback_data=f"app_{user_id}"),
            types.InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")
        )
        
        if data.get("photo_file_id"):
            bot.send_photo(ADMIN_ID, data["photo_file_id"], caption=admin_notification, parse_mode="Markdown", reply_markup=admin_markup)
        else:
            bot.send_message(ADMIN_ID, admin_notification, parse_mode="Markdown", reply_markup=admin_markup)

@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    user_id = message.from_user.id
    if user_state.get(user_id, {}).get("step") == "waiting_screenshot":
        user_state[user_id]["photo_file_id"] = message.photo[-1].file_id
        user_state[user_id]["step"] = "waiting_bkash"
        bot.send_message(user_id, "✅ স্ক্রিনশট সেভ হয়েছে। এখন আপনার যে **বিকাশ নম্বরে** টাকা নিতে চান তা লিখে পাঠান:")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global DOLAR_RATE
    user_id = call.from_user.id
    data = call.data

    if user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ অনুমতি নেই!", show_alert=True)
        return

    if data.startswith("app_"):
        target_user = int(data.split("_")[1])
        bot.answer_callback_query(call.id, "Approved")
        bot.send_message(target_user, "🎉 **আপনার অর্ডারটি অ্যাপ্রুভ ও পেমেন্ট সম্পন্ন হয়েছে!**", parse_mode="Markdown", reply_markup=main_menu())
        bot.edit_message_caption(caption=call.message.caption + "\n\n✅ **STATUS: APPROVED**", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif data.startswith("rej_"):
        target_user = int(data.split("_")[1])
        bot.answer_callback_query(call.id, "Rejected")
        bot.send_message(target_user, "⚠️ **আপনার অর্ডারটি রিজেক্ট করা হয়েছে। সঠিক তথ্য দিয়ে আবার চেষ্টা করুন।**", parse_mode="Markdown", reply_markup=main_menu())
        bot.edit_message_caption(caption=call.message.caption + "\n\n❌ **STATUS: REJECTED**", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif data == "admin_toggle":
        bot_status["is_active"] = not bot_status["is_active"]
        bot.answer_callback_query(call.id, f"Status changed", show_alert=True)

    elif data == "admin_rate":
        bot.answer_callback_query(call.id, f"Rate: {DOLAR_RATE}", show_alert=True)

    elif data == "admin_broadcast":
        user_state[ADMIN_ID] = {"step": "waiting_broadcast"}
        bot.send_message(ADMIN_ID, "📢 ব্রডকাস্ট মেসেজটি লিখে পাঠান:")

if __name__ == "__main__":
    set_webhook_url()
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
