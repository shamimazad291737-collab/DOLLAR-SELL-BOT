import os
import telebot
from flask import Flask
from threading import Thread

# Render-এর Environment Variables থেকে টোকেন এবং অ্যাডমিন আইডি রিড করবে
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Global variables for rates and wallet numbers
bot_data = {
    "sell_rate": 119.00,
    "buy_rate": 122.00,
    "bkash_number": "01700000000 (Personal)",
    "nagad_number": "01800000000 (Personal)"
}

# Web Service সচল রাখার জন্য রেন্ডারের হোমপেজ রুট
@app.route('/')
def home():
    return "<h1>Dollar Sell/Buy Bot is Running Successfully! 🚀</h1>"

# /start command handler (Example এর মতো হুবহু Banglish UI)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_sell = types.InlineKeyboardButton("💸 Sell Dollar", callback_data="sell_dollar")
    btn_buy = types.InlineKeyboardButton("🛒 Buy Dollar", callback_data="buy_dollar")
    btn_rates = types.InlineKeyboardButton("📊 Today's Rate", callback_data="check_rates")
    btn_support = types.InlineKeyboardButton("📞 Customer Support", callback_data="support")
    
    markup.add(btn_sell, btn_buy, btn_rates, btn_support)
    
    # Jodi user admin hoy, tobe admin panel button dekhabe
    if message.from_user.id == ADMIN_ID:
        btn_admin = types.InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel")
        markup.add(btn_admin)

    welcome_text = (
        f"🌟 **Welcome to our trusted dollar exchange service!**\n\n"
        f"💰 Current Dollar Rate (Khuchra):\n"
        f"• Sell Rate: **{bot_data['sell_rate']} TK**\n"
        f"• Buy Rate: **{bot_data['buy_rate']} TK**\n\n"
        f"Nicer button theke apnar dorkari option ti select korun 👇"
    )
    
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

# Callback query handler for button clicks
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "sell_dollar":
        text = (
            f"💸 **Dollar Sell Korar Niyomaboli:**\n\n"
            f"• Current Khuchra Rate: **{bot_data['sell_rate']} TK**\n"
            f"• Minimum Sell: **$10**\n\n"
            f"Apni koto doller sell korte chan? Amount ti ekhane likhun (Jemon: `50` likhe send korun)."
        )
        bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="Markdown")

    elif call.data == "buy_dollar":
        text = (
            f"🛒 **Dollar Kenar Niyomaboli:**\n\n"
            f"• Current Rate: **{bot_data['buy_rate']} TK**\n"
            f"• Payment Method: bKash / Nagad\n\n"
            f"Amader official personal number:\n"
            f"📲 bKash: `{bot_data['bkash_number']}`\n\n"
            f"Taka pathiye Transaction ID (TrxID) ebong apnar wallet details ekhane send korun."
        )
        bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="Markdown")

    elif call.data == "check_rates":
        text = (
            f"📊 **Live Dollar Rate List:**\n\n"
            f"🔸 Sell Rate (Apni amader kase sell korben): **{bot_data['sell_rate']} TK**\n"
            f"🔹 Buy Rate (Apni amader kase kinben): **{bot_data['buy_rate']} TK**\n\n"
            f"💡 Boro amount er doller exchange er jonno direct support a যোগাযোগ korun."
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Back to Home", callback_data="back_home"))
        bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "support":
        text = (
            f"📞 **Customer Support & Helpline:**\n\n"
            f"Jekono proyojone amader official support a যোগাযোগ korun:\n"
            f"👤 Admin Username: @YourAdminUsername\n"
            f"⏰ Somoykal: Sokal 10ta theke rat 12ta porjonto."
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Back to Home", callback_data="back_home"))
        bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "admin_panel" and call.from_user.id == ADMIN_ID:
        admin_text = (
            f"⚙️️ **Admin Control Panel**\n\n"
            f"Current Settings:\n"
            f"• Sell Rate: {bot_data['sell_rate']} TK\n"
            f"• Buy Rate: {bot_data['buy_rate']} TK\n"
            f"• bKash Number: {bot_data['bkash_number']}\n\n"
            f"Rate ba bkash number change korar jonno command use korun:\n"
            f"👉 `/setrate [sell] [buy]`\n"
            f"👉 `/setbkash [number]`"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Back to Home", callback_data="back_home"))
        bot.edit_message_text(text=admin_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "back_home":
        send_welcome(call.message)

# Admin Command: Update Rates (Jemon: /setrate 120 123)
@bot.message_handler(commands=['setrate'])
def update_rate(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Apnar ei command use korar permission nei!")
        return
    
    try:
        parts = message.text.split()
        new_sell = float(parts[1])
        new_buy = float(parts[2])
        bot_data["sell_rate"] = new_sell
        bot_data["buy_rate"] = new_buy
        bot.reply_to(message, f"✅ Safolvabe rate update kora hoyeche!\nNotun sell rate: {new_sell} TK\nNotun buy rate: {new_buy} TK")
    except Exception as e:
        bot.reply_to(message, "⚠️ Sothik niyome likhun. Example: `/setrate 119 122`", parse_mode="Markdown")

# Admin Command: Update bKash Number (Jemon: /setbkash 017xxxxxxxx)
@bot.message_handler(commands=['setbkash'])
def update_bkash(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Apnar ei permission nei!")
        return
    
    try:
        new_number = message.text.replace("/setbkash", "").strip()
        bot_data["bkash_number"] = new_number
        bot.reply_to(message, f"✅ bKash number safolvabe update hoyeche:\n`{new_number}`", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, "⚠️ Sothik niyome likhun. Example: `/setbkash 01712345678`")

# Telegram Bot Background Thread
def run_bot():
    print("Telegram Bot is running...")
    bot.infinity_polling()

if __name__ == "__main__":
    t = Thread(target=run_bot)
    t.start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)