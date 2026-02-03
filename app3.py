import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)

# =====================
# Gemini
# =====================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent"
)

SYSTEM_PROMPT = (
    "أنت مساعد ذكي محترف، مختصر، واضح، "
    "وترد باللغة العربية بشكل ودود."
)

def gemini_reply(user_message):
    payload = {
        "contents": [{
            "parts": [{
                "text": f"{SYSTEM_PROMPT}\n\nسؤال المستخدم:\n{user_message}"
            }]
        }]
    }

    response = requests.post(
        f"{GEMINI_URL}?key={GEMINI_API_KEY}",
        json=payload,
        timeout=20
    )

    if response.status_code == 200:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]

    return "⚠️ حدث خطأ مؤقت، حاول لاحقًا."

# =====================
# Webhook Twilio
# =====================
@app.route("/whatsapp", methods=["POST"])
def whatsapp_bot():
    incoming_msg = request.values.get("Body", "")
    resp = MessagingResponse()
    msg = resp.message()

    msg.body(gemini_reply(incoming_msg))
    return str(resp)

# =====================
# Health check
# =====================
@app.route("/")
def health():
    return "OK", 200
