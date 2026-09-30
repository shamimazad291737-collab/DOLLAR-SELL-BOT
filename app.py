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
    btn_sell = types.KeyboardButton("💵 SELL DOLLER NOW")
    btn_support = types.KeyboardButton("📞 SUPPORT & HELP")
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
    return "🚀 Premium Dollar Sell Bot is running smoothly!", 200

def set_webhook_url():
    bot.remove_webhook()
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        bot.set_webhook(url=f"{render_url}/{TOKEN}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not bot_status["is_active"] and message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⚠️ দুঃখಿತ! বর্তমানে আমাদের সার্ভিস সাময়িকভাবে বন্ধ রয়েছে। একটু পরে আবার চেষ্টা করুন।")
        return
    
    user_state.pop(message.from_user.id, None)
    welcome_text = (
        f"🌟 **అlān! প্রিমিয়াম ডলার এক্সচেঞ্জ জোনে আপনাকে স্বাগতম!** 🌟\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💱 **বর্তমান রেট:** `1 USD = ৳{DOLAR_RATE}`\n"
        f"⚡ **সেবা:** দ্রুত ও শতভাগ নিরাপদ লেনদেন।\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👇 আপনার প্রয়োজনীয় অপশনটি নিচে থেকে সিলেক্ট করুন:"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text

    if not bot_status["is_active"] and user_id != ADMIN_ID:
        bot.reply_to(message, "⚠️ বটটি বর্তমানে অফলাইন রয়েছে।")
        return

    if text == "💵 SELL DOLLER NOW":
        user_state[user_id] = {"step": "waiting_amount"}
        msg = (
            f"🎉 **অভিনন্দন! আপনি আমাদের সাথে সফলভাবে ডলার সেল প্রক্রিয়া শুরু করেছেন।**\n\n"
            f"📈 বর্তমান এক্সচেঞ্জ রেট: **৳{DOLAR_RATE} / USD**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✏️ **আপনি কত ডলার (USD) সেল করতে চান?**\n"
            f"দয়া করে শুধু সংখ্যাটি (যেমন: `10` বা `50`) নিচে লিখে পাঠান:"
        )
        bot.send_message(user_id, msg, parse_mode="Markdown")

    elif text == "📞 SUPPORT & HELP":
        support_msg = (
            f"🛠 **কাস্টমার সাপোর্ট ও হেল্প ডেস্ক**\n\n"
            f"লেনদেন বা অন্য যেকোনো প্রয়োজনে সরাসরি আমাদের অফিসিয়াল এডমিনের সাথে যোগাযোগ করুন:\n\n"
            f"👤 **Admin Username:** @{ADMIN_USERNAME}\n"
            f"⚡ আমরা ২৪/ঘন্টা আপনার সহায়তায় নিয়োজিত।"
        )
        bot.send_message(user_id, support_msg, parse_mode="Markdown")

    elif text == "👑 ADMIN PANEL":
        if user_id != ADMIN_ID:
            bot.send_message(user_id, "❌ আপনার এই প্যানেলটি ব্যবহারের অনুমতি নেই!")
            return
        
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
            types.InlineKeyboardButton("💱 Change Rate", callback_data="admin_rate"),
            types.InlineKeyboardButton("🔄 Bot On/Off", callback_data="admin_toggle")
        )
        bot.send_message(user_id, "👑 **এডমিন কন্ট্রোল প্যানেল**\n\nনিচের অপশনগুলো থেকে আপনার প্রয়োজনীয় কাজ সিলেক্ট করুন:", parse_mode="Markdown", reply_markup=admin_markup)

    elif user_state.get(user_id, {}).get("step") == "waiting_broadcast":
        if user_id == ADMIN_ID:
            user_state.pop(user_id, None)
            bot.send_message(user_id, f"✅ ব্রডকাস্ট সফলভাবে সম্পন্ন হয়েছে!\n\nমেসেজ:\n{text}")

    elif user_state.get(user_id, {}).get("step") == "waiting_amount":
        try:
            amount = float(text)
            total_taka = amount * DOLAR_RATE
            user_state[user_id]["amount"] = amount
            user_state[user_id]["total_taka"] = total_taka
            user_state[user_id]["step"] = "waiting_order_id"

            binance_msg = (
                f"✅ আপনি সেল করতে চাচ্ছেন: **{amount} USD**\n"
                f"💰 আপনি পাবেন: **৳{total_taka}**\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💎 **পেমেন্ট নির্দেশিকা:**\n"
                f"দয়া করে নিচের Binance Pay ID তে আপনার ডলারগুলো সেন্ড করুন:\n\n"
                f"🆔 **Binance Pay ID:** `{BINANCE_ID}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📥 ডলার পাঠানোর পর প্রাপ্ত **Order ID (TXID)** টি এখানে লিখে পাঠান:"
            )
            bot.send_message(user_id, binance_msg, parse_mode="Markdown")
        except ValueError:
            bot.send_message(user_id, "⚠️ দয়া করে সঠিক সংখ্যা লিখুন (যেমন: 10 বা 20)")

    elif user_state.get(user_id, {}).get("step") == "waiting_order_id":
        user_state[user_id]["order_id"] = text
        user_state[user_id]["step"] = "waiting_screenshot"
        bot.send_message(user_id, "✅ **Order ID সফলভাবে গৃহীত হয়েছে!**\n\n📸 এখন আপনার Binance Payment-এর পরিষ্কার **স্ক্রিনশট (Screenshot)** ছবি আকারে পাঠান:")

    elif user_state.get(user_id, {}).get("step") == "waiting_bkash":
        user_state[user_id]["bkash_number"] = text
        data = user_state[user_id]
        user_state[user_id]["step"] = "completed"

        summary_msg = (
            f"🎉 **অর্ডারটি সফলভাবে সাবমিট হয়েছে!**\n\n"
            f"💵 ডলার পরিমাণ: `{data['amount']} USD`\n"
            f"💰 প্রদেয় টাকা: `৳{data['total_taka']}`\n"
            f"🆔 Order ID: `{data['order_id']}`\n"
            f"📱 বিকাশ নম্বর: `{data['bkash_number']}`\n\n"
            f"⏳ **দয়া করে ১৫ মিনিট অপেক্ষা করুন। পেমেন্ট সম্পন্ন হলে আপনার বিকাশ নাম্বারে কনফার্মেশন এসএমএস চলে যাবে।**"
        )
        bot.send_message(user_id, summary_msg, parse_mode="Markdown", reply_markup=main_menu())

        admin_notification = (
            f"🚨 **NEW DOLLAR SELL ORDER!** 🚨\n\n"
            f"👤 **User ID:** `{user_id}`\n"
            f"💵 **Dollar:** `{data['amount']} USD`\n"
            f"💱 **Taka:** `৳{data['total_taka']}`\n"
            f"🆔 **Order ID:** `{data['order_id']}`\n"
            f"📱 **bKash:** `{data['bkash_number']}`"
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
        
        # বিকাশ নম্বর পাঠানোর জন্য সুন্দর রি-প্লাই কিবোর্ড বাটন
        bkash_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        bkash_markup.add(types.KeyboardButton("📱 Share My Contact/bKash", request_contact=True))
        
        bot.send_message(
            user_id, 
            "✅ **স্ক্রিনশট সফলভাবে সংরক্ষিত হয়েছে!**\n\n"
            "💳 এখন আপনি যে **বিকাশ নম্বরে** টাকা নিতে চান তা নিচে লিখে পাঠান:", 
            reply_markup=bkash_markup
        )

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user_id = message.from_user.id
    if user_state.get(user_id, {}).get("step") == "waiting_bkash":
        phone = message.contact.phone_number
        message.text = phone
        handle_messages(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global DOLAR_RATE
    user_id = call.from_user.id
    data = call.data

    if user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ আপনার এই কাজটি করার অনুমতি নেই!", show_alert=True)
        return

    if data.startswith("app_"):
        target_user = int(data.split("_")[1])
        bot.answer_callback_query(call.id, "Order Approved Successfully!")
        bot.send_message(
            target_user, 
            "🎉 **অভিনন্দন! আপনার ডলার অর্ডারটি সফলভাবে ভেরিফাই ও পেমেন্ট সম্পন্ন হয়েছে।**\n\n"
            "আমাদের সাথে থাকার জন্য ধন্যবাদ। আবার ডলার সেল করতে চাইলে নিচের মেনു ব্যবহার করুন।", 
            parse_mode="Markdown", 
            reply_markup=main_menu()
        )
        bot.edit_message_caption(caption=call.message.caption + "\n\n✅ **STATUS: APPROVED & PAID**", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif data.startswith("rej_"):
        target_user = int(data.split("_")[1])
        bot.answer_callback_query(call.id, "Order Rejected.")
        bot.send_message(
            target_user, 
            "⚠️ **সতর্কবার্তা! আপনার ডলার অর্ডারটি রিজেক্ট করা হয়েছে।**\n\n"
            "দয়া করে আপনার Order ID এবং Screenshot ভালোভাবে চেক করে পুনরায় সঠিক তথ্য দিয়ে রিসাবমিট (Resubmit) করুন।", 
            parse_mode="Markdown", 
            reply_markup=main_menu()
        )
        bot.edit_message_caption(caption=call.message.caption + "\n\n❌ **STATUS: REJECTED**", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif data == "admin_toggle":
        bot_status["is_active"] = not bot_status["is_active"]
        status_text = "Active (চালু)" if bot_status["is_active"] else "Off (বন্ধ)"
        bot.answer_callback_query(call.id, f"বটের বর্তমান স্ট্যাটাস: {status_text}", show_alert=True)

    elif data == "admin_rate":
        bot.answer_callback_query(call.id, f"বর্তমান ডলার রেট: ৳{DOLAR_RATE}", show_alert=True)

    elif data == "admin_broadcast":
        user_state[ADMIN_ID] = {"step": "waiting_broadcast"}
        bot.send_message(ADMIN_ID, "📢 সকল ইউজারের কাছে পাঠানোর জন্য ব্রডকাস্ট মেসেজটি লিখে পাঠান:")

if __name__ == "__main__":
    set_webhook_url()
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
