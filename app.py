from flask import Flask, request, jsonify
import os
import threading
import telebot

app = Flask(__name__)

# -----------------------------------------------------------------
# ⚙️ GLOBAL CONFIGURATION
# -----------------------------------------------------------------
# Aapki locked site aur proxy configuration
SHOPIFY_SITE = "https://ferrierdesigns.myshopify.com"
PROXY_CONFIG = "3930:eQBl6g1qpdjU@p104.instantproxies.com:9290"

# Secure Token Loading from Railway Environment Variables
BOT_TOKEN = "7627130297:AAF8oEnwCxV0a3doIKcFDhiazsvGP9p1Z74" os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    # Agar variable nahi milega toh log mein saaf dikhega
    print("❌ CRITICAL ERROR: 'BOT_TOKEN' environment variable is missing in Railway!")
    bot = None
else:
    try:
        bot = telebot.TeleBot(BOT_TOKEN)
    except Exception as e:
        print(f"❌ Error initializing bot: {str(e)}")
        bot = None


# -----------------------------------------------------------------
# ⚙️ CORE BACKEND CHECKER LOGIC
# -----------------------------------------------------------------
def check_shopify_card(site, cc, proxy):
    """
    Backend Core Engine: Card verification logic runs here.
    """
    try:
        cc_parts = cc.split('|')
        if len(cc_parts) < 4:
            return {"status": "Error", "message": "Invalid CC Format (Use: cc|mm|yy|cvv)"}
        
        # Fixed logic for proxies string configuration
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        
        # Test baseline string (Replace with real automation response later)
        gateway_text = "insufficient_funds" 
        
        if "success" in gateway_text or "status\":\"paid" in gateway_text:
            return {"status": "🟢 CHARGED / APPROVED", "message": f"Card charged successfully on {site}!"}
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
# 🤖 TELEGRAM HANDLER (Sirf tab chalega jab token valid ho)
# -----------------------------------------------------------------
if bot:
    @bot.message_handler(commands=['sh'])
    def handle_shopify_check(message):
        try:
            # Extract arguments following /sh command
            input_text = message.text.split(' ', 1)
            if len(input_text) < 2:
                bot.reply_to(message, "❌ **Format:** `/sh cc|mm|yy|cvv`", parse_mode="Markdown")
                return

            cc = input_text[1].strip()
            
            # Format validation
            if len(cc.split('|')) < 4:
                bot.reply_to(message, "❌ **Format Error!** Use: `/sh card|mm|yy|cvv`", parse_mode="Markdown")
                return

            # Telegram live status update
            status_msg = bot.reply_to(message, f"⏳ *Checking via Backend...*\n🌐 Site: {SHOPIFY_SITE}", parse_mode="Markdown")

            # Execute checker core function
            result = check_shopify_card(SHOPIFY_SITE, cc, PROXY_CONFIG)

            # Final response delivery on chat
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
# 🔄 AUTOMATIC START BACKGROUND THREAD (Gunicorn Compatible)
# -----------------------------------------------------------------
def run_bot_in_background():
    if bot:
        try:
            print("🤖 Telegram Bot Polling Triggered Successfully...")
            bot.infinity_polling(skip_pending=True)
        except Exception as e:
            print(f"❌ Critical Bot Error in Background Thread: {str(e)}")

# Yeh line if__main__ ke bahar hai taaki Railway server start hote hi automatic chalu ho jaye
if bot:
    threading.Thread(target=run_bot_in_background, daemon=True).start()


# -----------------------------------------------------------------
# 🌐 WEB DASHBOARD ENDPOINT
# -----------------------------------------------------------------
@app.route('/')
def home():
    if bot:
        return f"Backend engine operational. Locked Site: {SHOPIFY_SITE} | Bot Status: ACTIVE"
    return f"Backend running, but BOT IS INACTIVE due to missing BOT_TOKEN variable."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
