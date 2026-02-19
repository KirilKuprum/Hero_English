from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_json = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    return gspread.authorize(creds)

try:
    client = get_gspread_client()
    sheet = client.open(os.getenv("GOOGLE_SHEET_NAME", "Applications")).sheet1
except Exception as e:
    print(f"Помилка підключення до Google Sheets: {e}")

TELEGRAM_TOKEN = "8496406059:AAHSeFLSb87-BGj4yu8M0K4Yc4QPiX-kUnM" 
CHAT_ID = "5247430396"

sent_messages = {}

@app.on_event("startup")
def set_bot_commands():
    commands = [
        {"command": "start", "description": "Start the bot"},
        {"command": "help", "description": "Show available commands"},
        {"command": "clear", "description": "Clear bot messages"}
    ]

    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setMyCommands",
        json={"commands": commands}
    )

def send_message(chat_id, text):
    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    ).json()

    if "result" in response:
        message_id = response["result"]["message_id"]

        if chat_id not in sent_messages:
            sent_messages[chat_id] = []

        sent_messages[chat_id].append(message_id)

def clear_bot_messages(chat_id):
    if chat_id not in sent_messages or not sent_messages[chat_id]:
        send_message(chat_id, "There are no messages to delete.")
        return

    for message_id in sent_messages[chat_id]:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteMessage",
            json={"chat_id": chat_id, "message_id": message_id}
        )

    sent_messages[chat_id] = []
    send_message(chat_id, "Bot messages have been cleared.")

@app.post("/telegram")
async def telegram_webhook(request: Request):
    data = await request.json()

    if "message" not in data:
        return {"ok": True}

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text == "/start":
        send_message(chat_id, "Welcome! I am the application bot.")

    elif text == "/help":
        send_message(
            chat_id,
            "Available commands:\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/clear - Clear bot messages"
        )

    elif text == "/clear":
        clear_bot_messages(chat_id)

    return {"ok": True}

@app.post("/apply")
async def apply(request: Request):
    data = await request.json()
    name = data.get("name")
    phone = data.get("phone")
    email = data.get("email")
    level = data.get("level")

    if not all([name, phone, email, level]):
        return {"message": "Please fill in all fields."}

    sheet.append_row([name, phone, email, level])

    message = (
        f"New application received:\n"
        f"Name: {name}\n"
        f"Phone: {phone}\n"
        f"Email: {email}\n"
        f"Level: {level}"
    )

    send_message(CHAT_ID, message)

    return {"message": "Thank you! Your application has been submitted successfully."}
