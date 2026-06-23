from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/shopify', methods=['GET'])
def shopify_handler():
    # URL से पैरामीटर्स निकालना
    site = request.args.get('site')
    cc = request.args.get('cc', '')
    proxy = request.args.get('proxy', '')

    if not site:
        return jsonify({"error": "Missing 'site' parameter"}), 400

    # यहाँ आप अपना सुरक्षित लॉजिक लिख सकते हैं
    # उदाहरण के लिए, सिर्फ डेटा को कंसोल में प्रिंट करना:
    print(f"Processing site: {site} with proxy: {proxy}")

    # रिस्पॉन्स भेजना
    return jsonify({
        "status": "success",
        "received_site": site,
        "received_cc": cc,
        "received_proxy": proxy
    })

if __name__ == '__main__':
    # Railway environment पोर्ट का उपयोग करता है
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
