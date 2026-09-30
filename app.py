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

bot = telebot.TeleBot(TOKEN)
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

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return '', 403

@server.route("/")
def webhook():
    bot.remove_webhook()
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        bot.set_webhook(url=render_url + '/' + TOKEN)
    return "Telegram Bot is running smoothly!", 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not bot_status["is_active"] and message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⚠️ Dukhhito, bortomane bot service bondho royeche.")
        return
    
    user_state.pop(message.from_user.id, None)
    welcome_text = (
        f"🌟 **Shagotom! Amader premium dollar sell zone e apnake shagotom.** 🌟\n\n"
        f"Bortoman dollar rate: **৳{DOLAR_RATE}**\n"
        f"Nicher button theke apnar pochondo option select korun:"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text

    if not bot_status["is_active"] and user_id != ADMIN_ID:
        bot.reply_to(message, "⚠️ Bot-ti bortomane offline royeche.")
        return

    if text == "💵 SELL DOLLER":
        user_state[user_id] = {"step": "waiting_amount"}
        msg = (
            f"🎉 **Ovinondon! Apni amader maddhome nirapode dollar sell korte parben.**\n\n"
            f"💱 Bortoman rate: **৳{DOLAR_RATE} / USD**\n\n"
            f"✏️ Apni koto dollar sell korte chan? Sudhu songkha ti niche likhe pathan:"
        )
        bot.send_message(user_id, msg, parse_mode="Markdown")

    elif text == "📞 SUPPORT":
        support_msg = (
            f"🛠 **Customer Support Center**\n\n"
            f"Jekono proyojone amader admin-er sathe jogajog korun:\n"
            f"👤 Admin username: @{ADMIN_USERNAME}"
        )
        bot.send_message(user_id, support_msg, parse_mode="Markdown")

    elif text == "👑 ADMIN PANEL":
        if user_id != ADMIN_ID:
            bot.send_message(user_id, "❌ Apnar ei panel use korar permission nei!")
            return
        
        admin_markup = types.InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            types.InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
            types.InlineKeyboardButton("💱 Change Rate", callback_data="admin_rate"),
            types.InlineKeyboardButton("🔄 Bot On/Off", callback_data="admin_toggle")
        )
        bot.send_message(user_id, "👑 **Admin Control Panel**\n\nNicher option gulo theke kaj select korun:", parse_mode="Markdown", reply_markup=admin_markup)

    elif user_state.get(user_id, {}).get("step") == "waiting_broadcast":
        if user_id == ADMIN_ID:
            broadcast_text = text
            user_state.pop(user_id, None)
            bot.send_message(user_id, f"✅ Broadcast shofolvabe somponno hoyeche!\n\nMessage:\n{broadcast_text}")

    elif user_state.get(user_id, {}).get("step") == "waiting_amount":
        try:
            amount = float(text)
            total_taka = amount * DOLAR_RATE
            user_state[user_id]["amount"] = amount
            user_state[user_id]["total_taka"] = total_taka
            user_state[user_id]["step"] = "waiting_order_id"

            binance_msg = (
                f"✅ Apni **{amount} USD** sell korte chan.\n"
                f"💰 Mot paben: **৳{total_taka}**\n\n"
                f"👇 Onugroho kore nicher Binance Pay ID te dollar send korun:\n\n"
                f"🆔 Binance ID: `{BINANCE_ID}`\n\n"
                f"Dollar pathanor por apnar **Order ID (TXID)** ti ekhane likhe pathan:"
            )
            bot.send_message(user_id, binance_msg, parse_mode="Markdown")
        except ValueError:
            bot.send_message(user_id, "⚠️ Dya kore thik moto songkha likhun (je: 20)")

    elif user_state.get(user_id, {}).get("step") == "waiting_order_id":
        user_state[user_id]["order_id"] = text
        user_state[user_id]["step"] = "waiting_screenshot"
        bot.send_message(user_id, "✅ Order ID grohon kora hoyeche.\n\n📸 Ekhon apnar Binance Payment-er **screenshot** (chobi) pathan:")

    elif user_state.get(user_id, {}).get("step") == "waiting_bkash":
        user_state[user_id]["bkash_number"] = text
        data = user_state[user_id]
        user_state[user_id]["step"] = "completed"

        summary_msg = (
            f"🎉 **Apnar order-ti shofolvabe submit hoyeche!**\n\n"
            f"💵 Dollar poriman: {data['amount']} USD\n"
            f"💰 Paowar kotha: ৳{data['total_taka']}\n"
            f"🆔 Order ID: {data['order_id']}\n"
            f"📱 Bkash number: {data['bkash_number']}\n\n"
            f"⏳ **Dya kore 15 minit opekkha korun. Payment somponno hole sms paben.**"
        )
        bot.send_message(user_id, summary_msg, parse_mode="Markdown", reply_markup=main_menu())

        admin_notification = (
            f"🚨 **NEW DOLLAR SELL ORDER!** 🚨\n\n"
            f"👤 User ID: `{user_id}`\n"
            f"👤 Username: @{message.from_user.username or 'N/A'}\n"
            f"💵 Dollar: **{data['amount']} USD**\n"
            f"💱 Mot Taka: **৳{data['total_taka']}**\n"
            f"🆔 Order ID: `{data['order_id']}`\n"
            f"📱 Bkash: `{data['bkash_number']}`\n"
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
        file_id = message.photo[-1].file_id
        user_state[user_id]["photo_file_id"] = file_id
        user_state[user_id]["step"] = "waiting_bkash"

        bot.send_message(user_id, "✅ Screenshot shongrokkhon kora hoyeche.\n\n💳 Ekhon apnar je **bkash number**-e taka nite chan ta niche likhe pathan:")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global DOLAR_RATE
    user_id = call.from_user.id
    data = call.data

    if user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Apnar ei kaj korar permission nei!", show_alert=True)
        return

    if data.startswith("app_"):
        target_user = int(data.split("_")[1])
        bot.answer_keyword = "Approved"
        bot.send_message(target_user, "🎉 **Ovinondon! Apnar dollar order-ti verify o payment somponno hoyeche.**", parse_mode="Markdown", reply_markup=main_menu())
        bot.edit_message_caption(caption=call.message.caption + "\n\n✅ **STATUS: APPROVED**", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif data.startswith("rej_"):
        target_user = int(data.split("_")[1])
        bot.send_message(target_user, "⚠️ **Sotorkobarta! Apnar order-ti reject kora hoyeche. Sothik vabe resubmit korun.**", parse_mode="Markdown", reply_markup=main_menu())
        bot.edit_message_caption(caption=call.message.caption + "\n\n❌ **STATUS: REJECTED**", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif data == "admin_toggle":
        bot_status["is_active"] = not bot_status["is_active"]
        status_text = "Active" if bot_status["is_active"] else "Off"
        bot.answer_callback_query(call.id, f"Bot status: {status_text}", show_alert=True)

    elif data == "admin_rate":
        bot.answer_callback_query(call.id, f"Bortoman rate ৳{DOLAR_RATE}", show_alert=True)

    elif data == "admin_broadcast":
        user_state[ADMIN_ID] = {"step": "waiting_broadcast"}
        bot.send_message(ADMIN_ID, "📢 Broadcast message-ti likhe pathan:")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.com.get("PORT", 5000)) if hasattr(os.environ, 'get') else 5000)
