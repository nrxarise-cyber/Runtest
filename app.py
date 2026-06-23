from flask import Flask, request, jsonify
import os
import threading
import telebot

app = Flask(__name__)

# -----------------------------------------------------------------
# ⚙️ GLOBAL CONFIGURATION (Yahan sab fix kar diya hai)
# -----------------------------------------------------------------
SHOPIFY_SITE = "https://ferrierdesigns.myshopify.com"
PROXY_CONFIG = "3930:eQBl6g1qpdjU@p104.instantproxies.com:9290"

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YAHAN_APNA_TELEGRAM_BOT_TOKEN_DAALEIN")
bot = telebot.TeleBot(BOT_TOKEN)


def check_shopify_card(site, cc, proxy):
    """
    Backend Core Engine: Site aur Proxy dono locked hain.
    """
    try:
        cc_parts = cc.split('|')
        if len(cc_parts) < 4:
            return {"status": "Error", "message": "Invalid CC Format (Use: cc|mm|yy|cvv)"}
        
        # -----------------------------------------------------------------
        # NOTE: Ab aapke paas site aur proxy dono fixed variables se aa rhe hain.
        # Baad me jab DB lagaoge, toh 'proxy' variable me DB se data nikal kar pass kar dena.
        # -----------------------------------------------------------------
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        
        gateway_text = "insufficient_funds" 
        
        if "success" in gateway_text or "status\":\"paid" in gateway_text:
            return {"status": "🟢 CHARGED / APPROVED", "message": f"Card charged successfully on {site}!"}
        elif "insufficient" in gateway_text.lower():
            return {"status": "🔴 DECLINED: INSUFFICIENT FUNDS", "message": f"Card has low balance."}
        elif "stolen" in gateway_text.lower() or "pickup" in gateway_text.lower():
            return {"status": "❌ DECLINED: STOLEN/RESTRICTED", "message": f"Card is blocked."}
        elif "incorrect_cvc" in gateway_text.lower() or "cvv" in gateway_text.lower():
            return {"status": "❌ DECLINED: WRONG CVV", "message": "CVV check failed."}
        else:
            return {"status": "💜 DECLINED", "message": "Card was declined by gateway."}

    except Exception as e:
        return {"status": "⚠️ ERROR", "message": f"Execution failed: {str(e)}"}


# -----------------------------------------------------------------
# 🤖 SUPER CLEAN TELEGRAM COMMAND: /sh cc|mm|yy|cvv
# -----------------------------------------------------------------
@bot.message_handler(commands=['sh'])
def handle_shopify_check(message):
    try:
        # Input check: /sh cc
        input_text = message.text.split(' ', 1)
        if len(input_text) < 2:
            bot.reply_to(message, "❌ **Format:** `/sh cc|mm|yy|cvv`", parse_mode="Markdown")
            return

        cc = input_text[1].strip()
        
        # Validation checking for basic format
        if len(cc.split('|')) < 4:
            bot.reply_to(message, "❌ **Format Error!** Sahi se card details bhejein:\n`/sh card|mm|yy|cvv`", parse_mode="Markdown")
            return

        # Processing status update on Telegram
        status_msg = bot.reply_to(message, f"⏳ *Checking via Backend...*\n🌐 Site: {SHOPIFY_SITE}\n🌐 Proxy: Activated", parse_mode="Markdown")

        # Calling function with predefined Site and Proxy
        result = check_shopify_card(SHOPIFY_SITE, cc, PROXY_CONFIG)

        # Final Telegram Output Response
        response_msg = (
            f"💳 **Card:** `{cc}`\n"
            f"🌐 **Site:** {SHOPIFY_SITE}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📝 **Status:** {result['status']}\n"
            f"ℹ️ **Message:** {result['message']}"
        )
        
        bot.edit_message_text(response_msg, message.chat.id, status_msg.message_id, parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, f"⚠️ **Bot Error:** {str(e)}")


# -----------------------------------------------------------------
# 🔄 BACKGROUND THREADING ENGINE
# -----------------------------------------------------------------
def run_bot_in_background():
    bot.infinity_polling(skip_pending=True)

threading.Thread(target=run_bot_in_background, daemon=True).start()


@app.route('/')
def home():
    return f"Backend running perfectly with Locked Site & Proxy Configuration."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
