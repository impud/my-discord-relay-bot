from flask import Flask
from threading import Thread
import discord
import requests
import os

# === НАСТРОЙКИ ===
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
ALLOWED_THREAD_ID = os.environ["ALLOWED_THREAD_ID"]

# === НАСТРОЙКА DISCORD ===
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# === TELEGRAM ===
def send_text_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }
    response = requests.post(url, data=payload)
    if not response.ok:
        print("❌ Ошибка при отправке текста:", response.text)

def send_file_to_telegram(file_url, filename):
    try:
        file_content = requests.get(file_url).content
        files = {"document": (filename, file_content)}
        data = {"chat_id": TELEGRAM_CHAT_ID}
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
        r = requests.post(url, data=data, files=files)
        if not r.ok:
            print("❌ Ошибка при отправке файла:", r.text)
    except Exception as e:
        print("❌ Ошибка при загрузке файла:", e)

def send_photo_to_telegram(file_url, caption=""):
    try:
        file_content = requests.get(file_url).content
        files = {"photo": ("image.jpg", file_content)}
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "caption": caption
        }
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        r = requests.post(url, data=data, files=files)
        if not r.ok:
            print("❌ Ошибка при отправке фото:", r.text)
    except Exception as e:
        print("❌ Ошибка при загрузке фото:", e)

# === ОБРАБОТКА СООБЩЕНИЙ ===
@client.event
async def on_ready():
    print(f"✅ Бот запущен как {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if str(message.channel.id) != ALLOWED_THREAD_ID:
        return

    author = message.author.display_name
    content = message.content.strip()

    print(f"📥 Получено сообщение: {content} от {author}")

    if content:
        send_text_to_telegram(f"{author}: {content}")

    for attachment in message.attachments:
        file_url = attachment.url
        filename = attachment.filename.lower()

        if filename.endswith((".png", ".jpg", ".jpeg", ".gif")):
            send_photo_to_telegram(file_url, caption=f"{author} отправил(а) изображение")
        else:
            send_text_to_telegram(f"{author} отправил(а) файл: {filename}")
            send_file_to_telegram(file_url, filename)

# === UPTIME ===
app = Flask('')

@app.route('/')
def home():
    return "Бот работает!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run_web).start()

# === ЗАПУСК ===
client.run(DISCORD_TOKEN)



