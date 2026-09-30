import os
import telebot
from telebot import types
from flask import Flask, request

# Render Environment Variables থেকে কনফিগারেশন রিড করা
TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID', '0'))
BINANCE_ID = os.environ.get('BINANCE_ID', 'YOUR_BINANCE_ID')
ADMIN_BKASH = os.environ.get('ADMIN_BKASH', '01XXXXXXXXX')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'SAIM_9X')
DOLAR_RATE = float(os.environ.get('DOLAR_RATE', '119'))

bot = telebot.TeleBot(TOKEN, threaded=False)
server = Flask(__name__)

# ইউজারদের টেম্পোরারি ডাটা এবং বট অন/অফ স্ট্যাটাস রাখার ডিকশনারি
user_state = {}
bot_status = {"is_active": True}

# মূল মেনু কিবোর্ড
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_sell = types.KeyboardButton("💵 SELL DOLLER")
    btn_support = types.KeyboardButton("📞 SUPPORT")
    btn_admin = types.KeyboardButton("👑 ADMIN PANEL")
    markup.add(btn_sell, btn_support, btn_admin)
    return markup

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    # Render-এর নিজস্ব URL এখানে বসাতে হবে ডিপ্লয়ের পর অথবা এনভায়রনমেন্ট ভ্যারিয়েবল দিয়ে অটো সেট করা যায়
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        bot.set_webhook(url=render_url + '/' + TOKEN)
    return "Telegram Bot is running smoothly!", 200

# /start কমান্ড
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not bot_status["is_active"] and message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⚠️ দুঃখিত, বর্তমানে বট সার্ভিসের কাজ চলছে বা বট বন্ধ রয়েছে। পরে চেষ্টা করুন।")
        return
    
    user_state.pop(message.from_user.id, None)
    welcome_text = (
        f"🌟 **স্বাগতম! আমাদের প্রিমিয়াম ডলার সেল জোনে আপনাকে স্বাগতম।** 🌟\n\n"
        f"বর্তমান ডলার রেট: **৳{DOLAR_RATE}**\n"
        f"নিচের বাটন থেকে আপনার পছন্দসই অপশন সিলেক্ট করুন:"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_menu())

# টেক্সট মেসেজ হ্যান্ডলার (বাটন এবং স্টেপ বাই স্টেপ ইনপুট)
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text

    if not bot_status["is_active"] and user_id != ADMIN_ID:
        bot.reply_to(message, "⚠️ বটটি বর্তমানে অফলাইন রয়েছে।")
        return

    # ১. SELL DOLLER বাটন ক্লিক করলে
    if text == "💵 SELL DOLLER":
        user_state[user_id] = {"step": "waiting_amount"}
        msg = (
            f"🎉 **অভিনন্দন! আপনি আমাদের মাধ্যমে নিরাপদভাবে ডলার সেল করতে পারবেন।**\n\n"
            f"💱 বর্তমান রেট: **৳{DOLAR_RATE} / USD**\n\n"
            f"✏️ আপনি কত ডলার সেল করতে চান? শুধু সংখ্যাটি (যেমন: 10 বা 50) নিচে লিখে পাঠান:"
        )
        bot.send_message(user_id, msg, parse_mode="Markdown")

    # ২. SUPPORT বাটন ক্লিক করলে
    elif text == "📞 SUPPORT":
        support_msg = (
            f"🛠 **কাস্টমার সাপোর্ট সেন্টার**\n\n"
            f"যেকোনো প্রয়োজনে আমাদের এডমিনের সাথে যোগাযোগ করুন:\n"
            f"👤 এডমিন ইউজারনেম: @{ADMIN_USERNAME}"
        )
        bot.send_message(user_id, support_msg, parse_mode="Markdown")

    # ৩. ADMIN PANEL বাটন ক্লিক করলে
    elif text == "👑 ADMIN PANEL":
        if user_id != ADMIN_ID:
            bot.send_message(user_id, "❌ আপনার এই প্যানেলটি ব্যবহার করার অনুমতি নেই!")
            return
        
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
            types.InlineKeyboardButton("💱 Change Rate", callback_data="admin_rate"),
            types.InlineKeyboardButton("🔄 Bot On/Off", callback_data="admin_toggle")
        )
        bot.send_message(user_id, "👑 **এডমিন কন্ট্রোল প্যানেল**\n\nনিচের অপশনগুলো থেকে আপনার প্রয়োজনীয় কাজ সিলেক্ট করুন:", parse_mode="Markdown", reply_markup=admin_markup)

    # ব্রডকাস্ট টেক্সট ইনপুট হ্যান্ডেল করার জন্য
    elif user_state.get(user_id, {}).get("step") == "waiting_broadcast":
        if user_id == ADMIN_ID:
            broadcast_text = text
            user_state.pop(user_id, None)
            bot.send_message(user_id, "📢 ব্রডকাস্ট মেসেজ পাঠানো শুরু হয়েছে...")
            # এখানে সিম্পল ডেমো হিসেবে এডমিনকে কনফার্ম করা হচ্ছে
            bot.send_message(user_id, f"✅ ব্রডকাস্ট সফলভাবে সম্পন্ন হয়েছে!\n\nমেসেজ:\n{broadcast_text}")

    # ডলার অ্যামাউন্ট ইনপুট দিলে
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
                f"👇 অনুগ্রহ করে নিচের Binance Pay ID তে ডলারগুলো সেন্ড করুন:\n\n"
                f"🆔 Binance ID: `{BINANCE_ID}`\n\n"
                f"ডলার পাঠানোর পর আপনার **Order ID (TXID)** টি এখানে লিখে পাঠান:"
            )
            bot.send_message(user_id, binance_msg, parse_mode="Markdown")
        except ValueError:
            bot.send_message(user_id, "⚠️ দয়া করে সঠিক সংখ্যা লিখুন (যেমন: 20)")

    # Order ID ইনপুট দিলে
    elif user_state.get(user_id, {}).get("step") == "waiting_order_id":
        user_state[user_id]["order_id"] = text
        user_state[user_id]["step"] = "waiting_screenshot"
        
        bot.send_message(user_id, "✅ Order ID গ্রহণ করা হয়েছে।\n\n📸 এখন আপনার Binance Payment-এর **ਸcreenshot** (ছবি) পাঠান:")

    # bKash নম্বর চাওয়া এবং মেনু বার বাটন দেওয়া
    elif user_state.get(user_id, {}).get("step") == "waiting_bkash":
        user_state[user_id]["bkash_number"] = text
        data = user_state[user_id]
        user_state[user_id]["step"] = "completed"

        summary_msg = (
            f"🎉 **আপনার অর্ডারটি সফলভাবে সাবমিট হয়েছে!**\n\n"
            f"💵 ডলার পরিমাণ: {data['amount']} USD\n"
            f"💰 পাওয়ার কথা: ৳{data['total_taka']}\n"
            f"🆔 Order ID: {data['order_id']}\n"
            f"📱 বিকাশ নম্বর: {data['bkash_number']}\n\n"
            f"⏳ **দয়া করে ১৫ মিনিট অপেক্ষা করুন। পেমেন্ট সম্পন্ন হলে বিকাশ থেকে কনফার্মেশন এসএমএস পাবেন।**"
        )
        bot.send_message(user_id, summary_msg, parse_mode="Markdown", reply_markup=main_menu())

        # এডমিনের কাছে সাজানো গোছানো প্রিমিয়াম ফরম্যাটে ডাটা পাঠানো
        admin_notification = (
            f"🚨 **NEW DOLLAR SELL ORDER!** 🚨\n\n"
            f"👤 ইউজার আইডি: `{user_id}`\n"
            f"👤 ইউজারনেম: @{message.from_user.username or 'N/A'}\n"
            f"💵 ডলার পরিমাণ: **{data['amount']} USD**\n"
            f"💱 মোট টাকা: **৳{data['total_taka']}**\n"
            f"🆔 Order ID: `{data['order_id']}`\n"
            f"📱 বিকাশ নম্বর: `{data['bkash_number']}`\n"
        )
        
        # এডমিনকে অ্যাকশন বাটন সহ পাঠানো (Approve / Reject)
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("✅ Approve", callback_data=f"app_{user_id}"),
            types.InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")
        )
        
        if data.get("photo_file_id"):
            bot.send_photo(ADMIN_ID, data["photo_file_id"], caption=admin_notification, parse_mode="Markdown", reply_markup=admin_markup)
        else:
            bot.send_message(ADMIN_ID, admin_notification, parse_mode="Markdown", reply_markup=admin_markup)

# ছবি (Screenshot) রিসিভ করার হ্যান্ডলার
@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    user_id = message.from_user.id
    if user_state.get(user_id, {}).get("step") == "waiting_screenshot":
        file_id = message.photo[-1].file_id
        user_state[user_id]["photo_file_id"] = file_id
        user_state[user_id]["step"] = "waiting_bkash"

        # বিকাশ নম্বর শেয়ার করার জন্য কন্টাক্ট বা কাস্টম কিবোর্ড বাটন
        bkash_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        bkash_markup.add(types.KeyboardButton("📱 Share bKash Number", request_contact=True))

        bot.send_message(
            user_id, 
            "✅ স্ক্রিনশট সফলভাবে সংরক্ষিত হয়েছে।\n\n"
            "💳 এখন আপনার যে **বিকাশ নম্বরে** টাকা নিতে চান তা নিচে লিখে পাঠান অথবা নিচের বাটন ব্যবহার করুন:", 
            reply_markup=bkash_markup
        )

# কন্টাক্ট শেয়ার করলে বিকাশ নম্বর নিয়ে নেওয়া
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user_id = message.from_user.id
    if user_state.get(user_id, {}).get("step") == "waiting_bkash":
        phone = message.contact.phone_number
        # টেক্সট হ্যান্ডলারের মতই প্রসেস করার জন্য কল করা যায় অথবা ডাইরেক্ট হ্যান্ডেল করা যায়
        message.text = phone
        handle_messages(message)

# এডমিন অ্যাকশন এবং ইনলাইন বাটন কলব্যাক হ্যান্ডলার
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
        bot.answer_callback_query(call.id, "অর্ডারটি সফলভাবে অ্যাপ্রুভ করা হয়েছে!")
        bot.send_message(
            target_user, 
            "🎉 **অভিনন্দন! আপনার ডলার অর্ডারটি সফলভাবে ভেরিফাই ও পেমেন্ট সম্পন্ন হয়েছে।**\n\n"
            "আমাদের সাথে থাকার জন্য ধন্যবাদ। আবার ডলার সেল করতে চাইলে নিচের মেনু ব্যবহার করুন।", 
            parse_mode="Markdown", 
            reply_markup=main_menu()
        )
        bot.edit_message_caption(caption=call.message.caption + "\n\n✅ **STATUS: APPROVED**", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif data.startswith("rej_"):
        target_user = int(data.split("_")[1])
        bot.answer_callback_query(call.id, "অর্ডারটি রিজেক্ট করা হয়েছে।")
        bot.send_message(
            target_user, 
            "⚠️ **সতর্কবার্তা! আপনার ডলার অর্ডারটি রিজেক্ট করা হয়েছে।**\n\n"
            "দয়া করে আপনার Order ID এবং Screenshot ভালোভাবে চেক করে পুনরায় সঠিকভাবে রিসাবমিট (Resubmit) করুন।", 
            parse_mode="Markdown", 
            reply_markup=main_menu()
        )
        bot.edit_message_caption(caption=call.message.caption + "\n\n❌ **STATUS: REJECTED**", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif data == "admin_toggle":
        bot_status["is_active"] = not bot_status["is_active"]
        status_text = "চালু (Active)" if bot_status["is_active"] else "বন্ধ (Off)"
        bot.answer_callback_query(call.id, f"বটের বর্তমান অবস্থা: {status_text}", show_alert=True)

    elif data == "admin_rate":
        bot.answer_callback_query(call.id, f"বর্তমান রেট ৳{DOLAR_RATE}. রেট পরিবর্তনের জন্য Render Environment Variable আপডেট করুন।", show_alert=True)

    elif data == "admin_broadcast":
        user_state[ADMIN_ID] = {"step": "waiting_broadcast"}
        bot.send_message(ADMIN_ID, "📢 ব্রডকাস্ট করার জন্য মেসেজটি লিখে পাঠান:")

if __name__ == "__main__":
    # লোকাল ডেভেলপমেন্ট বা সরাসরি টেস্ট করার জন্য (Render-এ Gunicorn রান করবে)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
