import telebot
import re
import os

TOKEN = "8575320394:AAGVQxlmgrD0-bhGvTkhvL5KvAjUh4dFsXw"  # Get from @BotFather
bot = telebot.TeleBot(TOKEN)

CHANNEL = "@DarkWeb_MarketStore"
SUPPORT = "@Backdoor_Operator"

MENU = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
MENU.add("🛍 Browse Products", "💳 Service Availability")
MENU.add("ℹ How to Order", "👤 Support")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
        "Welcome to DarkWeb Market! 🛍️\n\nChoose an option below:",
        reply_markup=MENU)

@bot.message_handler(func=lambda m: m.text == "🛍 Browse Products")
def browse(message):
    bot.send_message(message.chat.id, """
To order a product:

1️⃣ Go to our channel → https://t.me/DarkWeb_MarketStore
2️⃣ Choose any product  
3️⃣ Forward the product post here

I will check the product and show you payment options.
    """, reply_markup=MENU)

@bot.message_handler(func=lambda m: m.text == "💳 Service Availability")
def service(message):
    bot.send_message(message.chat.id, """
🌍 Service Availability

We currently serve customers in:

🇪🇹 Ethiopia  
🌍 Worldwide shipping available for selected electronics  

💳 Payment Methods:
✔ Bitcoin (BTC)  
✔ Zcash (ZEC)

📦 Delivery Times:
• Ethiopia: 3–7 days  
• Worldwide: 5–12 days
    """, reply_markup=MENU)

@bot.message_handler(func=lambda m: m.text == "ℹ How to Order")
def howto(message):
    bot.send_message(message.chat.id, """
🛒 How to Order

1️⃣ Open our channel → https://t.me/DarkWeb_MarketStore
2️⃣ Pick any product  
3️⃣ Forward the post to this bot  
4️⃣ Choose BTC or Zcash  
5️⃣ Make the payment  
6️⃣ Press "I Paid"  
7️⃣ Our support will verify your payment and process delivery

Simple and fast.
    """, reply_markup=MENU)

@bot.message_handler(func=lambda m: m.text == "👤 Support")
def support(message):
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("👤 Contact Support", url="https://t.me/Backdoor_Operator"))
    bot.send_message(message.chat.id, "Need help?\nTap the button below to chat with support.", reply_markup=kb)

@bot.message_handler(content_types=['text'], func=lambda m: m.forward_from and str(m.forward_from.username) == CHANNEL[1:] or m.forward_from_chat and str(m.forward_from_chat.username) == CHANNEL[1:])
def forwarded_product(message):
    caption = message.caption or ""
    
    # Check if SOLD (case-insensitive)
    if any(x in caption.upper() for x in ["SOLD", "OUT OF STOCK"]):
        bot.reply_to(message, "❌ This item is SOLD.\nPlease choose another product.")
        return
    
    # Extract price (supports $10 or 10 USD)
    price_match = re.search(r'\$([\d,.]+)|(\d+)[\s,]*(USD|\$)?', caption, re.IGNORECASE)
    price = price_match.group(1).replace(',', '') or price_match.group(2) if price_match else None
    
    # Extract product name (first non-empty line)
    lines = [line.strip() for line in caption.split('\n') if line.strip()]
    product_name = lines[0] if lines else "Unknown product"
    
    if not price:
        bot.reply_to(message, "⚠ Could not detect price. Please contact support.")
        return
    
    kb = telebot.types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        telebot.types.InlineKeyboardButton("Pay with BTC", callback_data=f"btc_{price}_{product_name[:30]}"),  # Shorten name for data
        telebot.types.InlineKeyboardButton("Pay with Zcash", callback_data=f"zcash_{price}_{product_name[:30]}")
    )
    
    bot.send_message(message.chat.id,
        f"🔥 Product: {product_name}\n💵 Price: ${price}\n\nChoose a payment method:",
        reply_markup=kb)

@bot.callback_query_handler(func=lambda call: True)
def payment_callback(call):
    data = call.data.split("_", 2)
    method = "BTC" if data[0] == "btc" else "Zcash"
    price = data[1]
    name = data[2]  # Already shortened
    
    url = f"https://t.me/Backdoor_Operator?text=I%20completed%20payment%20for%20{name}%20${price}%20({method})"
    
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("✔ I Paid", url=url))
    
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Payment Method: {method}\nTotal: ${price}\n\nSend EXACTLY the amount shown in USD.\n\nAfter payment, click “I Paid”.",
        reply_markup=kb
    )

# Keep polling forever
if __name__ == "__main__":
    bot.infinity_polling()
