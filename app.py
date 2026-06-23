from flask import Flask, request, jsonify
import os
import requests  # Future use ke liye jab aap real API hit karenge

app = Flask(__name__)

def check_shopify_card(site, cc, proxy):
    """
    Card data split karta hai aur response check karta hai.
    """
    try:
        # 1. CC Data ko split karna (Format: 4487160040340792|06|26|452)
        cc_parts = cc.split('|')
        if len(cc_parts) < 4:
            return {"status": "Error", "message": "Invalid CC Format (Use: cc|mm|yy|cvv)"}
        
        card_num, exp_month, exp_year, cvv = cc_parts[0], cc_parts[1], cc_parts[2], cc_parts[3]

        # 2. Proxy Setup
        proxies = None
        if proxy:
            proxies = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }

        # --- GATEWAY RESPONSE LOGIC ---
        # Abhi ke liye hum gateway_text ko dynamic test karne ke liye 'insufficient_funds' maan rahe hain.
        # Jab aap real request bhejenge, toh ye line badal jayegi: gateway_text = response.text
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
# NEW: API ROUTE (Jo aapke code mein missing thi)
# -----------------------------------------------------------------
@app.route('/check', methods=['GET', 'POST'])
def check_card_api():
    # GET aur POST dono requests se data uthane ke liye
    if request.method == 'POST':
        # Agar JSON data bheja gaya ho
        data = request.get_json() or request.form
    else:
        # Agar URL query parameters hain (?cc=...&site=...)
        data = request.args

    site = data.get('site', '')
    cc = data.get('cc', '')
    proxy = data.get('proxy', '')

    if not cc:
        return jsonify({"status": "Error", "message": "CC parameter is required!"}), 400

    # Function ko call karke result lena
    result = check_shopify_card(site, cc, proxy)
    
    # JSON response return karna
    return jsonify(result)

# -----------------------------------------------------------------
# NEW: SERVER START LOGIC (Jo aapke code mein missing tha)
# -----------------------------------------------------------------
if __name__ == '__main__':
    # Railway automatically 'PORT' env variable provide karta hai
    port = int(os.environ.get("PORT", 5000))
    # host='0.0.0.0' hona zaroori hai taaki outside world se request aa sake
    app.run(host='0.0.0.0', port=port)
