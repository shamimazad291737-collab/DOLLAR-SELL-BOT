import os
import telebot
from flask import Flask
from threading import Thread

# Ekhane apnar token ebong admin ID direct bosiye din
TOKEN = "8920302105:AAG1D4e6KHl7d_ox8y8uV6Ox9i-l3u2mAQ4  # Jemon: "123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ"
ADMIN_ID = 7388500439           # Apnar Telegram numeric user ID

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Global variables for rates and bkash number
bot_data = {
    "sell_rate": 119.00,
    "buy_rate": 125.00,
    "bkash_number": "01858582881 (Personal)"
}

# User der ID track korar jonno set (broadcast er jonno)
users = set()

@app.route('/')
def home():
    return "<h1>Dollar Sell/Buy Bot is Running Successfully! 🚀</h1>"

# /start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    users.add(message.chat.id)
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn_sell = telebot.types.InlineKeyboardButton("💸 Sell Dollar", callback_data="sell_dollar")
    btn_buy = telebot.types.InlineKeyboardButton("🛒 Buy Dollar", callback_data="buy_dollar")
    btn_rates = telebot.types.InlineKeyboardButton("📊 Today's Rate", callback_data="check_rates")
    btn_support = telebot.types.InlineKeyboardButton("📞 Customer Support", callback_data="support")
    
    markup.add(btn_sell, btn_buy, btn_rates, btn_support)
    
    if message.from_user.id == ADMIN_ID:
        btn_admin = telebot.types.InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel")
        markup.add(btn_admin)

    welcome_text = (
        f"🌟 **Welcome to our trusted dollar exchange service!**\n\n"
        f"💰 Current Dollar Rate (Khuchra):\n"
        f"• Sell Rate (Amader kase sell korben): **{bot_data['sell_rate']} TK**\n"
        f"• Buy Rate (Amader kase kinben): **{bot_data['buy_rate']} TK**\n\n"
        f"Nicer button theke apnar dorkari option ti select korun 👇"
    )
    
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

# Callback query handler for buttons
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    users.add(call.message.chat.id)
    
    if call.data == "sell_dollar":
        text = (
            f"💸 **Dollar Sell Korar Niyomaboli:**\n\n"
            f"• Current Sell Rate: **{bot_data['sell_rate']} TK**\n"
            f"• Minimum Limit: **$10**\n\n"
            f"Apni amader **Binance Pay ID / Email** a dollar send kore, apnar bKash personal number ebong koto dollar sell korte chan tar amount ekhane send korun."
        )
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("🔙 Back to Home", callback_data="back_home"))
        bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "buy_dollar":
        text = (
            f"🛒 **Dollar Kenar Niyomaboli:**\n\n"
            f"• Current Buy Rate: **{bot_data['buy_rate']} TK**\n"
            f"• Payment Method: bKash (Personal)\n\n"
            f"Amader official bKash number:\n"
            f"📲 `{bot_data['bkash_number']}`\n\n"
            f"Taka send kore apnar **Transaction ID (TrxID)** ebong apnar **Binance Pay ID** ekhane send korun."
        )
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("🔙 Back to Home", callback_data="back_home"))
        bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "check_rates":
        text = (
            f"📊 **Live Dollar Rate List:**\n\n"
            f"🔸 Sell Rate (Apni amader kase sell korben): **{bot_data['sell_rate']} TK**\n"
            f"🔹 Buy Rate (Apni amader kase kinben): **{bot_data['buy_rate']} TK**\n\n"
            f"💡 Boro amount er doller exchange er jonno direct support a যোগাযোগ korun."
        )
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("🔙 Back to Home", callback_data="back_home"))
        bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "support":
        text = (
            f"📞 **Customer Support & Helpline:**\n\n"
            f"Jekono proyojone amader official support a যোগাযোগ korun:\n"
            f"👤 Admin Username: @YourAdminUsername\n"
            f"⏰ Somoykal: Sokal 10ta theke rat 12ta porjonto."
        )
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("🔙 Back to Home", callback_data="back_home"))
        bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "admin_panel" and call.from_user.id == ADMIN_ID:
        admin_text = (
            f"⚙️ **Admin Control Panel**\n\n"
            f"Current Settings:\n"
            f"• Sell Rate: {bot_data['sell_rate']} TK\n"
            f"• Buy Rate: {bot_data['buy_rate']} TK\n"
            f"• bKash Number: {bot_data['bkash_number']}\n"
            f"• Total Bot Users: {len(users)}\n\n"
            f"Admin Commands:\n"
            f"👉 `/setrate [sell] [buy]`\n"
            f"👉 `/setbkash [number]`\n"
            f"👉 `/broadcast [message]`"
        )
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("🔙 Back to Home", callback_data="back_home"))
        bot.edit_message_text(text=admin_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "back_home":
        send_welcome(call.message)

# Admin Command: Update Rates
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

# Admin Command: Update bKash Number
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

# Admin Command: Broadcast Message to all Users
@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Apnar ei command use korar permission nei!")
        return
    
    bc_text = message.text.replace("/broadcast", "").strip()
    if not bc_text:
        bot.reply_to(message, "⚠️ Sothik niyome likhun. Example:\n`/broadcast Ei shohore notun rate cholche!`", parse_mode="Markdown")
        return
    
    success = 0
    failed = 0
    for uid in users:
        try:
            bot.send_message(uid, f"📢 **Announcement:**\n\n{bc_text}", parse_mode="Markdown")
            success += 1
        except Exception:
            failed += 1
            
    bot.reply_to(message, f"✅ Broadcast Complete!\nSuccess: {success} users\nFailed: {failed}")

# Telegram Bot Background Thread
def run_bot():
    print("Telegram Bot is running...")
    bot.infinity_polling()

if __name__ == "__main__":
    t = Thread(target=run_bot)
    t.start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
