import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from pyngrok import ngrok
import requests

# تحميل المتغيرات
load_dotenv()

# إعداد Flask
app = Flask(__name__)

# =====================
# إعداد Gemini
# =====================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent"
)

def gemini_reply(user_message):
    payload = {
        "contents": [{
            "parts": [{"text": user_message}]
        }]
    }

    response = requests.post(
        f"{GEMINI_URL}?key={GEMINI_API_KEY}",
        json=payload,
        timeout=20
    )

    if response.status_code == 200:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]

    return "⚠️ حدث خطأ، حاول مرة أخرى."

# =====================
# استقبال واتساب
# =====================
@app.route("/whatsapp", methods=["POST"])
def whatsapp_bot():
    incoming_msg = request.values.get("Body", "")
    resp = MessagingResponse()
    msg = resp.message()

    reply = gemini_reply(incoming_msg)
    msg.body(reply)

    return str(resp)

# =====================
# تشغيل + pyngrok
# =====================
if __name__ == "__main__":
    port = 5000

    public_url = ngrok.connect(port, bind_tls=True).public_url
    print(f"🚀 Webhook URL:\n{public_url}/whatsapp")

    app.run(port=port)
