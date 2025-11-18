import os
import re
import telebot
from telebot import types
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(os.getenv("8575320394:AAGVQxlmgrD0-bhGvTkhvL5KvAjUh4dFsXw"), parse_mode="HTML")
admin_id = 7213658944  # ← change to your Telegram ID if you want admin commands

# === Main Menu ===
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Browse Products", callback_data="categories"),
        types.InlineKeyboardButton("How to Order", callback_data="howto"),
        types.InlineKeyboardButton("Support", url="t.me/Backdoor_Operator"),
        types.InlineKeyboardButton("Channel", url="t.me/DarkWeb_MarketStore")
    )
    return markup

# === Categories Menu ===
def categories_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Drugs", callback_data="cat_drugs"),
        types.InlineKeyboardButton("Cards & Docs", callback_data="cat_cards"),
        types.InlineKeyboardButton("Hacking", callback_data="cat_hacking"),
        types.InlineKeyboardButton("Counterfeit", callback_data="cat_counterfeit"),
        types.InlineKeyboardButton("Back", callback_data="back_main")
    )
    return markup

# === Fake product list (you can expand) ===
products = {
    "cat_drugs": ["Cocaine 1g – $90", "MDMA 1g – $70", "Weed 10g – $110"],
    "cat_cards": ["USA CC Fullz – $35", "EU Bank Login – $180", "PayPal Verified – $120"],
    "cat_hacking": ["Ransomware Source – $450", "Keylogger 2025 – $80", "Zero-Day Exploit – $1200"],
    "cat_counterfeit": ["USD 10k Bundle – $800", "Fake ID + License – $300"]
}

# === Start & Forward Handler ===
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "<b>DARKWEB MARKET</b>\n"
                     "World-wide underground prices | Fast delivery\n"
                     "We only accept Bitcoin • Monero • Zcash",
                     reply_markup=main_menu())

@bot.message_handler(content_types=['text', 'photo', 'document'])
def handle_forward(message):
    if message.forward_from or message.forward_from_chat:
        text = message.caption or message.text or ""
        price_match = re.search(r'(\d+[\d,]*)\s*[\$€£]', text, re.I)
        if price_match:
            price = price_match.group(1).replace(",", "")
            product_name = text.split("\n")[0][:50]
            pay_buttons(message.chat.id, product_name, price)

def pay_buttons(chat_id, name, price):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(f"Pay ${price} (BTC)", callback_data=f"paid_{price}"),
        types.InlineKeyboardButton(f"Pay ${price} (XMR/ZEC)", callback_data=f"paid_{price}")
    )
    markup.add(types.InlineKeyboardButton("I Already Paid", url="t.me/Backdoor_Operator"))
    bot.send_message(chat_id,
                     f"<b>PRODUCT:</b> {name}\n"
                     f"<b>PRICE:</b> ${price}\n\n"
                     "Choose payment method below:",
                     reply_markup=markup)

# === Callback Handler ===
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "categories":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=categories_menu())
    elif call.data.startswith("cat_"):
        cat = call.data.split("_")[1]
        items = products.get(call.data, ["No products yet"])
        text = "<b>Category:</b> " + cat.upper() + "\n\n"
        for item in items:
            text += "• " + item + "\n"
        text += "\nForward any post from @DarkWeb_MarketStore to order."
        bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=back_button())
    elif call.data == "howto":
        bot.edit_message_text("<b>How to Order</b>\n\n"
                              "1. Forward any product post from @DarkWeb_MarketStore\n"
                              "2. Choose payment method\n"
                              "3. Send proof to @Backdoor_Operator\n"
                              "4. Receive delivery instantly",
                              call.message.chat.id, call.message.id, reply_markup=back_button())
    elif call.data == "back_main":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=main_menu())
    elif call.data.startswith("paid_"):
        bot.answer_callback_query(call.id, "Contact @Backdoor_Operator with proof")

def back_button():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Back", callback_data="categories"))
    return markup

# === Start Polling ===
if __name__ == "__main__":
    print("DarkWeb Bot Started – No Emoji Edition")
    bot.infinity_polling()
