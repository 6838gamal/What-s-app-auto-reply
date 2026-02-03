import os
import requests
from fastapi import FastAPI, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from dotenv import load_dotenv

# ===== تحميل متغيرات البيئة =====
load_dotenv()

app = FastAPI()

# ===== مفاتيح Twilio =====
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

twilio_client = Client(
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN
)

# ===== Gemini =====
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent"
)

SYSTEM_PROMPT = """
أنت موظف خدمة عملاء محترف.
ترد بطريقة ودودة، مختصرة، واضحة.
إذا كان السؤال غير واضح اطلب التوضيح.
"""


# ===== دالة الذكاء الاصطناعي =====
def ai_reply(user_message):
    try:
        payload = {
            "contents": [{
                "parts": [{
                    "text": SYSTEM_PROMPT + "\n" + user_message
                }]
            }]
        }

        response = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]

        return "حدث خطأ مؤقت."

    except Exception:
        return "تعذر معالجة الطلب حالياً."


# ===== إرسال رسالة مباشرة (اختياري مستقبلاً) =====
def send_whatsapp_message(to_number, message):
    twilio_client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        body=message,
        to=to_number
    )


# ===== Webhook الرد التلقائي =====
@app.api_route("/whatsapp", methods=["GET", "POST"])
async def whatsapp_auto_reply(request: Request):
    form_data = await request.form()
    incoming_msg = form_data.get("Body", "")

    if not incoming_msg:
        reply_text = "كيف أقدر أساعدك؟"
    else:
        reply_text = ai_reply(incoming_msg)

    twilio_response = MessagingResponse()
    twilio_response.message(reply_text)

    return Response(
        content=str(twilio_response),
        media_type="application/xml"
    )


# ===== Status Callback URL =====
@app.api_route("/status", methods=["GET", "POST"])
async def message_status(request: Request):

    if request.method == "POST":
        data = await request.form()
    else:
        data = dict(request.query_params)

    message_sid = data.get("MessageSid")
    message_status = data.get("MessageStatus")
    to_number = data.get("To")
    from_number = data.get("From")

    # يمكنك لاحقاً حفظ الحالة في قاعدة بيانات أو عمل Logging
    print(f"Message {message_sid} | To: {to_number} | From: {from_number} | Status: {message_status}")

    return {"status": "received"}


# ===== Route اختبار =====
@app.get("/")
def home():
    return {"status": "WhatsApp Bot Running 🚀"}


# ===== دالة التشغيل MAIN =====
def main():
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )


# ===== تشغيل مباشر =====
if __name__ == "__main__":
    main()
