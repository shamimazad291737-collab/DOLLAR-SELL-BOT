import os
import telebot
from telebot import types
from flask import Flask, request

TOKEN = os.environ.get('BOT_TOKEN')
try:
    ADMIN_ID = int(os.environ.get('ADMIN_ID', '0'))
except ValueError:
    ADMIN_ID = 0

BINANCE_ID = os.environ.get('BINANCE_ID', 'YOUR_BINANCE_ID')
ADMIN_BKASH = os.environ.get('ADMIN_BKASH', '01XXXXXXXXX')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'SAIM_X9')
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
        bot.reply_to(message, "⚠️ Dukkito! Bortomane amader service bondho royeche.")
        return
    
    user_state.pop(message.from_user.id, None)
    welcome_text = (
        f"🌟 **Premium Dollar Exchange Zone e apnake shagotom!** 🌟\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💱 **Bortoman Rate:** `1 USD = ৳{DOLAR_RATE}`\n"
        f"⚡ **Sebaa:** Druto o nirapod len-den.\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👇 Apnar proyojonio option niche theke select korun:"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "💵 SELL DOLLER NOW")
def handle_sell(message):
    user_id = message.from_user.id
    user_state[user_id] = {"step": "waiting_amount"}
    msg = (
        f"🎉 **Ovinondon! Apni amader sathe shofolvabe dollar sell shuru korechen.**\n\n"
        f"📈 Bortoman exchange rate: **৳{DOLAR_RATE} / USD**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✏️️ **Apni koto dollar (USD) sell korte chan?**\n"
        f"Dya kore shudhu songkha ti (jemon: `10` ba `50`) niche likhe pathan:"
    )
    bot.send_message(user_id, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "📞 SUPPORT & HELP")
def handle_support(message):
    user_id = message.from_user.id
    support_msg = (
        f"🛠 **Customer Support & Help Desk**\n\n"
        f"Jekono proyojone amader official admin-er sathe jogajog korun:\n\n"
        f"👤 **Admin Username:** @{ADMIN_USERNAME}\n"
        f"⚡ Amra 24 ghonta apnar sohayotay niyojito."
    )
    bot.send_message(user_id, support_msg, parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "👑 ADMIN PANEL")
def handle_admin(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.send_message(user_id, f"❌ Apnar ei panel use korar permission nei!\n\nApnar Telegram User ID: `{user_id}`\n(Eta Render-er ADMIN_ID variable-e bosan)", parse_mode="Markdown")
        return
    
    admin_markup = types.InlineKeyboardMarkup(row_width=2)
    admin_markup.add(
        types.InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
        types.InlineKeyboardButton("💱 Change Rate", callback_data="admin_rate"),
        types.InlineKeyboardButton("🔄 Bot On/Off", callback_data="admin_toggle")
    )
    bot.send_message(user_id, "👑 **Admin Control Panel**\n\nNicher option gulo theke kaj select korun:", parse_mode="Markdown", reply_markup=admin_markup)

@bot.message_handler(func=lambda message: True)
def handle_text_steps(message):
    user_id = message.from_user.id
    text = message.text
    current_state = user_state.get(user_id, {}).get("step")

    if not bot_status["is_active"] and user_id != ADMIN_ID:
        bot.reply_to(message, "⚠️ Bot-ti bortomane offline royeche.")
        return

    if current_state == "waiting_broadcast":
        if user_id == ADMIN_ID:
            user_state.pop(user_id, None)
            bot.send_message(user_id, f"✅ Broadcast shofolvabe somponno hoyeche!\n\nMessage:\n{text}")

    elif current_state == "waiting_amount":
        try:
            amount = float(text)
            total_taka = amount * DOLAR_RATE
            user_state[user_id]["amount"] = amount
            user_state[user_id]["total_taka"] = total_taka
            user_state[user_id]["step"] = "waiting_order_id"

            binance_msg = (
                f"✅ Apni sell korte chacchen: **{amount} USD**\n"
                f"💰 Apni paben: **৳{total_taka}**\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💎 **Payment Nirdeshika:**\n"
                f"Dya kore nicher Binance Pay ID te dollar send korun:\n\n"
                f"🆔 **Binance Pay ID:** `{BINANCE_ID}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📥 Dollar pathanor por **Order ID (TXID)** ti ekhane likhe pathan:"
            )
            bot.send_message(user_id, binance_msg, parse_mode="Markdown")
        except ValueError:
            bot.send_message(user_id, "⚠️ Dya kore sothik songkha likhun (jemon: 10 ba 20)")

    elif current_state == "waiting_order_id":
        user_state[user_id]["order_id"] = text
        user_state[user_id]["step"] = "waiting_screenshot"
        bot.send_message(user_id, "✅ **Order ID grohon kora hoyeche!**\n\n📸 Ekhon apnar Binance Payment-er **screenshot** chobi akare pathan:")

    elif current_state == "waiting_bkash":
        user_state[user_id]["bkash_number"] = text
        data = user_state[user_id]
        user_state[user_id]["step"] = "completed"

        summary_msg = (
            f"🎉 **Order-ti shofolvabe submit hoyeche!**\n\n"
            f"💵 Dollar: `{data['amount']} USD`\n"
            f"💰 Taka: `৳{data['total_taka']}`\n"
            f"🆔 Order ID: `{data['order_id']}`\n"
            f"📱 Bkash: `{data['bkash_number']}`\n\n"
            f"⏳ **15 minit opekkha korun. Payment somponno hole sms paben.**"
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
    else:
        bot.send_message(user_id, "👇 Dya kore nicher menu theke kono option select korun:", reply_markup=main_menu())

@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    user_id = message.from_user.id
    if user_state.get(user_id, {}).get("step") == "waiting_screenshot":
        user_state[user_id]["photo_file_id"] = message.photo[-1].file_id
        user_state[user_id]["step"] = "waiting_bkash"
        
        bot.send_message(
            user_id, 
            "✅ **Screenshot shongrokkhon kora hoyeche!**\n\n"
            "💳 Ekhon apnar je **bkash number**-e taka nite chan ta niche likhe pathan:"
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
            "🎉 **Ovinondon! Apnar dollar order-ti verify o payment somponno hoyeche.**", 
            parse_mode="Markdown", 
            reply_markup=main_menu()
        )
        bot.edit_message_caption(caption=call.message.caption + "\n\n✅ **STATUS: APPROVED & PAID**", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif data.startswith("rej_"):
        target_user = int(data.split("_")[1])
        bot.answer_callback_query(call.id, "Rejected.")
        bot.send_message(
            target_user, 
            "⚠️️ **Sotorkobarta! Apnar order-ti reject kora hoyeche. Sothik tottho diye abar resubmit korun.**", 
            parse_mode="Markdown", 
            reply_markup=main_menu() ba main_menu()
        )
        bot.edit_message_caption(caption=call.message.caption + "\n\n❌ **STATUS: REJECTED**", chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif data == "admin_toggle":
        bot_status["is_active"] = not bot_status["is_active"]
        status_text = "Active" if bot_status["is_active"] else "Off"
        bot.answer_callback_query(call.id, f"Status: {status_text}", show_alert=True)

    elif data == "admin_rate":
        bot.answer_callback_query(call.id, f"Rate: ৳{DOLAR_RATE}", show_alert=True)

    elif data == "admin_broadcast":
        user_state[ADMIN_ID] = {"step": "waiting_broadcast"}
        bot.send_message(ADMIN_ID, "📢 Broadcast message-ti likhe pathan:")

if __name__ == "__main__":
    set_webhook_url()
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
