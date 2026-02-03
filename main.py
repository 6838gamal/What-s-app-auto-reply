import os
import requests
from fastapi import FastAPI, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from dotenv import load_dotenv
import uvicorn

# =========================
# Load Environment
# =========================
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Twilio Client (للإرسال)
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# FastAPI
app = FastAPI()

# =========================
# Gemini Setup
# =========================
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent"
)

SYSTEM_PROMPT = "أنت مساعد واتساب ذكي، مختصر، واضح، وترد بالعربية."

def gemini_reply(user_message: str) -> str:

    payload = {
        "contents": [{
            "parts": [{
                "text": f"{SYSTEM_PROMPT}\n\n{user_message}"
            }]
        }]
    }

    try:
        response = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            json=payload,
            timeout=20
        )

        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        print("Gemini Error:", e)

    return "⚠️ حدث خطأ مؤقت"

# =========================
# WhatsApp Webhook (استقبال)
# =========================
@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):

    form_data = await request.form()
    incoming_msg = form_data.get("Body", "")

    twilio_response = MessagingResponse()
    msg = twilio_response.message()

    reply = gemini_reply(incoming_msg)
    msg.body(reply)

    return Response(
        content=str(twilio_response),
        media_type="application/xml"
    )

# =========================
# إرسال رسالة واتساب
# =========================
@app.post("/send")
async def send_whatsapp_message(data: dict):

    to_number = data.get("to")
    message = data.get("message")

    sent = twilio_client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        to=to_number,
        body=message
    )

    return {
        "status": "sent",
        "sid": sent.sid
    }

# =========================
# Health Check
# =========================
@app.get("/")
def health():
    return {"status": "running"}

# =========================
# Main Function
# =========================
def main():
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main()
