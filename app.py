from flask import Flask, request, jsonify
import os
import threading
import telebot  # PyTelegramBotAPI library

app = Flask(__name__)

# -----------------------------------------------------------------
# TELEGRAM BOT SETUP (Auto-Start)
# -----------------------------------------------------------------
# BotFather ka token yahan paste karein ya Railway Variables me BOT_TOKEN set karein
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YAHAN_APNA_TELEGRAM_BOT_TOKEN_DAALEIN")
bot = telebot.TeleBot(BOT_TOKEN)

def check_shopify_card(site, cc, proxy):
    """
    Backend logical framework for card verification.
    """
    try:
        cc_parts = cc.split('|')
        if len(cc_parts) < 4:
            return {"status": "Error", "message": "Invalid CC Format (Use: cc|mm|yy|cvv)"}
        
        card_num, exp_month, exp_year, cvv = cc_parts[0], cc_parts[1], cc_parts[2], cc_parts[3]

        # --- DUMMY GATEWAY TEXT ---
        # Real integration ke waqt aap yahan requests ka response text pass karenge.
        gateway_text = "insufficient_funds" 
        
        if "success" in gateway_text or "status\":\"paid" in gateway_text:
            return {"status": "🟢 CHARGED / APPROVED", "message": "Card successfully charged!"}
        elif "insufficient" in gateway_text.lower():
            return {"status": "🔴 DECLINED: INSUFFICIENT FUNDS", "message": "Card has low balance."}
        elif "stolen" in gateway_text.lower() or "pickup" in gateway_text.lower():
            return {"status": "❌ DECLINED: STOLEN/RESTRICTED", "message": "Card is blocked."}
        elif "incorrect_cvc" in gateway_text.lower() or "cvv" in gateway_text.lower():
            return {"status": "❌ DECLINED: WRONG CVV", "message": "CVV check failed."}
        else:
            return {"status": "💜 DECLINED", "message": "Card was declined by gateway."}

    except Exception as e:
        return {"status": "⚠️ ERROR", "message": f"Execution failed: {str(e)}"}


# -----------------------------------------------------------------
# SINGLE TELEGRAM COMMAND: /sh
# -----------------------------------------------------------------
@bot.message_handler(commands=['sh'])
def handle_shopify_check(message):
    try:
        # Command input check: /sh site|cc|proxy
        input_text = message.text.split(' ', 1)
        if len(input_text) < 2:
            bot.reply_to(message, "❌ **Format:** `/sh site|cc|proxy`", parse_mode="Markdown")
            return

        # Splitting input parameters
        parts = input_text[1].split('|')
        if len(parts) < 6:
            bot.reply_to(message, "❌ **Missing Data!** Format sahi se check karein.\n`site | card | mm | yy | cvv | proxy`")
            return

        site = parts[0].strip()
        cc = f"{parts[1].strip()}|{parts[2].strip()}|{parts[3].strip()}|{parts[4].strip()}"
        proxy = parts[5].strip()

        # Processing Notification
        status_msg = bot.reply_to(message, "⏳ *Checking Card via Backend...*", parse_mode="Markdown")

        # Calling the backend core logic
        result = check_shopify_card(site, cc, proxy)

        # Final response output on Telegram
        response_msg = (
            f"💳 **Card:** `{cc}`\n"
            f"🌐 **Site:** {site}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📝 **Status:** {result['status']}\n"
            f"ℹ️ **Message:** {result['message']}"
        )
        
        bot.edit_message_text(response_msg, message.chat.id, status_msg.message_id, parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, f"⚠️ **Backend Error:** {str(e)}")


# -----------------------------------------------------------------
# BACKEND AUTO-START FUNCTION
# -----------------------------------------------------------------
def run_bot_in_background():
    # Bot bina kisi API hit ke backend me auto-start ho jayega
    bot.infinity_polling(skip_pending=True)

# Start background thread before Flask initializes
threading.Thread(target=run_bot_in_background, daemon=True).start()


@app.route('/')
def home():
    return "Backend Engine is Online & Running Telegram Bot."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
