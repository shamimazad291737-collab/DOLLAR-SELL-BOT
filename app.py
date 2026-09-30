import os
import telebot
from telebot import types

# শুধু টেলিগ্রাম টোকেনটি রেলওয়ে ভ্যারিয়েবল থেকে নেওয়া হবে
TOKEN = os.environ.get('BOT_TOKEN')

# বাকি সব কনফিগারেশন আপনি এখানে সরাসরি বসিয়ে দিন
ADMIN_ID = 6123456789          # আপনার টেলিগ্রাম অ্যাডমিন আইডি এখানে দিন
BINANCE_ID = "123456789"       # আপনার বাইন্যান্স পে আইডি এখানে দিন
ADMIN_BKASH = "01XXXXXXXXX"    # আপনার বিকাশ নম্বর এখানে দিন
ADMIN_USERNAME = "SAIM_X9"     # আপনার ইউজারনেম
DOLAR_RATE = 119.0             # বর্তমান ডলার রেট

bot = telebot.TeleBot(TOKEN)

user_state = {}
bot_status = {"is_active": True}

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_sell = types.KeyboardButton("💵 SELL DOLLER NOW")
    btn_support = types.KeyboardButton("📞 SUPPORT & HELP")
    btn_admin = types.KeyboardButton("👑 ADMIN PANEL")
    markup.add(btn_sell, btn_support, btn_admin)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not bot_status["is_active"] and message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⚠️ Dukkito! Bortomane amader service bondho royeche.")
        return
    
    user_state.pop(message.from_user.id, None)
    welcome_text = (
        f"🌟 Premium Dollar Exchange Zone e apnake shagotom! 🌟\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💱 Bortoman Rate: 1 USD = {DOLAR_RATE} BDT\n"
        f"⚡ Sebaa: Druto o nirapod len-den.\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👇 Apnar proyojonio option niche theke select korun:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text

    if not bot_status["is_active"] and user_id != ADMIN_ID:
        bot.reply_to(message, "⚠️ Bot-ti bortomane offline royeche.")
        return

    if text == "💵 SELL DOLLER NOW":
        user_state[user_id] = {"step": "waiting_amount"}
        msg = (
            f"🎉 Ovinondon! Apni amader sathe shofolvabe dollar sell shuru korechen.\n\n"
            f"📈 Bortoman exchange rate: {DOLAR_RATE} BDT / USD\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✏️ Apni koto dollar (USD) sell korte chan?\n"
            f"Dya kore shudhu songkha ti (je: 10 ba 50) niche likhe pathan:"
        )
        bot.send_message(user_id, msg, reply_markup=main_menu())

    elif text == "📞 SUPPORT & HELP":
        user_state.pop(user_id, None)
        support_msg = (
            f"🛠 Customer Support & Help Desk\n\n"
            f"Jekono proyojone amader official admin-er sathe jogajog korun:\n\n"
            f"👤 Admin Username: @{ADMIN_USERNAME}"
        )
        bot.send_message(user_id, support_msg, reply_markup=main_menu())

    elif text == "👑 ADMIN PANEL":
        if user_id != ADMIN_ID:
            bot.send_message(user_id, f"❌ Apnar ei panel use korar permission nei!\n\nApnar Telegram User ID: {user_id}", reply_markup=main_menu())
            return
        
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
            types.InlineKeyboardButton("💱 Change Rate", callback_data="admin_rate"),
            types.InlineKeyboardButton("🔄 Bot On/Off", callback_data="admin_toggle")
        )
        bot.send_message(user_id, "👑 Admin Control Panel\n\nNicher option gulo theke kaj select korun:", reply_markup=admin_markup)

    elif user_state.get(user_id, {}).get("step") == "waiting_broadcast":
        if user_id == ADMIN_ID:
            user_state.pop(user_id, None)
            bot.send_message(user_id, f"✅ Broadcast shofolvabe somponno hoyeche!\n\nMessage:\n{text}", reply_markup=main_menu())

    elif user_state.get(user_id, {}).get("step") == "waiting_amount":
        try:
            amount = float(text)
            total_taka = amount * DOLAR_RATE
            user_state[user_id]["amount"] = amount
            user_state[user_id]["total_taka"] = total_taka
            user_state[user_id]["step"] = "waiting_order_id"

            binance_msg = (
                f"✅ Apni sell korte chacchen: {amount} USD\n"
                f"💰 Apni paben: {total_taka} BDT\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💎 Payment Nirdeshika:\n"
                f"Dya kore nicher Binance Pay ID te dollar send korun:\n\n"
                f"🆔 Binance Pay ID: {BINANCE_ID}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📥 Dollar pathanor por Order ID (TXID) ti ekhane likhe pathan:"
            )
            bot.send_message(user_id, binance_msg, reply_markup=main_menu())
        except ValueError:
            bot.send_message(user_id, "⚠️ Dya kore sothik songkha likhun (je: 10 ba 20)", reply_markup=main_menu())

    elif user_state.get(user_id, {}).get("step") == "waiting_order_id":
        user_state[user_id]["order_id"] = text
        user_state[user_id]["step"] = "waiting_screenshot"
        bot.send_message(user_id, "✅ Order ID grohon kora hoyeche!\n\n📸 Ekhon apnar Binance Payment-er screenshot chobi akare pathan:", reply_markup=main_menu())

    elif user_state.get(user_id, {}).get("step") == "waiting_bkash":
        user_state[user_id]["bkash_number"] = text
        data = user_state[user_id]
        user_state[user_id]["step"] = "completed"

        summary_msg = (
            f"🎉 Order-ti shofolvabe submit hoyeche!\n\n"
            f"💵 Dollar: {data['amount']} USD\n"
            f"💰 Taka: {data['total_taka']} BDT\n"
            f"🆔 Order ID: {data['order_id']}\n"
            f"📱 Bkash: {data['bkash_number']}\n\n"
            f"⏳ 15 minit opekkha korun. Payment somponno hole sms paben."
        )
        bot.send_message(user_id, summary_msg, reply_markup=main_menu())

        admin_notification = (
            f"🚨 NEW DOLLAR SELL ORDER! 🚨\n\n"
            f"👤 User ID: {user_id}\n"
            f"💵 Dollar: {data['amount']} USD\n"
            f"💱 Taka: {data['total_taka']} BDT\n"
            f"🆔 Order ID: {data['order_id']}\n"
            f"📱 bKash: {data['bkash_number']}"
        )
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("✅ Approve", callback_data=f"app_{user_id}"),
            types.InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")
        )
        
        if data.get("photo_file_id"):
            bot.send_photo(ADMIN_ID, data["photo_file_id"], caption=admin_notification, reply_markup=admin_markup)
        else:
            bot.send_message(ADMIN_ID, admin_notification, reply_markup=admin_markup)

@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    user_id = message.from_user.id
    if user_state.get(user_id, {}).get("step") == "waiting_screenshot":
        user_state[user_id]["photo_file_id"] = message.photo[-1].file_id
        user_state[user_id]["step"] = "waiting_bkash"
        
        bot.send_message(
            user_id, 
            "✅ Screenshot shongrokkhon kora hoyeche!\n\n"
            "💳 Ekhon apnar je bkash number-e taka nite chan ta niche likhe pathan:",
            reply_markup=main_menu()
        )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global DOLAR_RATE
    user_id = call.from_user.id
    data = call.data

    if user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Ei kaj korar permission nei!", show_alert=True)
        return

    if data.startswith("app_"):
        target_user = int(data.split("_")[1])
        bot.answer_callback_query(call.id, "Approved!")
        bot.send_message(
            target_user, 
            "🎉 Ovinondon! Apnar dollar order-ti verify o payment somponno hoyeche.", 
            reply_markup=main_menu()
        )
        try:
            bot.edit_message_caption(caption=call.message.caption + "\n\n✅ STATUS: APPROVED & PAID", chat_id=call.message.chat.id, message_id=call.message.message_id)
        except Exception:
            bot.edit_message_text(text=call.message.text + "\n\n✅ STATUS: APPROVED & PAID", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif data.startswith("rej_"):
        target_user = int(data.split("_")[1])
        bot.answer_callback_query(call.id, "Rejected.")
        bot.send_message(
            target_user, 
            "⚠️ Sotorkobarta! Apnar order-ti reject kora hoyeche. Sothik tottho diye abar resubmit korun.", 
            reply_markup=main_menu()
        )
        try:
            bot.edit_message_caption(caption=call.message.caption + "\n\n❌ STATUS: REJECTED", chat_id=call.message.chat.id, message_id=call.message.message_id)
        except Exception:
            bot.edit_message_text(text=call.message.text + "\n\n❌ STATUS: REJECTED", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif data == "admin_toggle":
        bot_status["is_active"] = not bot_status["is_active"]
        status_text = "Active" if bot_status["is_active"] else "Off"
        bot.answer_callback_query(call.id, f"Status: {status_text}", show_alert=True)

    elif data == "admin_rate":
        bot.answer_callback_query(call.id, f"Rate: {DOLAR_RATE} BDT", show_alert=True)

    elif data == "admin_broadcast":
        user_state[ADMIN_ID] = {"step": "waiting_broadcast"}
        bot.send_message(ADMIN_ID, "📢 Broadcast message-ti likhe pathan:")

if __name__ == "__main__":
    print("Bot is starting on Railway...")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
