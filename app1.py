import os
from flask import Flask, request, jsonify
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)

# إعداد Twilio
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
client = Client(ACCOUNT_SID, AUTH_TOKEN)

# إعداد Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://api.gemini.ai/v1/chat"  # مثال، تحقق من الوثائق الرسمية

def gemini_reply(user_msg):
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gemini-1.5",
        "messages": [{"role": "user", "content": user_msg}]
    }
    response = requests.post(GEMINI_URL, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "❌ حدث خطأ أثناء الاتصال بـ Gemini"

# =========================
# استقبال رسائل واتساب
# =========================
@app.route("/whatsapp", methods=["POST"])
def receive_message():
    incoming_msg = request.values.get("Body", "")
    sender = request.values.get("From")

    resp = MessagingResponse()
    msg = resp.message()

    # رد تلقائي عبر Gemini
    reply_text = gemini_reply(incoming_msg)
    msg.body(reply_text)

    return str(resp)

# =========================
# إرسال رسالة واتساب يدوياً
# =========================
@app.route("/send", methods=["POST"])
def send_message():
    data = request.get_json()
    to_number = data.get("to")
    message = data.get("message")

    sent_msg = client.messages.create(
        from_=WHATSAPP_NUMBER,
        to=to_number,
        body=message
    )

    return jsonify({
        "status": "queued",
        "sid": sent_msg.sid
    })

if __name__ == "__main__":
    app.run(debug=True)
