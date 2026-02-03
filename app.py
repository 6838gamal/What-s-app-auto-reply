import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Twilio credentials
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# =========================
# استقبال الرسائل
# =========================
@app.route("/whatsapp", methods=["POST"])
def receive_message():
    incoming_msg = request.values.get("Body", "").lower()
    sender = request.values.get("From")

    resp = MessagingResponse()
    msg = resp.message()

    if "مرحبا" in incoming_msg or "اهلا" in incoming_msg:
        msg.body("👋 أهلاً بك! اكتب:\n1️⃣ الخدمات\n2️⃣ الأسعار\n3️⃣ الدعم")
    elif "1" in incoming_msg:
        msg.body("🛠 خدماتنا:\n- أتمتة\n- بوتات واتساب\n- سحب بيانات")
    elif "2" in incoming_msg:
        msg.body("💰 الأسعار تبدأ من 50$")
    elif "3" in incoming_msg:
        msg.body("📞 سيتم تحويلك للدعم البشري")
    else:
        msg.body("❓ لم أفهم طلبك، اكتب *مرحبا* لبدء القائمة")

    return str(resp)

# =========================
# إرسال رسالة يدوياً
# =========================
@app.route("/send", methods=["POST"])
def send_message():
    to_number = request.json.get("to")   # whatsapp:+967xxxxxxxx
    message = request.json.get("message")

    sent = client.messages.create(
        from_=WHATSAPP_NUMBER,
        to=to_number,
        body=message
    )

    return {
        "status": "sent",
        "sid": sent.sid
    }

if __name__ == "__main__":
    app.run(debug=True)
